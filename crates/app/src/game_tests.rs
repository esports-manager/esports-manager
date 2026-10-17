// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! Use case tests with in-memory content and saves.

use std::cell::RefCell;
use std::collections::BTreeMap;

use esports::Genre;
use esports::moba::fixtures::{id, template};
use esports::moba::world::World;

use super::*;
use crate::content::ContentText;
use crate::content::{Manifest, Problem};
use crate::saves::SaveListing;

/// Content that loads the fixture template, or fails with fixed problems.
struct Content(Result<Package, Vec<PackageError>>);

impl ContentSource for Content {
    fn load(&self) -> Result<Package, Vec<PackageError>> {
        self.0.clone()
    }
}

fn content() -> Content {
    Content(Ok(Package {
        manifest: Manifest {
            id: "test".into(),
            version: "1.0.0".into(),
            title: "Test".into(),
            license: "GPL-3.0-or-later".into(),
            authors: vec![],
            genre: Genre::Moba,
            locales: vec!["en".into()],
        },
        content_hash: [9; 32],
        template: template(),
        texts: vec![ContentText {
            locale: "en".into(),
            file: "locales/en/teams.ftl".into(),
            source: "team-a = A\n".into(),
        }],
    }))
}

#[derive(Clone)]
struct Stored {
    meta: SaveMeta,
    world: World,
    texts: Vec<ContentText>,
}

/// Saves kept in memory, keyed by file name.
#[derive(Default)]
struct Store(RefCell<BTreeMap<String, Stored>>);

impl SaveStore for Store {
    type Save = Stored;

    fn create(&self, save: NewSave) -> Result<String, SaveError> {
        let mut saves = self.0.borrow_mut();
        if saves
            .values()
            .any(|s| s.meta.name.to_lowercase() == save.meta.name.to_lowercase())
        {
            return Err(SaveError::NameTaken(save.meta.name));
        }
        let file = format!("{}.esmsave", saves.len());
        let NewSave { meta, world, texts } = save;
        saves.insert(file.clone(), Stored { meta, world, texts });
        Ok(file)
    }

    fn list(&self) -> Result<Vec<SaveListing>, SaveError> {
        let mut listings: Vec<SaveListing> = self
            .0
            .borrow()
            .iter()
            .map(|(file, stored)| SaveListing {
                file: file.clone(),
                save: Ok(stored.meta.clone()),
                in_use: false,
            })
            .collect();
        listings.push(SaveListing {
            file: "broken.esmsave".into(),
            save: Err(Damage::NotASave),
            in_use: false,
        });
        Ok(listings)
    }

    fn open(&self, file: &str, now: Timestamp) -> Result<Stored, SaveError> {
        let mut saves = self.0.borrow_mut();
        let stored = saves
            .get_mut(file)
            .ok_or_else(|| SaveError::NotFound(file.to_owned()))?;
        stored.meta.last_played_at = now;
        Ok(stored.clone())
    }
}

impl OpenSave for Stored {
    fn meta(&self) -> &SaveMeta {
        &self.meta
    }
    fn team(&mut self, id: &ContentId) -> Result<Option<Team>, SaveError> {
        Ok(self.world.teams.iter().find(|t| &t.id == id).cloned())
    }
    fn players_of(&mut self, team: &ContentId) -> Result<Vec<Player>, SaveError> {
        Ok(self
            .world
            .players
            .iter()
            .filter(|p| &p.team == team)
            .cloned()
            .collect())
    }
    fn player(&mut self, id: &ContentId) -> Result<Option<Player>, SaveError> {
        Ok(self.world.players.iter().find(|p| &p.id == id).cloned())
    }
    fn roles(&mut self) -> Result<RoleSet, SaveError> {
        Ok(self.world.roles.clone())
    }
    fn regions(&mut self) -> Result<Vec<domain::world::Region>, SaveError> {
        Ok(self.world.regions.clone())
    }
    fn nationalities(&mut self) -> Result<Vec<Nationality>, SaveError> {
        Ok(self.world.nationalities.clone())
    }
    fn competitions(&mut self) -> Result<Vec<Competition>, SaveError> {
        Ok(self.world.competitions.clone())
    }
    fn texts(&mut self) -> Result<Vec<ContentText>, SaveError> {
        Ok(self.texts.clone())
    }
}

fn request(manager: &str, team: &str, save: &str, seed: u64) -> NewGameRequest {
    NewGameRequest {
        manager_name: manager.into(),
        team: team.into(),
        save_name: save.into(),
        seed: Some(seed.to_string()),
        random_seed: 999,
        now: Timestamp(1_000),
    }
}

/// Changes the stored world of the only save, as a later day of play would.
fn edit_world(store: &Store, change: impl FnOnce(&mut World)) {
    let mut saves = store.0.borrow_mut();
    let stored = saves.values_mut().next().unwrap();
    change(&mut stored.world);
}

fn started(store: &Store) -> Stored {
    let file = new_game(&content(), store, &request("Ana", "team:a", "Ana's A", 42))
        .unwrap()
        .file;
    store.open(&file, Timestamp(2_000)).unwrap()
}

#[test]
fn new_game_offers_every_region_and_its_teams() {
    // Given
    let content = content();
    // When
    let options = new_game_options(&content).unwrap();
    // Then
    assert_eq!(options.regions.len(), 1);
    let region = &options.regions[0];
    assert_eq!(
        (
            region.name_message.as_str(),
            region.league_message.as_deref()
        ),
        ("region-r", Some("competition-league"))
    );
    let teams: Vec<(&str, &str, u8)> = region
        .teams
        .iter()
        .map(|t| (t.name_message.as_str(), t.crest.tag.as_str(), t.strength))
        .collect();
    assert_eq!(teams, [("team-a", "AAA", 4), ("team-b", "AAA", 2)]);
    assert_eq!(region.teams[0].crest.fill, "#1E5AA8");
    assert_eq!(region.teams[0].crest.border, "#F2C14E");
}

#[test]
fn a_new_game_creates_a_save_for_the_chosen_team() {
    // spec: NEWG-003
    // Given
    let store = Store::default();
    // When
    let created = new_game(
        &content(),
        &store,
        &request("  Ana ", "team:a", "Ana's A", 42),
    )
    .unwrap();
    // Then
    assert_eq!(created.team, "team:a");
    let mut save = store.open(&created.file, Timestamp(2_000)).unwrap();
    assert_eq!(save.meta().manager_name, "Ana");
    assert_eq!(save.meta().name, "Ana's A");
    assert_eq!(save.meta().seed, WorldSeed::new(42));
    assert_eq!(save.meta().created_at, Timestamp(1_000));
    assert_eq!(save.meta().packages[0].content_hash, [9; 32]);
    assert_eq!(save.meta().game_date.to_string(), "2027-01-01");
    assert_eq!(save.players_of(&id("team:a")).unwrap().len(), 7);
    assert_eq!(save.texts().unwrap().len(), 1);
}

#[test]
fn invalid_requests_report_every_problem_and_write_nothing() {
    // spec: NEWG-006
    // Given
    let store = Store::default();
    // When
    let result = new_game(
        &content(),
        &store,
        &request("   ", "team:nowhere", "Save", 1),
    );
    // Then
    assert_eq!(
        result,
        Err(NewGameError::Invalid(vec![
            RequestProblem::EmptyManagerName,
            RequestProblem::UnknownTeam {
                team: "team:nowhere".into()
            },
        ]))
    );
    assert!(store.0.borrow().is_empty());
}

#[test]
fn names_are_limited_in_characters_not_bytes() {
    let store = Store::default();
    let long_manager = "á".repeat(32);
    assert!(
        new_game(
            &content(),
            &store,
            &request(&long_manager, "team:a", "One", 1)
        )
        .is_ok()
    );
    let too_long = "á".repeat(33);
    let save_too_long = "x".repeat(49);
    let result = new_game(
        &content(),
        &store,
        &request(&too_long, "team:a", &save_too_long, 1),
    );
    assert_eq!(
        result,
        Err(NewGameError::Invalid(vec![
            RequestProblem::ManagerNameTooLong,
            RequestProblem::SaveNameTooLong
        ]))
    );
    let result = new_game(&content(), &store, &request("Ana\u{7}", "bad id", "", 1));
    assert_eq!(
        result,
        Err(NewGameError::Invalid(vec![
            RequestProblem::ControlCharacters { field: "manager" },
            RequestProblem::EmptySaveName,
            RequestProblem::UnknownTeam {
                team: "bad id".into()
            },
        ]))
    );
}

#[test]
fn a_broken_package_produces_no_save() {
    // spec: PKG-012
    // Given
    let broken = Content(Err(vec![PackageError::new(
        "teams/a.json",
        "",
        Problem::MissingFile,
    )]));
    let store = Store::default();
    // When
    let result = new_game(&broken, &store, &request("Ana", "team:a", "Save", 1));
    // Then
    assert!(matches!(result, Err(NewGameError::Package(ref errors)) if errors.len() == 1));
    assert!(store.0.borrow().is_empty());
    assert!(new_game_options(&broken).is_err());
}

#[test]
fn a_taken_save_name_is_reported() {
    let store = Store::default();
    new_game(&content(), &store, &request("Ana", "team:a", "Tigers", 1)).unwrap();
    let result = new_game(&content(), &store, &request("Bo", "team:b", "tigers", 2));
    assert_eq!(
        result,
        Err(NewGameError::Invalid(vec![RequestProblem::SaveNameTaken {
            name: "tigers".into()
        }]))
    );
}

#[test]
fn saves_list_with_their_summary_and_damage() {
    let store = Store::default();
    new_game(&content(), &store, &request("Ana", "team:a", "Tigers", 1)).unwrap();
    let saves = list_saves(&store).unwrap();
    assert_eq!(
        saves,
        [
            SaveSummary::Ready {
                file: "0.esmsave".into(),
                in_use: false,
                name: "Tigers".into(),
                manager_name: "Ana".into(),
                team_message: "team-a".into(),
                game_date: "2027-01-01".into(),
                last_played_at: 1_000,
            },
            SaveSummary::Damaged {
                file: "broken.esmsave".into(),
                damage: DamageView::NotASave
            },
        ]
    );
    assert_eq!(damage_view(Damage::NewerVersion), DamageView::NewerVersion);
}

#[test]
fn starters_come_first_then_subs_in_role_order() {
    // spec: ROST-001
    // Given
    let mut save = started(&Store::default());
    // When
    let view = roster(&mut save, None).unwrap();
    // Then
    let roles = |players: &[RosterPlayer]| {
        players
            .iter()
            .map(|p| p.role_id.clone())
            .collect::<Vec<_>>()
    };
    assert_eq!(
        roles(&view.starters),
        [
            "role:top",
            "role:jungle",
            "role:mid",
            "role:bot",
            "role:support"
        ]
    );
    assert_eq!(view.subs.len(), 2);
    let order: Vec<usize> = view
        .subs
        .iter()
        .map(|p| {
            [
                "role:top",
                "role:jungle",
                "role:mid",
                "role:bot",
                "role:support",
            ]
            .iter()
            .position(|r| *r == p.role_id)
            .unwrap()
        })
        .collect();
    assert!(order.windows(2).all(|w| w[0] < w[1]));
    assert_eq!(view.team.name_message, "team-a");
    assert_eq!(view.team.region_message, "region-r");
    assert_eq!(
        view.team.league_message.as_deref(),
        Some("competition-league")
    );
}

#[test]
fn each_row_carries_what_the_table_shows() {
    // spec: ROST-002
    // Given
    let mut save = started(&Store::default());
    // When
    let view = roster(&mut save, None).unwrap();
    // Then
    for player in view.starters.iter().chain(&view.subs) {
        assert!(
            !player.nickname.is_empty()
                && !player.given_name.is_empty()
                && !player.family_name.is_empty()
        );
        assert_eq!(player.role_message, player.role_id.replace(':', "-"));
        assert_eq!(player.nationality.code.len(), 2);
        assert!((17..=29).contains(&player.age));
        assert!((1..=99).contains(&player.overall));
    }
    let kairos = view
        .starters
        .iter()
        .find(|p| p.nickname == "Kairos")
        .unwrap();
    assert_eq!(
        (kairos.age, kairos.name_order),
        (29, NameOrderView::FamilyFirst)
    );
    assert_eq!(kairos.nationality.name_message, "nationality-kr");
}

#[test]
fn the_overall_shown_is_the_attributes_specs_overall() {
    // spec: ROST-005
    // Given a player whose stored overall is 74.50
    let store = Store::default();
    let file = new_game(&content(), &store, &request("Ana", "team:a", "A", 42))
        .unwrap()
        .file;
    edit_world(&store, |world| {
        let kairos = world
            .players
            .iter_mut()
            .find(|p| p.id == id("player:kairos"))
            .unwrap();
        kairos.attributes = esports::moba::attributes::MobaAttributes::uniform(
            domain::rating::Rating::from_hundredths(7450).unwrap(),
        );
    });
    let mut save = store.open(&file, Timestamp(2)).unwrap();
    // When
    let view = roster(&mut save, None).unwrap();
    // Then
    let shown = view
        .starters
        .iter()
        .chain(&view.subs)
        .find(|p| p.id == "player:kairos")
        .unwrap()
        .overall;
    assert_eq!(shown, 75);
}

#[test]
fn players_in_the_same_role_and_group_are_ordered_by_nickname() {
    let store = Store::default();
    let file = new_game(&content(), &store, &request("Ana", "team:a", "A", 42))
        .unwrap()
        .file;
    edit_world(&store, |world| {
        let mut subs: Vec<&mut Player> = world
            .players
            .iter_mut()
            .filter(|p| p.team == id("team:a") && !p.starter)
            .collect();
        subs[0].role = id("role:top");
        subs[0].nickname = "Zed".into();
        subs[1].role = id("role:top");
        subs[1].nickname = "Abe".into();
    });
    let mut save = store.open(&file, Timestamp(2)).unwrap();
    let view = roster(&mut save, None).unwrap();
    let names: Vec<&str> = view.subs.iter().map(|p| p.nickname.as_str()).collect();
    assert_eq!(names, ["Abe", "Zed"]);
}

#[test]
fn every_request_problem_is_reported_together_with_a_taken_name() {
    let store = Store::default();
    new_game(&content(), &store, &request("Ana", "team:a", "Tigers", 1)).unwrap();
    let mut second = request("", "team:b", "TIGERS", 2);
    second.seed = Some("forty-two".into());
    assert_eq!(
        new_game(&content(), &store, &second),
        Err(NewGameError::Invalid(vec![
            RequestProblem::EmptyManagerName,
            RequestProblem::SaveNameTaken {
                name: "TIGERS".into()
            },
            RequestProblem::InvalidSeed {
                seed: "forty-two".into()
            },
        ]))
    );
}

#[test]
fn a_blank_seed_uses_the_random_one_and_ids_are_trimmed() {
    let store = Store::default();
    let mut blank = request("Ana", " team:a ", "A", 0);
    blank.seed = Some("  ".into());
    let file = new_game(&content(), &store, &blank).unwrap().file;
    let save = store.open(&file, Timestamp(2)).unwrap();
    assert_eq!(save.meta().seed, WorldSeed::new(999));
    let mut none = request("Ana", "team:a", "B", 0);
    none.seed = None;
    let file = new_game(&content(), &store, &none).unwrap().file;
    assert_eq!(
        store.open(&file, Timestamp(2)).unwrap().meta().seed,
        WorldSeed::new(999)
    );
}

#[test]
fn invisible_characters_are_refused() {
    let store = Store::default();
    // Joiners are part of real names and emoji, so they pass.
    let family = "Ana \u{1F468}\u{200D}\u{1F469}\u{200D}\u{1F467}";
    assert!(
        new_game(
            &content(),
            &store,
            &request(
                family,
                "team:a",
                "Persian \u{0645}\u{06CC}\u{200C}\u{062E}\u{0648}\u{0627}\u{0645}",
                1
            )
        )
        .is_ok()
    );
    let zero_width = new_game(&content(), &store, &request("Ana", "team:a", "\u{200B}", 1));
    assert_eq!(
        zero_width,
        Err(NewGameError::Invalid(vec![
            RequestProblem::EmptySaveName,
            RequestProblem::ControlCharacters { field: "save" },
        ]))
    );
    let override_ = new_game(
        &content(),
        &store,
        &request("Ana\u{202E}", "team:a", "Save", 1),
    );
    assert_eq!(
        override_,
        Err(NewGameError::Invalid(vec![
            RequestProblem::ControlCharacters { field: "manager" }
        ]))
    );
}

#[test]
fn find_save_prefers_the_file_and_refuses_ambiguous_names() {
    let store = Store::default();
    new_game(&content(), &store, &request("Ana", "team:a", "Tigers", 1)).unwrap();
    // A save named after another save's file name.
    new_game(
        &content(),
        &store,
        &request("Ana", "team:b", "0.esmsave", 2),
    )
    .unwrap();
    assert_eq!(find_save(&store, "0.esmsave"), Ok("0.esmsave".to_owned()));
    assert_eq!(find_save(&store, "tigers"), Ok("0.esmsave".to_owned()));
    assert_eq!(
        find_save(&store, "Nothing"),
        Err(QueryError::Save(SaveError::NotFound("Nothing".to_owned())))
    );
    // Two saves with one name can only come from files copied in by hand.
    store.0.borrow_mut().get_mut("1.esmsave").unwrap().meta.name = "Tigers".into();
    assert_eq!(
        find_save(&store, "TIGERS"),
        Err(QueryError::AmbiguousSave("TIGERS".to_owned()))
    );
}

#[test]
fn another_team_can_be_viewed_and_unknown_teams_are_errors() {
    let mut save = started(&Store::default());
    assert_eq!(roster(&mut save, Some("team:b")).unwrap().team.id, "team:b");
    assert_eq!(
        roster(&mut save, Some("team:zz")),
        Err(QueryError::UnknownTeam("team:zz".into()))
    );
}

#[test]
fn the_profile_shows_skills_and_traits_and_hides_hidden_attributes() {
    // spec: ROST-006, ATTR-007
    // Given
    let mut save = started(&Store::default());
    // When
    let profile = player_profile(&mut save, "player:kairos").unwrap();
    // Then
    assert_eq!(profile.skills.len(), 7);
    assert_eq!(profile.traits.len(), 4);
    assert!(
        profile
            .skills
            .iter()
            .chain(&profile.traits)
            .all(|a| a.value.is_some())
    );
    let hidden: Vec<(&str, Option<u8>)> = profile
        .hidden
        .iter()
        .map(|a| (a.name_message.as_str(), a.value))
        .collect();
    assert_eq!(
        hidden,
        [
            ("attribute-consistency", None),
            ("attribute-potential", None)
        ]
    );
    assert_eq!(profile.birth_date, "1997-03-14");
    assert!(profile.starter);
    assert_eq!(profile.team.id, "team:a");
    assert_eq!(profile.skills[0].name_message, "attribute-mechanics");
    assert_eq!(profile.traits[3].name_message, "attribute-work-ethic");
}

#[test]
fn an_unknown_player_is_an_error() {
    let mut save = started(&Store::default());
    assert_eq!(
        player_profile(&mut save, "player:nobody"),
        Err(QueryError::UnknownPlayer("player:nobody".into()))
    );
    assert_eq!(
        player_profile(&mut save, "Bad Id"),
        Err(QueryError::UnknownPlayer("Bad Id".into()))
    );
    assert_eq!(
        roster(&mut save, Some("Bad Id")),
        Err(QueryError::UnknownTeam("Bad Id".into()))
    );
}

#[test]
fn every_failure_has_a_message() {
    let invalid = new_game_messages(NewGameError::Invalid(vec![
        RequestProblem::EmptyManagerName,
        RequestProblem::ManagerNameTooLong,
        RequestProblem::EmptySaveName,
        RequestProblem::SaveNameTooLong,
        RequestProblem::ControlCharacters { field: "save" },
        RequestProblem::UnknownTeam { team: "x".into() },
        RequestProblem::SaveNameTaken { name: "n".into() },
        RequestProblem::InvalidSeed { seed: "s".into() },
    ]));
    let ids: Vec<&str> = invalid.iter().map(|m| m.id.as_str()).collect();
    assert_eq!(
        ids,
        [
            "error-manager-name-empty",
            "error-manager-name-long",
            "error-save-name-empty",
            "error-save-name-long",
            "error-control-characters",
            "error-unknown-team",
            "error-save-name-taken",
            "error-invalid-seed"
        ]
    );
    assert_eq!(
        invalid[1].args[0].value,
        crate::messages::ArgValue::Number(32)
    );
    assert_eq!(
        invalid[3].args[0].value,
        crate::messages::ArgValue::Number(48)
    );
    let package = new_game_messages(NewGameError::Package(vec![PackageError::new(
        "a",
        "",
        Problem::MissingFile,
    )]));
    assert_eq!(package[0].id, "problem-missing-file");
    let generation = new_game_messages(NewGameError::Generation(
        GenerationError::NicknamesExhausted,
    ));
    assert_eq!(generation[0].id, "error-generation");
    let saves = [
        SaveError::NameTaken("n".into()),
        SaveError::NotFound("f".into()),
        SaveError::NotASave,
        SaveError::NewerVersion,
        SaveError::InUse,
        SaveError::Storage("d".into()),
    ];
    let ids: Vec<String> = saves
        .iter()
        .map(|e| {
            new_game_messages(NewGameError::Save(e.clone()))[0]
                .id
                .clone()
        })
        .collect();
    assert_eq!(
        ids,
        [
            "error-save-name-taken",
            "error-save-not-found",
            "error-save-not-a-save",
            "error-save-newer",
            "error-save-in-use",
            "error-storage"
        ]
    );
    assert_eq!(
        query_message(QueryError::UnknownTeam("t".into())).id,
        "error-unknown-team"
    );
    assert_eq!(
        query_message(QueryError::UnknownPlayer("p".into())).id,
        "error-unknown-player"
    );
    assert_eq!(
        query_message(QueryError::Save(SaveError::NotFound("f".into()))).id,
        "error-save-not-found"
    );
}
