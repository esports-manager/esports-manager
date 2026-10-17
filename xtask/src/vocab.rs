// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! Genre vocabulary check: the core crate speaks no esport's language
//! (ADR 0002).

use std::path::Path;

use anyhow::Result;

use crate::config::Vocabulary;
use crate::files;

pub fn run(root: &Path, config: &Vocabulary) -> Result<Vec<String>> {
    let crate_dir = root.join("crates").join(&config.crate_name);
    let mut violations = Vec::new();
    for file in files::walk(&crate_dir, &["rs", "toml", "md"])? {
        let text = files::read(&file)?;
        for (line, word) in find_denied(&text, &config.denied) {
            violations.push(format!(
                "{}:{line}: `{word}` is genre vocabulary and must not appear in `{}` (ADR 0002)",
                files::display(root, &file),
                config.crate_name,
            ));
        }
    }
    Ok(violations)
}

/// Every `(line number, word)` in `text` whose word is in `denied`.
/// Identifiers are split at `_` and at camel-case humps, so `champion_id`
/// and `ChampionId` both contain `champion`.
pub fn find_denied(text: &str, denied: &[String]) -> Vec<(usize, String)> {
    let mut found = Vec::new();
    for (index, line) in text.lines().enumerate() {
        for word in words(line) {
            if denied.contains(&word) {
                found.push((index + 1, word));
            }
        }
    }
    found
}

fn words(line: &str) -> Vec<String> {
    let mut words = Vec::new();
    let mut current = String::new();
    let mut previous_was_lower = false;
    for character in line.chars() {
        if !character.is_alphanumeric() {
            push_word(&mut words, &mut current);
            previous_was_lower = false;
            continue;
        }
        if character.is_uppercase() && previous_was_lower {
            push_word(&mut words, &mut current);
        }
        previous_was_lower = character.is_lowercase() || character.is_numeric();
        current.extend(character.to_lowercase());
    }
    push_word(&mut words, &mut current);
    words
}

fn push_word(words: &mut Vec<String>, current: &mut String) {
    if !current.is_empty() {
        words.push(std::mem::take(current));
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn denied() -> Vec<String> {
        vec!["champion".to_owned(), "lane".to_owned()]
    }

    #[test]
    fn splits_snake_case_and_camel_case() {
        assert_eq!(
            words("let ChampionId = champion_id2;"),
            ["let", "champion", "id", "champion", "id2"]
        );
    }

    #[test]
    fn reports_line_numbers_of_denied_words() {
        let text = "fn ok() {}\nstruct LanePlan;\n// a champion\n";
        assert_eq!(
            find_denied(text, &denied()),
            [(2, "lane".to_owned()), (3, "champion".to_owned())]
        );
    }

    #[test]
    fn longer_words_containing_a_denied_word_pass() {
        assert_eq!(find_denied("let planes = championship;", &denied()), []);
    }

    #[test]
    fn the_core_crate_passes() {
        let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("..");
        let quality = crate::config::Quality::load(&root.join("quality.toml")).unwrap();
        assert_eq!(
            run(&root, &quality.vocabulary).unwrap(),
            Vec::<String>::new()
        );
    }
}
