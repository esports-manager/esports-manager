// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! Spec-to-test traceability (ADR 0009).
//!
//! Scenario ids come from `### ID — title` headings in `docs/specs/*.md`.
//! Tests reference them with a `spec: ID` marker in a comment.

use std::collections::{BTreeMap, BTreeSet};
use std::path::Path;

use anyhow::Result;

use crate::files;

/// Files in `docs/specs/` that describe the format instead of a feature.
const NOT_SPECS: [&str; 2] = ["README.md", "TEMPLATE.md"];
/// Where tests live, relative to the repository root.
const SOURCE_DIRS: [&str; 5] = ["crates", "src", "src-tauri", "e2e", "smoke"];
const SOURCE_EXTENSIONS: [&str; 3] = ["rs", "ts", "tsx"];
const MARKER: &str = "spec:";

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Status {
    Draft,
    Accepted,
    Implemented,
}

#[derive(Debug, PartialEq, Eq)]
pub struct Scenario {
    pub id: String,
    pub withdrawn: bool,
}

#[derive(Debug, PartialEq, Eq)]
pub struct Spec {
    pub name: String,
    pub status: Option<Status>,
    pub scenarios: Vec<Scenario>,
}

pub fn run(root: &Path) -> Result<Vec<String>> {
    let mut specs = Vec::new();
    for path in files::walk(&root.join("docs/specs"), &["md"])? {
        let name = files::display(root, &path);
        if NOT_SPECS.iter().any(|skip| path.ends_with(skip)) {
            continue;
        }
        specs.push(parse_spec(name, &files::read(&path)?));
    }

    let mut references = BTreeMap::new();
    for dir in SOURCE_DIRS {
        for path in files::walk(&root.join(dir), &SOURCE_EXTENSIONS)? {
            let location = files::display(root, &path);
            for id in find_references(&files::read(&path)?) {
                references
                    .entry(id)
                    .or_insert_with(BTreeSet::new)
                    .insert(location.clone());
            }
        }
    }

    Ok(check(&specs, &references))
}

/// Reads a spec's status and scenario headings, ignoring fenced code blocks.
pub fn parse_spec(name: String, text: &str) -> Spec {
    let mut status = None;
    let mut scenarios = Vec::new();
    let mut in_code = false;
    for line in text.lines() {
        let trimmed = line.trim();
        if trimmed.starts_with("```") {
            in_code = !in_code;
            continue;
        }
        if in_code {
            continue;
        }
        if let Some(value) = trimmed.strip_prefix("- **Status:**") {
            status = parse_status(value.trim());
        } else if let Some(heading) = trimmed.strip_prefix("### ")
            && let Some(id) = leading_id(heading)
        {
            scenarios.push(Scenario {
                id: id.to_owned(),
                withdrawn: heading.contains("(Withdrawn)"),
            });
        }
    }
    Spec {
        name,
        status,
        scenarios,
    }
}

fn parse_status(value: &str) -> Option<Status> {
    match value {
        "Draft" => Some(Status::Draft),
        "Accepted" => Some(Status::Accepted),
        "Implemented" => Some(Status::Implemented),
        _ => None,
    }
}

/// The scenario id at the start of `text`: uppercase letters, `-`, three
/// digits, then the end of the text or a non-alphanumeric character.
fn leading_id(text: &str) -> Option<&str> {
    let prefix_len = text.chars().take_while(char::is_ascii_uppercase).count();
    let rest = text.get(prefix_len..)?;
    let digits = rest.strip_prefix('-')?;
    let digit_count = digits.chars().take_while(char::is_ascii_digit).count();
    let terminated = digits
        .chars()
        .nth(3)
        .is_none_or(|next| !next.is_ascii_alphanumeric());
    if prefix_len == 0 || digit_count != 3 || !terminated {
        return None;
    }
    text.get(..prefix_len + 4)
}

/// Every scenario id referenced by a `spec:` marker. A marker may list
/// several ids separated by commas.
pub fn find_references(text: &str) -> Vec<String> {
    let mut ids = Vec::new();
    for (index, _) in text.match_indices(MARKER) {
        let after = &text[index + MARKER.len()..];
        let line = after.lines().next().unwrap_or("");
        for candidate in line.split(',') {
            if let Some(id) = leading_id(candidate.trim()) {
                ids.push(id.to_owned());
            }
        }
    }
    ids
}

/// Compares the scenarios declared in specs with the ids tests reference.
pub fn check(specs: &[Spec], references: &BTreeMap<String, BTreeSet<String>>) -> Vec<String> {
    let mut violations = Vec::new();
    let mut declared: BTreeMap<&str, (&Spec, &Scenario)> = BTreeMap::new();

    for spec in specs {
        let Some(status) = spec.status else {
            violations.push(format!(
                "{}: missing or unknown `- **Status:**` line (Draft, Accepted or Implemented)",
                spec.name
            ));
            continue;
        };
        let traced = matches!(status, Status::Accepted | Status::Implemented);
        if traced && spec.scenarios.is_empty() {
            violations.push(format!(
                "{}: an {status:?} spec must have scenarios",
                spec.name
            ));
        }
        for scenario in &spec.scenarios {
            if let Some((other, _)) = declared.insert(&scenario.id, (spec, scenario)) {
                violations.push(format!(
                    "{}: scenario {} is also declared in {}",
                    spec.name, scenario.id, other.name
                ));
            }
            if traced && !scenario.withdrawn && !references.contains_key(&scenario.id) {
                violations.push(format!(
                    "{}: scenario {} has no test (add a `spec: {}` marker to its test)",
                    spec.name, scenario.id, scenario.id
                ));
            }
        }
    }

    for (id, locations) in references {
        let where_ = locations.iter().cloned().collect::<Vec<_>>().join(", ");
        match declared.get(id.as_str()) {
            None => violations.push(format!("{where_}: references unknown scenario {id}")),
            Some((_, scenario)) if scenario.withdrawn => {
                violations.push(format!("{where_}: references withdrawn scenario {id}"));
            }
            Some(_) => {}
        }
    }

    violations
}

#[cfg(test)]
mod tests {
    use super::*;

    fn spec(status: Option<Status>, scenarios: &[(&str, bool)]) -> Spec {
        Spec {
            name: "docs/specs/x.md".to_owned(),
            status,
            scenarios: scenarios
                .iter()
                .map(|&(id, withdrawn)| Scenario {
                    id: id.to_owned(),
                    withdrawn,
                })
                .collect(),
        }
    }

    fn refs(ids: &[&str]) -> BTreeMap<String, BTreeSet<String>> {
        ids.iter()
            .map(|&id| (id.to_owned(), BTreeSet::from(["crates/a.rs".to_owned()])))
            .collect()
    }

    #[test]
    fn parses_status_and_scenarios_outside_code_blocks() {
        let text = "\
- **Status:** Accepted

### COND-001 — Rest restores stamina
### COND-002 — Old rule (Withdrawn)
### Not a scenario

```markdown
### COND-999 — Example inside a code block
```
";
        let parsed = parse_spec("c.md".to_owned(), text);
        assert_eq!(parsed.status, Some(Status::Accepted));
        assert_eq!(
            parsed.scenarios,
            [
                Scenario {
                    id: "COND-001".to_owned(),
                    withdrawn: false
                },
                Scenario {
                    id: "COND-002".to_owned(),
                    withdrawn: true
                },
            ]
        );
    }

    #[test]
    fn unknown_status_values_parse_as_none() {
        let parsed = parse_spec("c.md".to_owned(), "- **Status:** Draft | Accepted\n");
        assert_eq!(parsed.status, None);
    }

    #[test]
    fn leading_id_requires_letters_dash_and_exactly_three_digits() {
        assert_eq!(leading_id("DRAFT-007 — title"), Some("DRAFT-007"));
        assert_eq!(leading_id("DRAFT-007"), Some("DRAFT-007"));
        assert_eq!(leading_id("DRAFT-07"), None);
        assert_eq!(leading_id("DRAFT-0071"), None);
        assert_eq!(leading_id("DRAFT-007a"), None);
        assert_eq!(leading_id("-007"), None);
        assert_eq!(leading_id("draft-007"), None);
    }

    #[test]
    fn finds_single_and_listed_references() {
        let text = "// spec: COND-001\n// spec: COND-002, MAST-010\nlet spec = 3;\n";
        assert_eq!(find_references(text), ["COND-001", "COND-002", "MAST-010"]);
    }

    #[test]
    fn a_fully_traced_accepted_spec_passes() {
        let specs = [spec(
            Some(Status::Accepted),
            &[("A-001", false), ("A-002", true)],
        )];
        assert_eq!(check(&specs, &refs(&["A-001"])), Vec::<String>::new());
    }

    #[test]
    fn an_untested_scenario_in_an_accepted_spec_is_reported() {
        let specs = [spec(Some(Status::Implemented), &[("A-001", false)])];
        let violations = check(&specs, &refs(&[]));
        assert_eq!(violations.len(), 1);
        assert!(violations[0].contains("scenario A-001 has no test"));
    }

    #[test]
    fn draft_specs_are_not_traced() {
        let specs = [spec(Some(Status::Draft), &[("A-001", false)])];
        assert_eq!(check(&specs, &refs(&[])), Vec::<String>::new());
    }

    #[test]
    fn an_accepted_spec_without_scenarios_is_reported() {
        let specs = [spec(Some(Status::Accepted), &[])];
        assert_eq!(
            check(&specs, &refs(&[])),
            ["docs/specs/x.md: an Accepted spec must have scenarios"]
        );
    }

    #[test]
    fn a_missing_status_is_reported() {
        let violations = check(&[spec(None, &[])], &refs(&[]));
        assert_eq!(violations.len(), 1);
        assert!(violations[0].contains("missing or unknown"));
    }

    #[test]
    fn duplicate_ids_are_reported() {
        let specs = [
            spec(Some(Status::Draft), &[("A-001", false)]),
            spec(Some(Status::Draft), &[("A-001", false)]),
        ];
        let violations = check(&specs, &refs(&["A-001"]));
        assert_eq!(violations.len(), 1);
        assert!(violations[0].contains("A-001 is also declared"));
    }

    #[test]
    fn unknown_and_withdrawn_references_are_reported() {
        let specs = [spec(
            Some(Status::Accepted),
            &[("A-001", true), ("A-002", false)],
        )];
        assert_eq!(
            check(&specs, &refs(&["A-001", "A-002", "Z-999"])),
            [
                "crates/a.rs: references withdrawn scenario A-001",
                "crates/a.rs: references unknown scenario Z-999",
            ]
        );
    }

    #[test]
    fn the_repository_is_traceable() {
        let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("..");
        assert_eq!(run(&root).unwrap(), Vec::<String>::new());
    }
}
