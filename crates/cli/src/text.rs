// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! Renders [`Message`]s as text through Fluent (ADR 0007): the game's own
//! catalogs from `src/locales`, built into the binary, plus a package's text.
//! A message missing in the chosen locale falls back to `en`.

use app::content::ContentText;
use app::messages::{ArgValue, Message};
use fluent_bundle::{FluentArgs, FluentBundle, FluentResource, FluentValue};
use unic_langid::LanguageIdentifier;

/// The fallback for every other locale.
pub const FALLBACK: &str = "en";
pub const LOCALES: [&str; 2] = ["en", "pt-BR"];

/// Every catalog under `src/locales`, as `(locale, file, source)`. A test
/// checks this list against the folder.
pub const CATALOGS: [(&str, &str, &str); 14] = [
    (
        "en",
        "cli.ftl",
        include_str!("../../../src/locales/en/cli.ftl"),
    ),
    (
        "en",
        "errors.ftl",
        include_str!("../../../src/locales/en/errors.ftl"),
    ),
    (
        "en",
        "main.ftl",
        include_str!("../../../src/locales/en/main.ftl"),
    ),
    (
        "en",
        "people.ftl",
        include_str!("../../../src/locales/en/people.ftl"),
    ),
    (
        "en",
        "problems.ftl",
        include_str!("../../../src/locales/en/problems.ftl"),
    ),
    (
        "en",
        "saves.ftl",
        include_str!("../../../src/locales/en/saves.ftl"),
    ),
    (
        "en",
        "screens.ftl",
        include_str!("../../../src/locales/en/screens.ftl"),
    ),
    (
        "pt-BR",
        "cli.ftl",
        include_str!("../../../src/locales/pt-BR/cli.ftl"),
    ),
    (
        "pt-BR",
        "errors.ftl",
        include_str!("../../../src/locales/pt-BR/errors.ftl"),
    ),
    (
        "pt-BR",
        "main.ftl",
        include_str!("../../../src/locales/pt-BR/main.ftl"),
    ),
    (
        "pt-BR",
        "people.ftl",
        include_str!("../../../src/locales/pt-BR/people.ftl"),
    ),
    (
        "pt-BR",
        "problems.ftl",
        include_str!("../../../src/locales/pt-BR/problems.ftl"),
    ),
    (
        "pt-BR",
        "saves.ftl",
        include_str!("../../../src/locales/pt-BR/saves.ftl"),
    ),
    (
        "pt-BR",
        "screens.ftl",
        include_str!("../../../src/locales/pt-BR/screens.ftl"),
    ),
];

/// Text in one locale, falling back to `en`.
pub struct Text {
    bundles: Vec<FluentBundle<FluentResource>>,
}

impl Text {
    /// The game's catalogs and `content` (a package's or a save's text) for
    /// `locale`, then for `en`. An unknown locale falls back to `en` alone.
    #[must_use]
    pub fn new(locale: &str, content: &[ContentText]) -> Self {
        let mut chain = vec![locale];
        if locale != FALLBACK {
            chain.push(FALLBACK);
        }
        let bundles = chain
            .into_iter()
            .filter(|locale| LOCALES.contains(locale))
            .map(|locale| bundle(locale, content))
            .collect();
        Self { bundles }
    }

    /// The message, or its id when no locale defines it.
    #[must_use]
    pub fn render(&self, message: &Message) -> String {
        let mut args = FluentArgs::new();
        for arg in &message.args {
            let value = match &arg.value {
                ArgValue::Text(text) => FluentValue::from(text.clone()),
                ArgValue::Number(number) => FluentValue::from(*number),
                ArgValue::Message(id) => FluentValue::from(self.render(&Message::content(id))),
            };
            args.set(arg.name.clone(), value);
        }
        for bundle in &self.bundles {
            if let Some(pattern) = bundle.get_message(&message.id).and_then(|m| m.value()) {
                let mut errors = Vec::new();
                return bundle
                    .format_pattern(pattern, Some(&args), &mut errors)
                    .into_owned();
            }
        }
        message.id.clone()
    }
}

fn bundle(locale: &str, content: &[ContentText]) -> FluentBundle<FluentResource> {
    let language: LanguageIdentifier = locale.parse().unwrap_or_default();
    let mut bundle = FluentBundle::new(vec![language]);
    // No Unicode isolation marks around arguments: this text goes to a
    // terminal, not a bidirectional layout.
    bundle.set_use_isolating(false);
    let game = CATALOGS
        .iter()
        .filter(|(catalog, _, _)| *catalog == locale)
        .map(|(_, _, source)| *source);
    let package = content
        .iter()
        .filter(|text| text.locale == locale)
        .map(|text| text.source.as_str());
    for source in game.chain(package) {
        let resource =
            FluentResource::try_new(source.to_owned()).unwrap_or_else(|(partial, _)| partial);
        // A package may not override the game's messages; duplicates are
        // skipped, not fatal.
        let _ = bundle.add_resource(resource);
    }
    bundle
}

#[cfg(test)]
mod tests {
    use super::*;

    fn content(locale: &str, source: &str) -> ContentText {
        ContentText {
            locale: locale.to_owned(),
            file: format!("locales/{locale}/teams.ftl"),
            source: source.to_owned(),
        }
    }

    #[test]
    fn renders_the_game_catalogs_with_arguments() {
        let text = Text::new("en", &[]);
        let message = Message::new("error-save-name-long").number("max", 48);
        assert_eq!(
            text.render(&message),
            "The save name can have at most 48 characters."
        );
        let pt = Text::new("pt-BR", &[]);
        assert_eq!(
            pt.render(&message),
            "O nome do jogo salvo pode ter no máximo 48 caracteres."
        );
    }

    #[test]
    fn package_names_resolve_inside_other_messages() {
        let text = Text::new("en", &[content("en", "team-a = Azure Tigers\n")]);
        let message = Message::new("cli-new-game-created")
            .text("file", "a.esmsave")
            .message("team", "team-a");
        assert_eq!(
            text.render(&message),
            "Created a.esmsave with Azure Tigers."
        );
    }

    #[test]
    fn a_name_missing_in_another_locale_falls_back() {
        // spec: PKG-011
        // Given
        let texts = [
            content("en", "team-a = Azure Tigers\n"),
            content("pt-BR", "team-b = Equipe B\n"),
        ];
        // When
        let shown = Text::new("pt-BR", &texts).render(&Message::content("team-a"));
        // Then
        assert_eq!(shown, "Azure Tigers");
    }

    #[test]
    fn selectors_follow_their_argument() {
        let text = Text::new("en", &[]);
        let name = |order: &str| {
            text.render(
                &Message::new("person-full-name")
                    .text("order", order)
                    .text("given", "Do-yun")
                    .text("family", "Han"),
            )
        };
        assert_eq!(name("family-first"), "Han Do-yun");
        assert_eq!(name("given-first"), "Do-yun Han");
    }

    #[test]
    fn unknown_messages_and_locales_fall_back_visibly() {
        assert_eq!(
            Text::new("en", &[]).render(&Message::content("no-such-message")),
            "no-such-message"
        );
        let klingon = Text::new("tlh", &[]);
        assert_eq!(
            klingon.render(&Message::new("error-save-newer")),
            "This save was made by a newer version of the game."
        );
    }

    #[test]
    fn broken_package_text_keeps_what_parses() {
        let text = Text::new("en", &[content("en", "team-a = A\n= broken\nteam-b = B\n")]);
        assert_eq!(text.render(&Message::content("team-a")), "A");
        assert_eq!(text.render(&Message::content("team-b")), "B");
    }

    #[test]
    fn every_catalog_file_is_built_in() {
        let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../src/locales");
        let mut on_disk = Vec::new();
        for locale in std::fs::read_dir(&root).unwrap() {
            let locale = locale.unwrap();
            for file in std::fs::read_dir(locale.path()).unwrap() {
                on_disk.push((
                    locale.file_name().into_string().unwrap(),
                    file.unwrap().file_name().into_string().unwrap(),
                ));
            }
        }
        on_disk.sort();
        let mut built_in: Vec<(String, String)> = CATALOGS
            .iter()
            .map(|(l, f, _)| ((*l).to_owned(), (*f).to_owned()))
            .collect();
        built_in.sort();
        assert_eq!(
            built_in, on_disk,
            "update CATALOGS in crates/cli/src/text.rs"
        );
    }

    /// Every message of every catalog formats without a Fluent error in
    /// every locale, given a value for each variable it names, with the core
    /// package's text loaded for the names it refers to.
    #[test]
    fn every_message_formats_without_errors() {
        let core =
            std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../content/core/locales");
        let mut texts = Vec::new();
        for locale in LOCALES {
            for file in std::fs::read_dir(core.join(locale)).unwrap() {
                let path = file.unwrap().path();
                texts.push(content(locale, &std::fs::read_to_string(path).unwrap()));
            }
        }
        let mut problems = Vec::new();
        for locale in LOCALES {
            let bundle = bundle(locale, &texts);
            for (_, file, source) in CATALOGS.iter().filter(|(l, _, _)| *l == locale) {
                // Every `$name` in the file gets a value; a number suits both
                // text and selectors.
                let mut args = FluentArgs::new();
                for name in source.split('$').skip(1) {
                    let name: String = name
                        .chars()
                        .take_while(|c| c.is_ascii_alphanumeric() || *c == '-' || *c == '_')
                        .collect();
                    args.set(name, FluentValue::from(1));
                }
                let resource = FluentResource::try_new((*source).to_owned()).unwrap();
                for entry in resource.entries() {
                    let fluent_syntax::ast::Entry::Message(message) = entry else {
                        continue;
                    };
                    let found = bundle.get_message(message.id.name).unwrap();
                    let patterns = found
                        .value()
                        .into_iter()
                        .chain(found.attributes().map(|a| a.value()));
                    for pattern in patterns {
                        let mut errors = Vec::new();
                        let _ = bundle.format_pattern(pattern, Some(&args), &mut errors);
                        if !errors.is_empty() {
                            problems
                                .push(format!("{locale}/{file}: {}: {errors:?}", message.id.name));
                        }
                    }
                }
            }
        }
        assert!(problems.is_empty(), "{problems:#?}");
    }
}
