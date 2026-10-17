// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! Every error message the use cases build formats cleanly through the
//! game's catalogs: each variable its text names is passed, with the right
//! kind of value, in every locale (ADR 0007). The examples cover every
//! variant; a new variant doesn't compile until it has one here.
#![allow(clippy::unwrap_used, reason = "test")]

use std::path::Path;

use app::content::{NameKind, PackageError, Problem};
use app::game::{NewGameError, QueryError, RequestProblem, new_game_messages, query_message};
use app::messages::{ArgValue, Message};
use app::saves::SaveError;
use domain::id::ContentId;
use esports::moba::attributes::OverallAttribute;
use esports::moba::generation::GenerationError;
use esports::moba::roles::RoleSetError;
use fluent_bundle::{FluentArgs, FluentBundle, FluentResource, FluentValue};

const LOCALES: [&str; 2] = ["en", "pt-BR"];

fn id(text: &str) -> ContentId {
    ContentId::parse(text).unwrap()
}

/// One example of every package problem.
fn problems() -> Vec<Problem> {
    let mut examples = file_problems();
    examples.extend(content_problems());
    for example in &examples {
        covered(example);
    }
    examples
}

/// Problems with a file's form.
fn file_problems() -> Vec<Problem> {
    vec![
        Problem::Unreadable {
            reason: "denied".into(),
        },
        Problem::MissingFile,
        Problem::UnknownFolder,
        Problem::UnexpectedFile,
        Problem::Syntax {
            line: 3,
            column: 14,
        },
        Problem::NotAnEntity,
        Problem::NotUtf8,
        Problem::UnknownField {
            field: "reputaton".into(),
        },
        Problem::DuplicateField { field: "id".into() },
        Problem::MissingField { field: "id".into() },
        Problem::InvalidValue {
            detail: "expected a number".into(),
        },
        Problem::Empty,
        Problem::InvalidFormat,
        Problem::OutOfRange,
        Problem::InvalidId {
            id: "Team:A".into(),
        },
        Problem::WrongKind {
            id: id("team:a"),
            expected: "players".into(),
        },
        Problem::DuplicateId {
            id: id("team:a"),
            other_file: "teams/b.json".into(),
        },
        Problem::UnresolvedReference {
            field: "region".into(),
            id: "region:x".into(),
        },
        Problem::WrongCount {
            folder: "roles".into(),
            count: 2,
        },
        Problem::UnsupportedGenre {
            genre: "fps".into(),
        },
        Problem::UnknownLocale {
            locale: "xx".into(),
        },
        Problem::TextSyntax { line: 2 },
    ]
}

/// Problems with what the files say.
fn content_problems() -> Vec<Problem> {
    vec![
        Problem::MissingText {
            message: "team-a".into(),
            locale: "en".into(),
        },
        Problem::InvalidMix {
            region: id("region:r"),
        },
        Problem::EmptyNamePool {
            nationality: id("nationality:kr"),
            names: NameKind::Given,
        },
        Problem::EmptyNamePool {
            nationality: id("nationality:kr"),
            names: NameKind::Family,
        },
        Problem::RoleSet(RoleSetError::Empty),
        Problem::RoleSet(RoleSetError::DuplicateRole(id("role:mid"))),
        Problem::RoleSet(RoleSetError::MissingWeight {
            role: id("role:mid"),
            attribute: OverallAttribute::Composure,
        }),
        Problem::RoleSet(RoleSetError::ZeroWeights(id("role:mid"))),
        Problem::TooManySubs { subs: 6, roles: 5 },
        Problem::DuplicateNickname {
            nickname: "Kairos".into(),
            player: id("player:a"),
            other: id("player:b"),
        },
        Problem::NicknamePoolTooSmall {
            distinct: 10,
            needed: 30,
        },
        Problem::IncompletableRoster {
            team: id("team:a"),
            missing_roles: vec![id("role:mid")],
        },
    ]
}

/// Fails to compile when a variant is added, until it has an example.
fn covered(problem: &Problem) {
    match problem {
        Problem::Unreadable { .. }
        | Problem::MissingFile
        | Problem::UnknownFolder
        | Problem::UnexpectedFile
        | Problem::Syntax { .. }
        | Problem::NotAnEntity
        | Problem::NotUtf8
        | Problem::UnknownField { .. }
        | Problem::DuplicateField { .. }
        | Problem::MissingField { .. }
        | Problem::InvalidValue { .. }
        | Problem::Empty
        | Problem::InvalidFormat
        | Problem::OutOfRange
        | Problem::InvalidId { .. }
        | Problem::WrongKind { .. }
        | Problem::DuplicateId { .. }
        | Problem::UnresolvedReference { .. }
        | Problem::WrongCount { .. }
        | Problem::UnsupportedGenre { .. }
        | Problem::UnknownLocale { .. }
        | Problem::TextSyntax { .. }
        | Problem::MissingText { .. }
        | Problem::InvalidMix { .. }
        | Problem::EmptyNamePool { .. }
        | Problem::RoleSet(
            RoleSetError::Empty
            | RoleSetError::DuplicateRole(_)
            | RoleSetError::MissingWeight { .. }
            | RoleSetError::ZeroWeights(_),
        )
        | Problem::TooManySubs { .. }
        | Problem::DuplicateNickname { .. }
        | Problem::NicknamePoolTooSmall { .. }
        | Problem::IncompletableRoster { .. } => {}
    }
}

fn save_errors() -> Vec<SaveError> {
    let examples = vec![
        SaveError::NameTaken("Tigers".into()),
        SaveError::NotFound("tigers.esmsave".into()),
        SaveError::NotASave,
        SaveError::NewerVersion,
        SaveError::InUse,
        SaveError::Storage("disk full".into()),
    ];
    for example in &examples {
        match example {
            SaveError::NameTaken(_)
            | SaveError::NotFound(_)
            | SaveError::NotASave
            | SaveError::NewerVersion
            | SaveError::InUse
            | SaveError::Storage(_) => {}
        }
    }
    examples
}

fn request_problems() -> Vec<RequestProblem> {
    let examples = vec![
        RequestProblem::EmptyManagerName,
        RequestProblem::ManagerNameTooLong,
        RequestProblem::EmptySaveName,
        RequestProblem::SaveNameTooLong,
        RequestProblem::ControlCharacters { field: "manager" },
        RequestProblem::ControlCharacters { field: "save" },
        RequestProblem::UnknownTeam {
            team: "team:x".into(),
        },
        RequestProblem::SaveNameTaken {
            name: "Tigers".into(),
        },
        RequestProblem::InvalidSeed { seed: "abc".into() },
    ];
    for example in &examples {
        match example {
            RequestProblem::EmptyManagerName
            | RequestProblem::ManagerNameTooLong
            | RequestProblem::EmptySaveName
            | RequestProblem::SaveNameTooLong
            | RequestProblem::ControlCharacters { .. }
            | RequestProblem::UnknownTeam { .. }
            | RequestProblem::SaveNameTaken { .. }
            | RequestProblem::InvalidSeed { .. } => {}
        }
    }
    examples
}

/// Every message the use cases build for a failure.
fn messages() -> Vec<Message> {
    let mut all = new_game_messages(NewGameError::Invalid(request_problems()));
    let package: Vec<PackageError> = problems()
        .into_iter()
        .map(|problem| PackageError::new("teams/a.json", "[0].tag", problem))
        .collect();
    all.extend(new_game_messages(NewGameError::Package(package)));
    all.extend(new_game_messages(NewGameError::Generation(
        GenerationError::NicknamesExhausted,
    )));
    for error in save_errors() {
        all.extend(new_game_messages(NewGameError::Save(error.clone())));
        all.push(query_message(QueryError::Save(error)));
    }
    for error in [
        QueryError::UnknownTeam("team:x".into()),
        QueryError::UnknownPlayer("player:x".into()),
        QueryError::AmbiguousSave("Tigers".into()),
    ] {
        all.push(query_message(error));
    }
    all
}

/// The game's catalogs and the core package's text for `locale`.
fn bundle(locale: &str) -> FluentBundle<FluentResource> {
    let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
    let language: unic_langid::LanguageIdentifier = locale.parse().unwrap();
    let mut bundle = FluentBundle::new(vec![language]);
    bundle.set_use_isolating(false);
    for dir in [
        root.join("src/locales").join(locale),
        root.join("content/core/locales").join(locale),
    ] {
        for file in std::fs::read_dir(dir).unwrap() {
            let source = std::fs::read_to_string(file.unwrap().path()).unwrap();
            bundle
                .add_resource(FluentResource::try_new(source).unwrap())
                .unwrap();
        }
    }
    bundle
}

/// Formats `message`, collecting every Fluent error, its arguments' included.
fn format(
    bundle: &FluentBundle<FluentResource>,
    message: &Message,
    errors: &mut Vec<String>,
) -> String {
    let mut args = FluentArgs::new();
    for arg in &message.args {
        let value = match &arg.value {
            ArgValue::Text(text) => FluentValue::from(text.clone()),
            ArgValue::Number(number) => FluentValue::from(*number),
            ArgValue::Message(id) => {
                FluentValue::from(format(bundle, &Message::content(id), errors))
            }
        };
        args.set(arg.name.clone(), value);
    }
    let Some(pattern) = bundle.get_message(&message.id).and_then(|m| m.value()) else {
        errors.push(format!("no message {}", message.id));
        return String::new();
    };
    let mut found = Vec::new();
    let text = bundle
        .format_pattern(pattern, Some(&args), &mut found)
        .into_owned();
    errors.extend(
        found
            .iter()
            .map(|error| format!("{}: {error:?}", message.id)),
    );
    text
}

#[test]
fn every_error_message_formats_with_the_arguments_it_is_given() {
    let mut problems = Vec::new();
    for locale in LOCALES {
        let bundle = bundle(locale);
        for message in messages() {
            let mut errors = Vec::new();
            let text = format(&bundle, &message, &mut errors);
            if !errors.is_empty() || text.contains('{') {
                problems.push(format!("{locale}: {text:?} {errors:?}"));
            }
        }
    }
    assert!(problems.is_empty(), "{problems:#?}");
}
