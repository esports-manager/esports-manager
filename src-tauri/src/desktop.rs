// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! What the desktop app holds while it runs: the save store, the content it
//! builds new worlds from, and the save the player has open. Every command
//! is one call into here, so the adapter's behaviour is tested without a
//! window.

use std::path::{Path, PathBuf};

use app::content::ContentText;
use app::game::{self, NewGameRequest};
use app::locations::DataLocations;
use app::messages::{Message, package_error};
use app::saves::{OpenSave, SaveStore, Timestamp};
use app::views::{Failure, GameOpened, NewGameOptions, PlayerProfile, RosterView, SaveSummary};
use db::{SqliteSave, SqliteSaveStore};
use packages::PackageDir;
use serde::Deserialize;

/// What New Game sends. The seed is text because a `u64` doesn't survive a
/// JavaScript number.
#[derive(Debug, PartialEq, Eq, Deserialize, specta::Type)]
#[serde(rename_all = "camelCase")]
pub struct NewGameInput {
    pub manager_name: String,
    pub team: String,
    pub save_name: String,
    pub seed: Option<String>,
}

pub struct Desktop {
    store: SqliteSaveStore,
    content: PackageDir,
    /// The open save and its file name.
    open: Option<(String, SqliteSave)>,
}

fn fail(message: Message) -> Failure {
    Failure {
        messages: vec![message],
    }
}

impl Desktop {
    #[must_use]
    pub fn new(saves: PathBuf, content: PathBuf) -> Self {
        Self {
            store: SqliteSaveStore::new(saves),
            content: PackageDir(content),
            open: None,
        }
    }

    /// # Errors
    ///
    /// The package's problems.
    pub fn new_game_options(&self) -> Result<NewGameOptions, Failure> {
        game::new_game_options(&self.content).map_err(|errors| Failure {
            messages: errors.into_iter().map(package_error).collect(),
        })
    }

    /// The text of the open save's packages, or of the content New Game
    /// builds from when no save is open.
    ///
    /// # Errors
    ///
    /// When the save or the package can't be read.
    pub fn content_text(&mut self) -> Result<Vec<ContentText>, Failure> {
        match &mut self.open {
            Some((_, save)) => save.texts().map_err(|e| fail(game::save_message(e))),
            None => packages::load(&self.content.0)
                .map(|p| p.texts)
                .map_err(|errors| Failure {
                    messages: errors.into_iter().map(package_error).collect(),
                }),
        }
    }

    /// Creates the game and opens it.
    ///
    /// # Errors
    ///
    /// Every problem with the request, the package or the save.
    pub fn start_new_game(
        &mut self,
        input: NewGameInput,
        random_seed: u64,
        now: Timestamp,
    ) -> Result<GameOpened, Failure> {
        let request = NewGameRequest {
            manager_name: input.manager_name,
            team: input.team,
            save_name: input.save_name,
            seed: input.seed,
            random_seed,
            now,
        };
        let created =
            game::new_game(&self.content, &self.store, &request).map_err(|error| Failure {
                messages: game::new_game_messages(error),
            })?;
        self.open_save(&created.file, now)
    }

    /// # Errors
    ///
    /// When the saves folder can't be read.
    pub fn list_saves(&self) -> Result<Vec<SaveSummary>, Failure> {
        let saves = game::list_saves(&self.store).map_err(|e| fail(game::save_message(e)))?;
        // The save this app holds open shows as locked to its own probe; to
        // the player it is simply the game they're playing.
        Ok(saves
            .into_iter()
            .map(|mut save| {
                if let (SaveSummary::Ready { file, in_use, .. }, Some((open, _))) =
                    (&mut save, &self.open)
                    && file == open
                {
                    *in_use = false;
                }
                save
            })
            .collect())
    }

    /// Opens a save. The one that was open stays open if this fails; it is
    /// closed first only when it is the same file, whose lock it holds.
    ///
    /// # Errors
    ///
    /// When the save can't be opened.
    pub fn open_save(&mut self, file: &str, now: Timestamp) -> Result<GameOpened, Failure> {
        if self.open.as_ref().is_some_and(|(open, _)| open == file) {
            self.open = None;
        }
        let save = self
            .store
            .open(file, now)
            .map_err(|e| fail(game::save_message(e)))?;
        let opened = GameOpened::new(file.to_owned(), &save.meta().team);
        self.open = Some((file.to_owned(), save));
        Ok(opened)
    }

    fn save(&mut self) -> Result<&mut SqliteSave, Failure> {
        self.open
            .as_mut()
            .map(|(_, save)| save)
            .ok_or_else(|| fail(Message::new("error-no-save-open")))
    }

    /// # Errors
    ///
    /// When no save is open, the team doesn't exist or storage fails.
    pub fn roster(&mut self, team: Option<&str>) -> Result<RosterView, Failure> {
        game::roster(self.save()?, team).map_err(|e| fail(game::query_message(e)))
    }

    /// # Errors
    ///
    /// When no save is open, the player doesn't exist or storage fails.
    pub fn player(&mut self, id: &str) -> Result<PlayerProfile, Failure> {
        game::player_profile(self.save()?, id).map_err(|e| fail(game::query_message(e)))
    }
}

/// How the main window is built.
#[derive(Debug, PartialEq, Eq)]
pub struct WindowConfig {
    pub label: &'static str,
    pub width: u32,
    pub height: u32,
    pub min_width: u32,
    pub min_height: u32,
    /// The webview's own data folder, inside the portable folder in
    /// portable mode (SAVE-006). `None` keeps the platform default.
    pub data_directory: Option<PathBuf>,
}

#[must_use]
pub fn window_config(locations: &DataLocations) -> WindowConfig {
    WindowConfig {
        label: "main",
        width: 1440,
        height: 900,
        min_width: 960,
        min_height: 600,
        data_directory: locations.webview(),
    }
}

/// Where the bundled core package is, inside the app's resources.
#[must_use]
pub fn core_content(resources: &Path) -> PathBuf {
    resources.join("content").join("core")
}

#[cfg(test)]
mod tests {
    use super::*;
    use app::locations::{Environment, Platform, resolve};

    fn folder(name: &str) -> PathBuf {
        let dir = std::env::temp_dir().join(format!("esm-desktop-{name}-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        dir
    }

    fn core() -> PathBuf {
        core_content(&Path::new(env!("CARGO_MANIFEST_DIR")).join(".."))
    }

    fn desktop(name: &str) -> Desktop {
        Desktop::new(folder(name), core())
    }

    fn input(save: &str, seed: Option<&str>) -> NewGameInput {
        NewGameInput {
            manager_name: "Ana".into(),
            team: "team:azure_tigers".into(),
            save_name: save.into(),
            seed: seed.map(str::to_owned),
        }
    }

    fn ids(failure: &Failure) -> Vec<&str> {
        failure.messages.iter().map(|m| m.id.as_str()).collect()
    }

    #[test]
    fn new_game_options_come_from_the_bundled_package() {
        let options = desktop("options").new_game_options().unwrap();
        assert_eq!(options.regions.len(), 2);
    }

    #[test]
    fn a_new_game_is_created_and_opened() {
        let mut desktop = desktop("start");
        let opened = desktop
            .start_new_game(input("Tigers", Some(" 42 ")), 7, Timestamp(1))
            .unwrap();
        assert_eq!(
            opened,
            GameOpened {
                file: "tigers.esmsave".into(),
                team: "team:azure_tigers".into(),
                team_message: "team-azure_tigers".into(),
            }
        );
        let roster = desktop.roster(None).unwrap();
        assert_eq!(roster.team.id, "team:azure_tigers");
        assert_eq!(roster.starters.len(), 5);
        let profile = desktop.player("player:kairos").unwrap();
        assert_eq!(profile.player.nickname, "Kairos");
    }

    #[test]
    fn the_given_seed_wins_over_the_drawn_one() {
        let mut one = desktop("seed-one");
        one.start_new_game(input("A", Some("42")), 1, Timestamp(1))
            .unwrap();
        let mut two = desktop("seed-two");
        two.start_new_game(input("A", None), 42, Timestamp(1))
            .unwrap();
        let mut three = desktop("seed-three");
        three
            .start_new_game(input("A", Some("  ")), 42, Timestamp(1))
            .unwrap();
        let roster = |d: &mut Desktop| d.roster(None).unwrap();
        assert_eq!(roster(&mut one), roster(&mut two));
        assert_eq!(roster(&mut two), roster(&mut three));
    }

    #[test]
    fn an_invalid_seed_is_reported() {
        let failure = desktop("bad-seed")
            .start_new_game(input("A", Some("forty-two")), 1, Timestamp(1))
            .unwrap_err();
        assert_eq!(ids(&failure), ["error-invalid-seed"]);
    }

    #[test]
    fn new_game_failures_carry_every_message() {
        let mut desktop = desktop("invalid");
        let failure = desktop
            .start_new_game(
                NewGameInput {
                    manager_name: String::new(),
                    team: "team:nope".into(),
                    save_name: "x".into(),
                    seed: None,
                },
                1,
                Timestamp(1),
            )
            .unwrap_err();
        assert_eq!(
            ids(&failure),
            ["error-manager-name-empty", "error-unknown-team"]
        );
    }

    #[test]
    fn queries_need_an_open_save() {
        let mut desktop = desktop("closed");
        assert_eq!(
            ids(&desktop.roster(None).unwrap_err()),
            ["error-no-save-open"]
        );
        assert_eq!(
            ids(&desktop.player("player:kairos").unwrap_err()),
            ["error-no-save-open"]
        );
        desktop
            .start_new_game(input("A", Some("1")), 1, Timestamp(1))
            .unwrap();
        assert_eq!(
            ids(&desktop.roster(Some("team:nowhere")).unwrap_err()),
            ["error-unknown-team"]
        );
        assert_eq!(
            ids(&desktop.player("player:nobody").unwrap_err()),
            ["error-unknown-player"]
        );
    }

    #[test]
    fn opening_another_save_releases_the_first() {
        let mut desktop = desktop("switch");
        desktop
            .start_new_game(input("First", Some("1")), 1, Timestamp(1))
            .unwrap();
        desktop
            .start_new_game(input("Second", Some("2")), 1, Timestamp(2))
            .unwrap();
        let reopened = desktop.open_save("first.esmsave", Timestamp(3)).unwrap();
        assert_eq!(reopened.file, "first.esmsave");
        // The second save's lock was released when the first was opened.
        assert!(desktop.open_save("second.esmsave", Timestamp(4)).is_ok());
        let saves = desktop.list_saves().unwrap();
        assert_eq!(saves.len(), 2);
        // The open save is listed as ready, not as in use by this app, and
        // first: it was played last.
        let files: Vec<(&str, bool)> = saves
            .iter()
            .filter_map(|save| match save {
                SaveSummary::Ready { file, in_use, .. } => Some((file.as_str(), *in_use)),
                SaveSummary::Damaged { .. } => None,
            })
            .collect();
        assert_eq!(
            files,
            [("second.esmsave", false), ("first.esmsave", false)],
            "{saves:?}"
        );
        assert_eq!(
            ids(&desktop
                .open_save("missing.esmsave", Timestamp(5))
                .unwrap_err()),
            ["error-save-not-found"]
        );
    }

    #[test]
    fn other_damaged_saves_stay_damaged() {
        let dir = folder("damaged");
        std::fs::write(dir.join("broken.esmsave"), b"not a save").unwrap();
        let mut desktop = Desktop::new(dir, core());
        desktop
            .start_new_game(input("Open", Some("1")), 1, Timestamp(1))
            .unwrap();
        let saves = desktop.list_saves().unwrap();
        let damaged: Vec<&SaveSummary> = saves
            .iter()
            .filter(|s| matches!(s, SaveSummary::Damaged { .. }))
            .collect();
        assert_eq!(damaged.len(), 1, "{saves:?}");
    }

    #[test]
    fn content_text_comes_from_the_package_then_the_save() {
        let mut desktop = desktop("text");
        let before = desktop.content_text().unwrap();
        assert!(
            before
                .iter()
                .any(|t| t.locale == "pt-BR" && t.source.contains("team-azure_tigers"))
        );
        desktop
            .start_new_game(input("A", Some("1")), 1, Timestamp(1))
            .unwrap();
        let after = desktop.content_text().unwrap();
        assert_eq!(after.len(), before.len());
    }

    #[test]
    fn a_broken_package_is_reported() {
        let mut desktop = Desktop::new(folder("broken"), PathBuf::from("/definitely/not/here"));
        assert_eq!(
            ids(&desktop.new_game_options().unwrap_err()),
            ["problem-unreadable"]
        );
        assert_eq!(
            ids(&desktop.content_text().unwrap_err()),
            ["problem-unreadable"]
        );
    }

    #[test]
    fn a_listing_failure_is_reported() {
        let desktop = Desktop::new(PathBuf::from("/definitely/not/here"), core());
        assert_eq!(ids(&desktop.list_saves().unwrap_err()), ["error-storage"]);
    }

    fn environment(portable: bool) -> Environment {
        Environment {
            data_dir_flag: None,
            executable_dir: Some(PathBuf::from("/games/esm")),
            portable_marker: portable,
            os_data_dir: Some(PathBuf::from("/home/ana/.local/share")),
            platform: Platform::Linux,
        }
    }

    #[test]
    fn portable_desktop_keeps_webview_data_inside_the_folder() {
        // spec: SAVE-006
        // Given
        let locations = resolve(&environment(true)).unwrap();
        // When
        let config = window_config(&locations);
        // Then
        assert_eq!(
            config.data_directory,
            Some(PathBuf::from("/games/esm/data/webview"))
        );
        assert_eq!(config.label, "main");
        assert_eq!(
            window_config(&resolve(&environment(false)).unwrap()).data_directory,
            None
        );
    }

    /// The wiring behind SAVE-007; the smoke test checks the scenario
    /// itself with both real binaries.
    #[test]
    fn the_desktop_app_resolves_its_data_folder_like_the_cli() {
        assert_eq!(
            crate::data_locations().unwrap(),
            db::environment::locations(None).unwrap()
        );
    }

    #[test]
    fn the_cli_and_the_desktop_see_the_same_roster() {
        // spec: ROST-011
        // Given a new game: Ana's Azure Tigers from seed 42, the game the
        // CLI built `src/test/fixtures/roster.json` from (`just e2e-fixtures`)
        let mut desktop = desktop("same-roster");
        desktop
            .start_new_game(input("Ana's Tigers", Some("42")), 1, Timestamp(1))
            .unwrap();
        // When the desktop app's `get_roster` command builds the view
        let view = serde_json::to_value(desktop.roster(None).unwrap()).unwrap();
        // Then it is the view `esm roster --json` printed
        let cli: serde_json::Value = serde_json::from_str(
            &std::fs::read_to_string(
                Path::new(env!("CARGO_MANIFEST_DIR")).join("../src/test/fixtures/roster.json"),
            )
            .unwrap(),
        )
        .unwrap();
        assert_eq!(view, cli);
    }

    #[test]
    fn the_core_package_is_under_the_resources() {
        assert_eq!(
            core_content(Path::new("/app/res")),
            PathBuf::from("/app/res/content/core")
        );
    }
}
