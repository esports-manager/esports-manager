// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! Text the backend asks an adapter to show: a Fluent message id and typed
//! arguments, never prose (ADR 0007).
//!
//! Every id is a string literal passed to `Message::new`, so the i18n gate
//! can find the ids Rust uses and check each one exists in `src/locales`.

use serde::Serialize;

use crate::content::{NameKind, PackageError, Problem};

/// One Fluent message with its arguments.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, specta::Type)]
#[serde(rename_all = "camelCase")]
pub struct Message {
    pub id: String,
    pub args: Vec<MessageArg>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, specta::Type)]
#[serde(rename_all = "camelCase")]
pub struct MessageArg {
    pub name: String,
    pub value: ArgValue,
}

/// A Fluent argument. `Message` is the name of another message, such as a
/// team's name in package text, which the adapter resolves first.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, specta::Type)]
#[serde(tag = "kind", content = "value", rename_all = "camelCase")]
pub enum ArgValue {
    Text(String),
    /// Counts and limits; a JavaScript number holds them exactly.
    Number(#[specta(type = i32)] i64),
    Message(String),
}

impl Message {
    #[must_use]
    pub fn new(id: &str) -> Self {
        Self {
            id: id.to_owned(),
            args: Vec::new(),
        }
    }

    /// A message from a package's own text, such as a team's name
    /// (`team-azure_tigers`), or one whose id is only known at run time. The
    /// i18n gate checks `Message::new` ids against the game's catalogs;
    /// these come from content instead.
    #[must_use]
    pub fn content(id: &str) -> Self {
        Self::new(id)
    }

    #[must_use]
    pub fn text(mut self, name: &str, value: impl Into<String>) -> Self {
        self.args.push(MessageArg {
            name: name.to_owned(),
            value: ArgValue::Text(value.into()),
        });
        self
    }

    /// A number argument, clamped to the `i32` range a JavaScript number
    /// and the bindings promise to hold exactly.
    #[must_use]
    pub fn number(mut self, name: &str, value: impl Into<i64>) -> Self {
        let value = value.into().clamp(i64::from(i32::MIN), i64::from(i32::MAX));
        self.args.push(MessageArg {
            name: name.to_owned(),
            value: ArgValue::Number(value),
        });
        self
    }

    #[must_use]
    pub fn message(mut self, name: &str, id: impl Into<String>) -> Self {
        self.args.push(MessageArg {
            name: name.to_owned(),
            value: ArgValue::Message(id.into()),
        });
        self
    }
}

fn count(value: usize) -> i64 {
    i64::try_from(value).unwrap_or(i64::MAX)
}

/// The message for a package problem, with its file and path.
#[must_use]
pub fn package_error(error: PackageError) -> Message {
    problem(error.problem)
        .text("file", error.file)
        .text("path", error.path)
}

fn problem(problem: Problem) -> Message {
    match problem {
        Problem::Unreadable { reason } => Message::new("problem-unreadable").text("reason", reason),
        Problem::MissingFile => Message::new("problem-missing-file"),
        Problem::UnknownFolder => Message::new("problem-unknown-folder"),
        Problem::UnexpectedFile => Message::new("problem-unexpected-file"),
        Problem::Syntax { line, column } => Message::new("problem-syntax")
            .number("line", count(line))
            .number("column", count(column)),
        Problem::NotAnEntity => Message::new("problem-not-an-entity"),
        Problem::NotUtf8 => Message::new("problem-not-utf8"),
        Problem::Empty => Message::new("problem-empty"),
        Problem::UnknownField { field } => {
            Message::new("problem-unknown-field").text("field", field)
        }
        Problem::DuplicateField { field } => {
            Message::new("problem-duplicate-field").text("field", field)
        }
        Problem::MissingField { field } => {
            Message::new("problem-missing-field").text("field", field)
        }
        Problem::InvalidValue { detail } => {
            Message::new("problem-invalid-value").text("detail", detail)
        }
        Problem::InvalidFormat => Message::new("problem-invalid-format"),
        Problem::OutOfRange => Message::new("problem-out-of-range"),
        Problem::InvalidId { id } => Message::new("problem-invalid-id").text("id", id),
        Problem::WrongKind { id, expected } => Message::new("problem-wrong-kind")
            .text("id", id.to_string())
            .text("expected", expected),
        Problem::DuplicateId { id, other_file } => Message::new("problem-duplicate-id")
            .text("id", id.to_string())
            .text("other", other_file),
        Problem::UnresolvedReference { field, id } => Message::new("problem-unresolved-reference")
            .text("field", field)
            .text("id", id),
        Problem::WrongCount {
            folder,
            count: found,
        } => Message::new("problem-wrong-count")
            .text("folder", folder)
            .number("count", count(found)),
        Problem::UnsupportedGenre { genre } => {
            Message::new("problem-unsupported-genre").text("genre", genre)
        }
        Problem::UnknownLocale { locale } => {
            Message::new("problem-unknown-locale").text("locale", locale)
        }
        Problem::TextSyntax { line } => {
            Message::new("problem-text-syntax").number("line", count(line))
        }
        Problem::MissingText { message, locale } => Message::new("problem-missing-text")
            .text("message", message)
            .text("locale", locale),
        Problem::InvalidMix { region } => {
            Message::new("problem-invalid-mix").text("region", region.to_string())
        }
        Problem::EmptyNamePool { nationality, names } => Message::new(match names {
            NameKind::Given => "problem-empty-given-names",
            NameKind::Family => "problem-empty-family-names",
        })
        .text("nationality", nationality.to_string()),
        Problem::RoleSet(error) => role_set_problem(error),
        Problem::TooManySubs { subs, roles } => Message::new("problem-too-many-subs")
            .number("subs", i64::from(subs))
            .number("roles", count(roles)),
        Problem::DuplicateNickname {
            nickname,
            player,
            other,
        } => Message::new("problem-duplicate-nickname")
            .text("player", player.to_string())
            .text("nickname", nickname)
            .text("other", other.to_string()),
        Problem::NicknamePoolTooSmall { distinct, needed } => Message::new("problem-nickname-pool")
            .number("distinct", count(distinct))
            .number("needed", count(needed)),
        Problem::IncompletableRoster {
            team,
            missing_roles,
        } => Message::new("problem-incompletable-roster")
            .text("team", team.to_string())
            .text(
                "roles",
                missing_roles
                    .iter()
                    .map(ToString::to_string)
                    .collect::<Vec<_>>()
                    .join(", "),
            ),
    }
}

fn role_set_problem(error: esports::moba::roles::RoleSetError) -> Message {
    use esports::moba::roles::RoleSetError;
    match error {
        RoleSetError::Empty => Message::new("problem-no-roles"),
        RoleSetError::DuplicateRole(role) => {
            Message::new("problem-duplicate-role").text("role", role.to_string())
        }
        RoleSetError::MissingWeight { role, attribute } => Message::new("problem-missing-weight")
            .text("role", role.to_string())
            .message("attribute", crate::views::attribute_message(attribute)),
        RoleSetError::ZeroWeights(role) => {
            Message::new("problem-zero-weights").text("role", role.to_string())
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use domain::id::ContentId;

    fn id(text: &str) -> ContentId {
        ContentId::parse(text).unwrap()
    }

    #[test]
    fn a_message_keeps_its_arguments_in_order() {
        let message = Message::new("cli-team")
            .text("tag", "AZT")
            .number("stars", 5)
            .message("name", "team-azure_tigers");
        assert_eq!(message.id, "cli-team");
        let args: Vec<(&str, &ArgValue)> = message
            .args
            .iter()
            .map(|a| (a.name.as_str(), &a.value))
            .collect();
        assert_eq!(
            args,
            [
                ("tag", &ArgValue::Text("AZT".to_owned())),
                ("stars", &ArgValue::Number(5)),
                ("name", &ArgValue::Message("team-azure_tigers".to_owned())),
            ]
        );
    }

    #[test]
    fn counts_become_numbers() {
        let syntax = problem(Problem::Syntax {
            line: 3,
            column: 14,
        });
        let values: Vec<&ArgValue> = syntax.args.iter().map(|a| &a.value).collect();
        assert_eq!(values, [&ArgValue::Number(3), &ArgValue::Number(14)]);
        assert_eq!(count(usize::MAX), i64::MAX);
        let huge = Message::new("cli-team").number("stars", i64::MAX);
        assert_eq!(huge.args[0].value, ArgValue::Number(i64::from(i32::MAX)));
    }

    #[test]
    fn package_errors_carry_their_file_and_path() {
        let error = PackageError::new(
            "teams/a.json",
            "[2].reputaton",
            Problem::UnknownField {
                field: "reputaton".to_owned(),
            },
        );
        let message = package_error(error);
        assert_eq!(message.id, "problem-unknown-field");
        let names: Vec<&str> = message.args.iter().map(|a| a.name.as_str()).collect();
        assert_eq!(names, ["field", "file", "path"]);
    }

    #[test]
    fn every_problem_has_its_own_message() {
        use esports::moba::attributes::OverallAttribute;
        use esports::moba::roles::RoleSetError;
        let problems = [
            Problem::Unreadable { reason: "r".into() },
            Problem::MissingFile,
            Problem::UnknownFolder,
            Problem::UnexpectedFile,
            Problem::Syntax { line: 1, column: 2 },
            Problem::NotAnEntity,
            Problem::NotUtf8,
            Problem::Empty,
            Problem::DuplicateField { field: "id".into() },
            Problem::UnknownField { field: "f".into() },
            Problem::MissingField { field: "f".into() },
            Problem::InvalidValue { detail: "d".into() },
            Problem::InvalidFormat,
            Problem::OutOfRange,
            Problem::InvalidId { id: "x".into() },
            Problem::WrongKind {
                id: id("team:a"),
                expected: "player".into(),
            },
            Problem::DuplicateId {
                id: id("team:a"),
                other_file: "b".into(),
            },
            Problem::UnresolvedReference {
                field: "f".into(),
                id: "x".into(),
            },
            Problem::WrongCount {
                folder: "roles/".into(),
                count: 2,
            },
            Problem::UnsupportedGenre { genre: "g".into() },
            Problem::UnknownLocale {
                locale: "fr".into(),
            },
            Problem::TextSyntax { line: 3 },
            Problem::MissingText {
                message: "m".into(),
                locale: "en".into(),
            },
            Problem::InvalidMix {
                region: id("region:r"),
            },
            Problem::EmptyNamePool {
                nationality: id("nationality:se"),
                names: NameKind::Given,
            },
            Problem::EmptyNamePool {
                nationality: id("nationality:se"),
                names: NameKind::Family,
            },
            Problem::RoleSet(RoleSetError::Empty),
            Problem::RoleSet(RoleSetError::DuplicateRole(id("role:a"))),
            Problem::RoleSet(RoleSetError::MissingWeight {
                role: id("role:a"),
                attribute: OverallAttribute::Composure,
            }),
            Problem::RoleSet(RoleSetError::ZeroWeights(id("role:a"))),
            Problem::TooManySubs { subs: 6, roles: 5 },
            Problem::DuplicateNickname {
                nickname: "n".into(),
                player: id("player:b"),
                other: id("player:a"),
            },
            Problem::NicknamePoolTooSmall {
                distinct: 1,
                needed: 2,
            },
            Problem::IncompletableRoster {
                team: id("team:a"),
                missing_roles: vec![id("role:a"), id("role:b")],
            },
        ];
        let total = problems.len();
        let messages: Vec<Message> = problems.into_iter().map(problem).collect();
        let ids: std::collections::BTreeSet<&str> =
            messages.iter().map(|m| m.id.as_str()).collect();
        assert_eq!(ids.len(), total);
        let roster = messages.last().unwrap();
        assert_eq!(
            roster.args[1].value,
            ArgValue::Text("role:a, role:b".to_owned())
        );
    }
}
