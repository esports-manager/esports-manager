// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! No rest patterns in package conversion modules (ADR 0005).
//!
//! The conversion from package types to domain types destructures every
//! definition exhaustively, so a field can't be validated and then ignored.
//! A rest pattern (`let TeamDef { id, .. } = def;`) would silently let a new
//! field through, so it is banned in the files `quality.toml` lists.

use std::path::Path;

use anyhow::Result;

use crate::files;

pub fn run(root: &Path, conversion_files: &[String]) -> Result<Vec<String>> {
    let mut violations = Vec::new();
    for file in conversion_files {
        let text = files::read(&root.join(file))?;
        for line in find_rest_patterns(&text) {
            violations.push(format!(
                "{file}:{line}: rest pattern `..` in a package conversion module; bind every field (ADR 0005)"
            ));
        }
    }
    Ok(violations)
}

/// Line numbers of rest patterns, and of fields ignored with `field: _`.
///
/// A `..` is a rest pattern when, ignoring whitespace and line breaks, it
/// comes after `{`, `(`, `[` or `,` and before `}`, `)`, `]` or `,`. Ranges
/// (`1..`, `a..b`, `..=`), slices (`&s[1..]`, `&s[..]`) and struct update syntax
/// (`..Default::default()`) don't match. Binding a field as `_` skips it as
/// silently as `..` does, so it is flagged too; only `schema: _` is allowed,
/// because `$schema` is editor metadata, not content. Comments and string
/// literals are ignored. A full range passed as an argument, `f(..)`, reads
/// like the tuple pattern `Some(..)` and is flagged; write `RangeFull` there.
pub fn find_rest_patterns(text: &str) -> Vec<usize> {
    let code: Vec<String> = text.lines().map(code_only).collect();
    let joined = code.join("\n");
    let line_of = |offset: usize| joined[..offset].matches('\n').count() + 1;
    let mut found = Vec::new();
    for (index, _) in joined.match_indices("..") {
        let head = joined[..index].trim_end();
        let before = head.chars().next_back();
        let after = joined[index + 2..].trim_start().chars().next();
        // `s[..]` indexes: its `[` follows a name, `)` or `]`. A slice
        // pattern's `[` never does.
        let indexes = before == Some('[')
            && head[..head.len() - 1]
                .chars()
                .next_back()
                .is_some_and(|c| c.is_alphanumeric() || matches!(c, '_' | ')' | ']'));
        let opens = matches!(before, Some('{' | '(' | '[' | ',')) && !indexes;
        let closes = matches!(after, Some('}' | ')' | ']' | ','));
        if opens && closes {
            found.push(line_of(index));
        }
    }
    for (index, _) in joined.match_indices(": _") {
        let start = joined[..index]
            .rfind(|c: char| !(c.is_alphanumeric() || c == '_'))
            .map_or(0, |position| position + 1);
        let field = &joined[start..index];
        let after = joined[index + 3..].chars().next();
        let ignores = matches!(after, Some(',' | '}' | ')' | ' ' | '\n') | None);
        if ignores && !field.is_empty() && field != "schema" {
            found.push(line_of(index));
        }
    }
    found.sort_unstable();
    found.dedup();
    found
}

/// The line without its `//` comment and with string literals emptied.
fn code_only(line: &str) -> String {
    let mut code = String::new();
    let mut in_string = false;
    let mut escaped = false;
    let mut chars = line.chars().peekable();
    while let Some(c) = chars.next() {
        if in_string {
            if escaped {
                escaped = false;
            } else if c == '\\' {
                escaped = true;
            } else if c == '"' {
                in_string = false;
                code.push('"');
            }
            continue;
        }
        match c {
            '"' => {
                in_string = true;
                code.push('"');
            }
            '/' if chars.peek() == Some(&'/') => break,
            _ => code.push(c),
        }
    }
    code
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn finds_struct_tuple_and_slice_rest_patterns() {
        let text = "let TeamDef { id, .. } = def;\nlet Pair(a, ..) = pair;\nlet [first, ..] = list;\nlet (a, .., z) = t;\n";
        assert_eq!(find_rest_patterns(text), [1, 2, 3, 4]);
    }

    #[test]
    fn finds_a_rest_pattern_on_its_own_line() {
        let text = "let TeamDef {\n    id,\n    ..\n} = def;\n";
        assert_eq!(find_rest_patterns(text), [3]);
        let text = "let TeamDef {\n    id, ..\n} = def;\n";
        assert_eq!(find_rest_patterns(text), [2]);
    }

    #[test]
    fn slices_and_range_from_are_not_rest_patterns() {
        let text = "let a = &s[1..];\nlet b = &s[..2];\nlet c = f(1..);\nlet d = g(x, 1..);\nlet e = &s[..];\nlet f = &v()[..];\n";
        assert_eq!(find_rest_patterns(text), Vec::<usize>::new());
        // Slice and tuple patterns still count.
        assert_eq!(
            find_rest_patterns("let [a, ..] = s;\nlet [..] = t;\nif let Some(..) = x {}\n"),
            [1, 2, 3]
        );
    }

    #[test]
    fn ignored_fields_are_flagged_except_the_schema() {
        let text =
            "let TeamDef {\n    schema: _,\n    tag: _,\n    id,\n} = def;\nlet B { x: _ } = b;\n";
        assert_eq!(find_rest_patterns(text), [3, 6]);
    }

    #[test]
    fn ranges_and_struct_updates_are_not_rest_patterns() {
        let text = "for i in 0..2 {}\nlet r = 1..=3;\nlet s = &x[2..4];\nlet t = Foo { a, ..Foo::default() };\n";
        assert_eq!(find_rest_patterns(text), Vec::<usize>::new());
    }

    #[test]
    fn comments_and_strings_are_ignored() {
        let text = "// let A { .. } = a;\nlet s = \"{ .. }\"; // ..}\nlet t = \"a\\\" .. }\";\n";
        assert_eq!(find_rest_patterns(text), Vec::<usize>::new());
    }

    #[test]
    fn the_repository_conversion_module_is_clean() {
        let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("..");
        let violations = run(&root, &["crates/packages/src/convert.rs".to_owned()]).unwrap();
        assert_eq!(violations, Vec::<String>::new());
    }
}
