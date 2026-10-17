// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! Loader tests against a small valid package built in memory, which each
//! test breaks in one way.

use std::collections::BTreeMap;
use std::fmt::Write;

use domain::id::ContentId;
use esports::moba::roles::RoleSetError;
use serde_json::{Value, json};

use super::*;

fn id(text: &str) -> ContentId {
    ContentId::parse(text).unwrap()
}

const ROLES: [&str; 5] = ["top", "jungle", "mid", "bot", "support"];

/// A valid package: one region, two nationalities, two teams, five roles.
struct Fixture {
    files: BTreeMap<String, Value>,
    texts: BTreeMap<String, String>,
}

impl Fixture {
    fn new() -> Self {
        let roles = role_set_roles();
        let nicknames: Vec<String> = (0..100).map(|n| format!("Nick{n:02}")).collect();
        let mut files = BTreeMap::new();
        let mut put = |path: &str, value: Value| {
            files.insert(path.to_owned(), value);
        };
        put(
            "manifest.json",
            json!({"id": "test", "version": "1.0.0", "title": "Test", "license": "GPL-3.0-or-later",
                   "authors": ["Tester"], "genre": "moba", "locales": ["en", "pt-BR"]}),
        );
        put("world.json", json!({"start_date": "2027-01-01"}));
        put(
            "regions/r.json",
            json!({"id": "region:r", "level": 4, "nationalities": {"nationality:kr": 9, "nationality:br": 1}}),
        );
        put(
            "nationalities/all.json",
            json!([
                {"id": "nationality:kr", "code": "KR", "name_order": "family_first"},
                {"id": "nationality:br", "code": "BR", "name_order": "given_first"}
            ]),
        );
        put(
            "name-pools/kr.json",
            json!({"id": "name_pool:kr", "nationality": "nationality:kr", "given": ["Do-yun"], "family": ["Han"]}),
        );
        put(
            "name-pools/br.json",
            json!({"id": "name_pool:br", "nationality": "nationality:br", "given": ["Caio"], "family": ["Ribeiro"]}),
        );
        put(
            "nicknames/all.json",
            json!({"id": "nickname_pool:test", "nicknames": nicknames}),
        );
        put(
            "competitions/league.json",
            json!({"id": "competition:league", "region": "region:r", "teams": ["team:a", "team:b"]}),
        );
        put("teams/a.json", team("a"));
        put("teams/b.json", team("b"));
        put(
            "roles/core.json",
            json!({"id": "role_set:core", "roles": roles, "subs": 2}),
        );
        put(
            "generation/core.json",
            json!({"id": "generation:core", "mu_base": 35.0, "mu_per_reputation": 0.4, "sigma_base": 12.0,
                   "sigma_per_reputation": 0.07, "sigma_min": 2.0, "attribute_spread": 6.0, "bias_scale": 8.0,
                   "style_mean": 50.0, "style_spread": 15.0, "consistency_mean": 55.0, "consistency_spread": 15.0,
                   "potential_peak_age": 24.0, "potential_per_year": 2.5, "potential_spread": 6.0,
                   "age_mean": 22.0, "age_spread": 2.5, "age_min": 17, "age_max": 28, "nickname_pool_factor": 3}),
        );
        let mut en = String::new();
        for message in [
            "region-r",
            "nationality-kr",
            "nationality-br",
            "competition-league",
            "team-a",
            "team-b",
            "role-top",
            "role-jungle",
            "role-mid",
            "role-bot",
            "role-support",
        ] {
            writeln!(en, "{message} = {message}").unwrap();
        }
        let mut texts = BTreeMap::new();
        texts.insert("locales/en/names.ftl".to_owned(), en);
        texts.insert(
            "locales/pt-BR/names.ftl".to_owned(),
            "team-a = Equipe A\n".to_owned(),
        );
        Self { files, texts }
    }

    fn set(&mut self, path: &str, value: Value) -> &mut Self {
        self.files.insert(path.to_owned(), value);
        self
    }

    fn edit(&mut self, path: &str, change: impl FnOnce(&mut Value)) -> &mut Self {
        change(self.files.get_mut(path).unwrap());
        self
    }

    fn remove(&mut self, path: &str) -> &mut Self {
        self.files.remove(path);
        self
    }

    fn text(&mut self, path: &str, source: &str) -> &mut Self {
        self.texts.insert(path.to_owned(), source.to_owned());
        self
    }

    fn files(&self) -> PackageFiles {
        let mut files = PackageFiles::new();
        for (path, value) in &self.files {
            files.insert(path.clone(), value.to_string());
        }
        for (path, source) in &self.texts {
            files.insert(path.clone(), source.clone());
        }
        files
    }

    fn load(&self) -> Result<Package, Vec<PackageError>> {
        load_files(&self.files())
    }

    fn errors(&self) -> Vec<PackageError> {
        self.load().unwrap_err()
    }
}

/// The core role weights, as package JSON.
fn role_set_roles() -> Vec<Value> {
    let weights = |row: [u32; 9]| {
        let keys = [
            "mechanics",
            "laning",
            "game_sense",
            "awareness",
            "positioning",
            "champion_pool_breadth",
            "shotcalling",
            "teamwork",
            "composure",
        ];
        keys.iter()
            .zip(row)
            .map(|(k, w)| ((*k).to_owned(), json!(w)))
            .collect::<serde_json::Map<_, _>>()
    };
    let rows = [
        [16, 18, 14, 10, 12, 6, 4, 10, 10],
        [14, 6, 20, 14, 8, 6, 14, 10, 8],
        [20, 16, 14, 10, 12, 8, 6, 6, 8],
        [20, 18, 10, 10, 16, 6, 4, 8, 8],
        [10, 12, 14, 16, 12, 6, 14, 10, 6],
    ];
    ROLES
        .iter()
        .zip(rows)
        .map(|(role, row)| json!({"id": format!("role:{role}"), "weights": weights(row)}))
        .collect()
}

fn team(slug: &str) -> Value {
    json!({"id": format!("team:{slug}"), "region": "region:r", "tag": "AAA",
           "colours": ["#1E5AA8", "#F2C14E"], "reputation": 50})
}

fn error(file: &str, path: &str, problem: Problem) -> PackageError {
    PackageError::new(file, path, problem)
}

#[test]
fn the_fixture_is_valid() {
    let package = Fixture::new().load().unwrap();
    assert_eq!(package.manifest.id, "test");
    assert_eq!(package.manifest.locales, ["en", "pt-BR"]);
    assert_eq!(
        package.template.settings.start_date.to_string(),
        "2027-01-01"
    );
    assert_eq!(package.template.regions[0].level, 4);
    assert_eq!(
        package.template.regions[0].nationalities,
        [(id("nationality:br"), 1), (id("nationality:kr"), 9)]
    );
    assert_eq!(package.template.nationalities.len(), 2);
    assert_eq!(package.template.name_pools.len(), 2);
    assert_eq!(package.template.nicknames.len(), 100);
    assert_eq!(
        package.template.competitions[0].teams,
        [id("team:a"), id("team:b")]
    );
    assert_eq!(package.template.teams.len(), 2);
    assert_eq!(package.template.teams[0].tag.as_str(), "AAA");
    assert_eq!(package.template.teams[0].colours[1].to_string(), "#F2C14E");
    assert_eq!(package.template.teams[0].reputation.value(), 50);
    assert_eq!(package.template.roles.roles().len(), 5);
    assert_eq!(package.template.roster.subs, 2);
    assert!((package.template.generation.common.mu_per_reputation - 0.4).abs() < f64::EPSILON);
    assert_eq!(package.template.generation.common.age_max, 28);
    assert_eq!(package.texts.len(), 2);
    assert_eq!(package.content_hash, Fixture::new().files().content_hash());
}

#[test]
fn subfolders_and_file_names_carry_no_meaning() {
    // spec: PKG-003
    // Given
    let player =
        json!({"id": "player:kairos", "team": "team:a", "role": "role:mid", "nickname": "Kairos"});
    let mut nested = Fixture::new();
    nested.set("players/kr/anything.json", player.clone());
    let mut moved = Fixture::new();
    moved.set("players/kairos.json", player);
    // When
    let (nested, moved) = (nested.load().unwrap(), moved.load().unwrap());
    // Then
    assert_eq!(nested.template.players, moved.template.players);
    assert_eq!(nested.template.players[0].id, id("player:kairos"));
}

#[test]
fn duplicate_ids_are_reported_with_both_files() {
    // spec: PKG-004
    // Given
    let mut fixture = Fixture::new();
    fixture.set("teams/b.json", team("a"));
    // When
    let errors = fixture.errors();
    // Then
    let duplicates: Vec<&PackageError> = errors
        .iter()
        .filter(|e| matches!(e.problem, Problem::DuplicateId { .. }))
        .collect();
    assert_eq!(
        duplicates,
        [&error(
            "teams/b.json",
            "id",
            Problem::DuplicateId {
                id: id("team:a"),
                other_file: "teams/a.json".to_owned()
            }
        )]
    );
}

#[test]
fn an_ids_kind_must_match_its_folder() {
    // spec: PKG-005
    // Given
    let mut fixture = Fixture::new();
    fixture.set(
        "players/wrong.json",
        json!({"id": "team:c", "team": "team:a", "role": "role:mid"}),
    );
    // When
    let errors = fixture.errors();
    // Then
    assert!(errors.contains(&error(
        "players/wrong.json",
        "id",
        Problem::WrongKind {
            id: id("team:c"),
            expected: "player".to_owned()
        }
    )));
}

#[test]
fn references_must_resolve() {
    // spec: PKG-008
    // Given
    let mut fixture = Fixture::new();
    fixture.edit("teams/a.json", |team| {
        team["region"] = json!("region:atlantis");
    });
    // When
    let errors = fixture.errors();
    // Then
    assert_eq!(
        errors,
        [error(
            "teams/a.json",
            "region",
            Problem::UnresolvedReference {
                field: "region".to_owned(),
                id: "region:atlantis".to_owned()
            }
        )]
    );
}

#[test]
fn every_error_is_reported_at_once_in_file_order() {
    // spec: PKG-009
    // Given
    let mut fixture = Fixture::new();
    fixture
        .set("teams/z.json", team("a"))
        .set(
            "players/p.json",
            json!({"id": "player:p", "team": "team:a", "role": "role:mid", "nickanme": "P"}),
        )
        .edit("competitions/league.json", |league| {
            league["region"] = json!("region:nowhere");
        });
    // When
    let errors = fixture.errors();
    // Then
    let files: Vec<&str> = errors.iter().map(|e| e.file.as_str()).collect();
    assert_eq!(
        files,
        ["competitions/league.json", "players/p.json", "teams/z.json"]
    );
    assert!(matches!(
        errors[0].problem,
        Problem::UnresolvedReference { .. }
    ));
    assert!(matches!(errors[1].problem, Problem::UnknownField { .. }));
    assert!(matches!(errors[2].problem, Problem::DuplicateId { .. }));
}

#[test]
fn translatable_names_must_exist_in_the_first_locale() {
    // spec: PKG-010
    // Given
    let mut fixture = Fixture::new();
    let en = fixture.texts["locales/en/names.ftl"].replace("team-b = team-b\n", "");
    fixture.text("locales/en/names.ftl", &en);
    // When
    let errors = fixture.errors();
    // Then
    assert_eq!(
        errors,
        [error(
            "teams/b.json",
            "id",
            Problem::MissingText {
                message: "team-b".to_owned(),
                locale: "en".to_owned()
            }
        )]
    );
}

#[test]
fn every_kind_of_name_needs_its_text() {
    let mut fixture = Fixture::new();
    fixture.text("locales/en/names.ftl", "");
    let missing: Vec<(String, String)> = fixture
        .errors()
        .into_iter()
        .filter_map(|e| {
            if let Problem::MissingText { message, .. } = e.problem {
                Some((e.file, message))
            } else {
                None
            }
        })
        .collect();
    assert_eq!(missing.len(), 11);
    assert!(missing.contains(&("roles/core.json".to_owned(), "role-support".to_owned())));
    assert!(missing.contains(&(
        "nationalities/all.json".to_owned(),
        "nationality-br".to_owned()
    )));
    assert!(missing.contains(&(
        "competitions/league.json".to_owned(),
        "competition-league".to_owned()
    )));
    assert!(missing.contains(&("regions/r.json".to_owned(), "region-r".to_owned())));
}

#[test]
fn text_in_an_undeclared_locale_is_an_error() {
    let mut fixture = Fixture::new();
    fixture.text("locales/fr/names.ftl", "team-a = Équipe A\n");
    assert_eq!(
        fixture.errors(),
        [error(
            "locales/fr/names.ftl",
            "",
            Problem::UnknownLocale {
                locale: "fr".to_owned()
            }
        )]
    );
}

#[test]
fn broken_text_reports_its_line() {
    let mut fixture = Fixture::new();
    fixture.text("locales/pt-BR/names.ftl", "team-a = Equipe A\n\n= broken\n");
    assert_eq!(
        fixture.errors(),
        [error(
            "locales/pt-BR/names.ftl",
            "",
            Problem::TextSyntax { line: 3 }
        )]
    );
}

#[test]
fn invalid_weights_are_package_errors() {
    // spec: ATTR-006
    // Given
    let mut fixture = Fixture::new();
    fixture.edit("roles/core.json", |set| {
        let roles = set["roles"].as_array_mut().unwrap();
        for weight in roles[4]["weights"].as_object_mut().unwrap().values_mut() {
            *weight = json!(0);
        }
        roles[1]["weights"]
            .as_object_mut()
            .unwrap()
            .remove("composure");
    });
    // When
    let errors = fixture.errors();
    // Then
    let problems: Vec<&Problem> = errors.iter().map(|e| &e.problem).collect();
    assert_eq!(
        problems,
        [
            &Problem::RoleSet(RoleSetError::MissingWeight {
                role: id("role:jungle"),
                attribute: esports::moba::attributes::OverallAttribute::Composure
            }),
            &Problem::RoleSet(RoleSetError::ZeroWeights(id("role:support"))),
        ]
    );
}

#[test]
fn a_roster_pinned_into_a_corner_is_a_package_error() {
    // spec: GEN-020
    // Given
    let mut fixture = Fixture::new();
    let players: Vec<Value> = ["top", "top", "mid", "mid", "bot", "bot"]
        .iter()
        .enumerate()
        .map(|(n, role)| json!({"id": format!("player:p{n}"), "team": "team:a", "role": format!("role:{role}")}))
        .collect();
    fixture.set("players/a.json", Value::Array(players));
    // When
    let errors = fixture.errors();
    // Then
    assert_eq!(
        errors,
        [error(
            "teams/a.json",
            "id",
            Problem::IncompletableRoster {
                team: id("team:a"),
                missing_roles: vec![id("role:jungle"), id("role:support")]
            }
        )]
    );
}

#[test]
fn three_pinned_players_in_one_role_cannot_fit() {
    let mut fixture = Fixture::new();
    let players: Vec<Value> = (0..3)
        .map(|n| json!({"id": format!("player:p{n}"), "team": "team:a", "role": "role:mid"}))
        .collect();
    fixture.set("players/a.json", Value::Array(players));
    assert!(matches!(
        fixture.errors()[0].problem,
        Problem::IncompletableRoster { .. }
    ));
}

#[test]
fn a_roster_with_room_left_is_fine() {
    let mut fixture = Fixture::new();
    let players: Vec<Value> = ["top", "top", "mid", "mid", "bot"]
        .iter()
        .enumerate()
        .map(|(n, role)| json!({"id": format!("player:p{n}"), "team": "team:a", "role": format!("role:{role}")}))
        .collect();
    fixture.set("players/a.json", Value::Array(players));
    assert_eq!(
        fixture.load().map(|p| p.template.players.len()).ok(),
        Some(5)
    );
}

#[test]
fn invalid_nationality_mixes_are_package_errors() {
    // spec: GEN-021
    // Given
    let mut fixture = Fixture::new();
    fixture
        .edit("regions/r.json", |region| {
            region["nationalities"] = json!({});
        })
        .set(
            "regions/s.json",
            json!({"id": "region:s", "level": 0, "nationalities": {"nationality:kr": 0}}),
        );
    fixture.text("locales/en/more.ftl", "region-s = S\n");
    // When
    let errors = fixture.errors();
    // Then
    let mixes: Vec<&PackageError> = errors
        .iter()
        .filter(|e| matches!(e.problem, Problem::InvalidMix { .. }))
        .collect();
    assert_eq!(
        mixes,
        [
            &error(
                "regions/r.json",
                "nationalities",
                Problem::InvalidMix {
                    region: id("region:r")
                }
            ),
            &error(
                "regions/s.json",
                "nationalities",
                Problem::InvalidMix {
                    region: id("region:s")
                }
            ),
        ]
    );
}

#[test]
fn every_drawable_nationality_needs_names() {
    // spec: GEN-022
    // Given
    let mut fixture = Fixture::new();
    fixture
        .edit("nationalities/all.json", |all| {
            all.as_array_mut()
                .unwrap()
                .push(json!({"id": "nationality:se", "code": "SE", "name_order": "given_first"}));
        })
        .edit("regions/r.json", |region| region["nationalities"]["nationality:se"] = json!(1))
        .set(
            "name-pools/se.json",
            json!({"id": "name_pool:se", "nationality": "nationality:se", "given": ["Elin"], "family": []}),
        );
    fixture.text("locales/en/more.ftl", "nationality-se = Sweden\n");
    // When
    let errors = fixture.errors();
    // Then
    assert_eq!(
        errors,
        [error(
            "nationalities/all.json",
            "[2].id",
            Problem::EmptyNamePool {
                nationality: id("nationality:se"),
                names: NameKind::Family
            }
        )]
    );
}

#[test]
fn nationalities_no_region_draws_need_no_names() {
    let mut fixture = Fixture::new();
    fixture.edit("nationalities/all.json", |all| {
        all.as_array_mut()
            .unwrap()
            .push(json!({"id": "nationality:se", "code": "SE", "name_order": "given_first"}));
    });
    fixture.text("locales/en/more.ftl", "nationality-se = Sweden\n");
    assert!(fixture.load().is_ok());
}

#[test]
fn too_few_distinct_nicknames_is_a_package_error() {
    // spec: GEN-023
    // Given 18 teams of 7 generated players, and 400 nicknames of which 300
    // differ when case is ignored
    let mut fixture = Fixture::new();
    let mut text = String::new();
    let mut teams = Vec::new();
    for n in 0..18 {
        let slug = format!("t{n}");
        writeln!(text, "team-{slug} = {slug}").unwrap();
        teams.push(team(&slug));
    }
    let nicknames: Vec<String> = (0..300)
        .map(|n| format!("Nick{n}"))
        .chain((0..100).map(|n| format!("NICK{n}")))
        .collect();
    fixture
        .remove("teams/a.json")
        .remove("teams/b.json")
        .set("teams/all.json", Value::Array(teams))
        .edit("competitions/league.json", |league| {
            league["teams"] = json!([]);
        })
        .edit("nicknames/all.json", |pool| {
            pool["nicknames"] = json!(nicknames);
        });
    fixture.text("locales/en/more.ftl", &text);
    // When
    let errors = fixture.errors();
    // Then
    assert_eq!(
        errors,
        [error(
            "nicknames/all.json",
            "",
            Problem::NicknamePoolTooSmall {
                distinct: 300,
                needed: 378
            }
        )]
    );
}

#[test]
fn pinned_nicknames_leave_the_pool_and_their_slots() {
    let mut fixture = Fixture::new();
    // 14 slots, 13 generated after pinning one: 39 needed. 40 entries, one
    // of which is the pinned nickname: 39 left, which is enough.
    let nicknames: Vec<String> = (0..39)
        .map(|n| format!("N{n}"))
        .chain(["Kairos".to_owned()])
        .collect();
    fixture
        .edit("nicknames/all.json", |pool| pool["nicknames"] = json!(nicknames))
        .set(
            "players/kairos.json",
            json!({"id": "player:kairos", "team": "team:a", "role": "role:mid", "nickname": "kairos"}),
        );
    assert!(fixture.load().is_ok());
    fixture.edit("nicknames/all.json", |pool| {
        pool["nicknames"].as_array_mut().unwrap().remove(0);
    });
    assert_eq!(
        fixture.errors()[0].problem,
        Problem::NicknamePoolTooSmall {
            distinct: 38,
            needed: 39
        }
    );
}

#[test]
fn duplicate_pinned_nicknames_are_a_package_error() {
    // spec: GEN-024
    // Given
    let mut fixture = Fixture::new();
    fixture.set(
        "players/both.json",
        json!([
            {"id": "player:kairos", "team": "team:a", "role": "role:mid", "nickname": "Kairos"},
            {"id": "player:other", "team": "team:b", "role": "role:mid", "nickname": "kairos"}
        ]),
    );
    // When
    let errors = fixture.errors();
    // Then
    assert_eq!(
        errors,
        [error(
            "players/both.json",
            "[1].nickname",
            Problem::DuplicateNickname {
                nickname: "kairos".to_owned(),
                player: id("player:other"),
                other: id("player:kairos")
            }
        )]
    );
}

#[test]
fn subs_cannot_exceed_the_roles() {
    let mut fixture = Fixture::new();
    fixture.edit("roles/core.json", |set| set["subs"] = json!(6));
    assert_eq!(
        fixture.errors(),
        [error(
            "roles/core.json",
            "subs",
            Problem::TooManySubs { subs: 6, roles: 5 }
        )]
    );
}

#[test]
fn the_role_set_and_generation_are_required_once() {
    let mut fixture = Fixture::new();
    fixture.remove("roles/core.json");
    let roles = fixture.errors();
    assert!(roles.contains(&error(
        "roles/",
        "",
        Problem::WrongCount {
            folder: "roles/".to_owned(),
            count: 0
        }
    )));
    let mut fixture = Fixture::new();
    let generation = fixture.files["generation/core.json"].clone();
    let mut second = generation;
    second["id"] = json!("generation:other");
    fixture.set("generation/other.json", second);
    assert_eq!(
        fixture.errors(),
        [error(
            "generation/other.json",
            "",
            Problem::WrongCount {
                folder: "generation/".to_owned(),
                count: 2
            }
        )]
    );
}

#[test]
fn manifest_and_world_are_required() {
    let mut fixture = Fixture::new();
    fixture.remove("manifest.json").remove("world.json");
    let errors = fixture.errors();
    assert!(errors.contains(&error("manifest.json", "", Problem::MissingFile)));
    assert!(errors.contains(&error("world.json", "", Problem::MissingFile)));
}

#[test]
fn manifest_fields_are_checked() {
    let mut fixture = Fixture::new();
    fixture.edit("manifest.json", |m| {
        m["id"] = json!("Bad Id");
        m["version"] = json!("1.0");
        m["genre"] = json!("chess");
        m["locales"] = json!([]);
    });
    let paths: Vec<(String, Problem)> = fixture
        .errors()
        .into_iter()
        .filter(|e| e.file == "manifest.json")
        .map(|e| (e.path, e.problem))
        .collect();
    assert_eq!(
        paths,
        [
            (
                "id".to_owned(),
                Problem::InvalidId {
                    id: "Bad Id".to_owned()
                }
            ),
            ("version".to_owned(), Problem::InvalidFormat),
            (
                "genre".to_owned(),
                Problem::UnsupportedGenre {
                    genre: "chess".to_owned()
                }
            ),
            ("locales".to_owned(), Problem::Empty),
        ]
    );
}

#[test]
fn versions_need_three_numbers() {
    for version in ["1.0.0.0", "1..0", "a.b.c", "1.0.x"] {
        let mut fixture = Fixture::new();
        fixture.edit("manifest.json", |m| m["version"] = json!(version));
        assert!(
            fixture.errors().iter().any(|e| e.path == "version"),
            "{version}"
        );
    }
}

#[test]
fn field_formats_and_ranges_are_checked() {
    let mut fixture = Fixture::new();
    fixture
        .edit("teams/a.json", |team| {
            team["tag"] = json!("az");
            team["colours"] = json!(["blue", "#FFFFFF"]);
            team["reputation"] = json!(0);
        })
        .edit("world.json", |world| {
            world["start_date"] = json!("2027-02-30");
        })
        .edit("nationalities/all.json", |all| {
            all[0]["code"] = json!("KOR");
        })
        .set(
            "players/p.json",
            json!({"id": "player:p", "team": "team:a", "role": "role:mid",
                   "birth_date": "1997/03/14", "attributes": {"mechanics": 100, "potential": 0}}),
        );
    let found: Vec<(String, String, Problem)> = fixture
        .errors()
        .into_iter()
        .map(|e| (e.file, e.path, e.problem))
        .collect();
    let expected = [
        ("nationalities/all.json", "[0].code", Problem::InvalidFormat),
        ("players/p.json", "birth_date", Problem::InvalidFormat),
        (
            "players/p.json",
            "attributes.mechanics",
            Problem::OutOfRange,
        ),
        (
            "players/p.json",
            "attributes.potential",
            Problem::OutOfRange,
        ),
        ("teams/a.json", "tag", Problem::InvalidFormat),
        ("teams/a.json", "colours[0]", Problem::InvalidFormat),
        ("teams/a.json", "reputation", Problem::OutOfRange),
        ("world.json", "start_date", Problem::InvalidFormat),
    ];
    for (file, path, problem) in expected {
        assert!(
            found.contains(&(file.to_owned(), path.to_owned(), problem.clone())),
            "{file} {path} {problem:?} in {found:?}"
        );
    }
}

#[test]
fn malformed_ids_and_references_are_errors() {
    let mut fixture = Fixture::new();
    fixture
        .edit("teams/a.json", |team| {
            team["id"] = json!("team:A");
            team["region"] = json!("nowhere");
        })
        .edit("roles/core.json", |set| {
            set["roles"][0]["id"] = json!("team:top");
        });
    let found: Vec<(String, Problem)> = fixture
        .errors()
        .into_iter()
        .map(|e| (e.path, e.problem))
        .collect();
    assert!(found.contains(&(
        "id".to_owned(),
        Problem::InvalidId {
            id: "team:A".to_owned()
        }
    )));
    assert!(found.contains(&(
        "region".to_owned(),
        Problem::InvalidId {
            id: "nowhere".to_owned()
        }
    )));
    assert!(found.contains(&(
        "roles[0].id".to_owned(),
        Problem::WrongKind {
            id: id("team:top"),
            expected: "role".to_owned()
        }
    )));
}

#[test]
fn every_reference_is_checked() {
    let mut fixture = Fixture::new();
    fixture
        .edit("regions/r.json", |r| r["nationalities"]["nationality:xx"] = json!(1))
        .edit("name-pools/br.json", |p| p["nationality"] = json!("nationality:yy"))
        .edit("competitions/league.json", |c| c["teams"] = json!(["team:a", "team:zz"]))
        .set(
            "players/p.json",
            json!({"id": "player:p", "team": "team:qq", "role": "role:coach", "nationality": "nationality:ww"}),
        );
    let found: Vec<(String, String)> = fixture
        .errors()
        .into_iter()
        .filter_map(|e| {
            if let Problem::UnresolvedReference { field, id } = e.problem {
                Some((field, id))
            } else {
                None
            }
        })
        .collect();
    for expected in [
        ("teams[1]", "team:zz"),
        ("nationality", "nationality:yy"),
        ("team", "team:qq"),
        ("role", "role:coach"),
        ("nationality", "nationality:ww"),
        ("nationalities.nationality:xx", "nationality:xx"),
    ] {
        assert!(
            found.contains(&(expected.0.to_owned(), expected.1.to_owned())),
            "{expected:?} in {found:?}"
        );
    }
}

#[test]
fn generation_constants_are_checked() {
    let mut fixture = Fixture::new();
    fixture.edit("generation/core.json", |g| {
        g["attribute_spread"] = json!(-1.0);
        g["age_min"] = json!(30);
    });
    let paths: Vec<String> = fixture.errors().into_iter().map(|e| e.path).collect();
    assert_eq!(paths, ["attribute_spread", "age_min"]);
}

#[test]
fn nickname_pools_merge_without_repeats() {
    let mut fixture = Fixture::new();
    fixture.set(
        "nicknames/more.json",
        json!({"id": "nickname_pool:more", "nicknames": ["nick00", "Fresh"]}),
    );
    let package = fixture.load().unwrap();
    assert_eq!(package.template.nicknames.len(), 101);
    assert_eq!(
        package.template.nicknames.last().map(String::as_str),
        Some("Fresh")
    );
}

#[test]
fn pinned_players_convert_every_field() {
    let mut fixture = Fixture::new();
    fixture.set(
        "players/kairos.json",
        json!({"id": "player:kairos", "team": "team:a", "role": "role:mid", "nickname": "Kairos",
               "given_name": "Do-yun", "family_name": "Han", "nationality": "nationality:kr",
               "birth_date": "1997-03-14",
               "attributes": {"mechanics": 95, "laning": 1, "game_sense": 2, "awareness": 3, "positioning": 4,
                              "champion_pool_breadth": 5, "shotcalling": 6, "teamwork": 7, "aggression": 8,
                              "composure": 9, "work_ethic": 10, "consistency": 11, "potential": 12}}),
    );
    let package = fixture.load().unwrap();
    let kairos = &package.template.players[0];
    assert_eq!(kairos.nickname.as_deref(), Some("Kairos"));
    assert_eq!(kairos.given_name.as_deref(), Some("Do-yun"));
    assert_eq!(kairos.family_name.as_deref(), Some("Han"));
    assert_eq!(kairos.nationality, Some(id("nationality:kr")));
    assert_eq!(
        kairos.birth_date.map(|d| d.to_string()),
        Some("1997-03-14".to_owned())
    );
    let a = kairos.attributes;
    let shown: Vec<Option<u8>> = [
        a.mechanics,
        a.laning,
        a.game_sense,
        a.awareness,
        a.positioning,
        a.champion_pool_breadth,
        a.shotcalling,
        a.teamwork,
        a.aggression,
        a.composure,
        a.work_ethic,
        a.consistency,
        a.potential,
    ]
    .iter()
    .map(|r| r.map(domain::rating::Rating::display))
    .collect();
    assert_eq!(shown, [95, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map(Some));
}

#[test]
fn weight_keys_map_to_their_attributes() {
    use esports::moba::attributes::OverallAttribute;
    let package = Fixture::new().load().unwrap();
    let mid = package.template.roles.get(&id("role:mid")).unwrap();
    let weights: Vec<u32> = OverallAttribute::ALL
        .iter()
        .map(|&a| mid.weight(a))
        .collect();
    assert_eq!(weights, [20, 16, 14, 10, 12, 8, 6, 6, 8]);
}

#[test]
fn licence_files_at_the_root_are_unexpected() {
    // ADR 0011: a package's licence is its manifest's `license` field.
    let fixture = Fixture::new();
    let mut files = fixture.files();
    for file in ["LICENSE", "REUSE.toml", "manifest.json.license"] {
        files.insert(file, "GPL-3.0-or-later");
    }
    let errors = load_files(&files).unwrap_err();
    for file in ["LICENSE", "REUSE.toml", "manifest.json.license"] {
        assert!(
            errors.contains(&error(file, "", Problem::UnexpectedFile)),
            "{errors:?}"
        );
    }
}

#[test]
fn an_unreadable_root_is_reported() {
    let errors = load(std::path::Path::new("/definitely/not/here")).unwrap_err();
    assert!(matches!(errors[0].problem, Problem::Unreadable { .. }));
}

#[test]
fn the_core_package_loads_with_no_errors() {
    // spec: PKG-001
    // Given
    let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../content/core");
    // When
    let package = load(&root);
    // Then
    let package = package.unwrap();
    assert_eq!(package.manifest.id, "core");
    assert_eq!(package.template.regions.len(), 2);
    assert_eq!(package.template.competitions.len(), 2);
    assert_eq!(package.template.teams.len(), 18);
    assert_eq!(package.template.nationalities.len(), 11);
    assert_eq!(package.template.players.len(), 4);
}

#[test]
fn package_ids_may_hold_digits_and_underscores() {
    let mut fixture = Fixture::new();
    fixture.edit("manifest.json", |m| m["id"] = json!("core_2"));
    assert_eq!(
        fixture.load().map(|p| p.manifest.id).ok().as_deref(),
        Some("core_2")
    );
}

#[test]
fn spreads_may_be_zero() {
    let mut fixture = Fixture::new();
    fixture.edit("generation/core.json", |g| {
        g["attribute_spread"] = json!(0.0);
        g["age_min"] = json!(22);
        g["age_max"] = json!(22);
    });
    assert!(fixture.load().is_ok());
}

#[test]
fn a_nationality_with_zero_weight_is_not_drawable() {
    let mut fixture = Fixture::new();
    fixture
        .edit("nationalities/all.json", |all| {
            all.as_array_mut()
                .unwrap()
                .push(json!({"id": "nationality:se", "code": "SE", "name_order": "given_first"}));
        })
        .edit("regions/r.json", |region| {
            region["nationalities"]["nationality:se"] = json!(0);
        });
    fixture.text("locales/en/more.ftl", "nationality-se = Sweden\n");
    assert!(fixture.load().is_ok());
}

#[test]
fn names_may_be_split_across_pools() {
    let mut fixture = Fixture::new();
    fixture.set(
        "name-pools/kr-more.json",
        json!({"id": "name_pool:kr_more", "nationality": "nationality:kr", "given": ["Seo-jun"], "family": ["Kim"]}),
    );
    assert_eq!(
        fixture.load().map(|p| p.template.name_pools.len()).ok(),
        Some(3)
    );
}

#[test]
fn subs_may_equal_the_roles() {
    let mut fixture = Fixture::new();
    fixture.edit("roles/core.json", |set| set["subs"] = json!(5));
    assert_eq!(fixture.load().map(|p| p.template.roster.subs).ok(), Some(5));
}

#[test]
fn pinned_players_only_free_their_own_team_slots() {
    // Three teams of 7: 21 places, and the pinned player has no nickname,
    // so all 21 draw one: 63 needed.
    let mut fixture = Fixture::new();
    let nicknames: Vec<String> = (0..59).map(|n| format!("N{n}")).collect();
    fixture
        .set("teams/c.json", team("c"))
        .edit("nicknames/all.json", |pool| {
            pool["nicknames"] = json!(nicknames);
        })
        .set(
            "players/p.json",
            json!({"id": "player:p", "team": "team:a", "role": "role:mid"}),
        );
    fixture.text("locales/en/more.ftl", "team-c = C\n");
    assert_eq!(
        fixture.errors(),
        [error(
            "nicknames/all.json",
            "",
            Problem::NicknamePoolTooSmall {
                distinct: 59,
                needed: 63
            }
        )]
    );
}

#[test]
fn a_broken_unicode_escape_is_a_syntax_error_not_a_crash() {
    let mut fixture = Fixture::new();
    fixture.text("locales/pt-BR/broken.ftl", "a = ok\nb = { \"\\u00é\" }\n");
    assert_eq!(
        fixture.errors(),
        [error(
            "locales/pt-BR/broken.ftl",
            "",
            Problem::TextSyntax { line: 2 }
        )]
    );
}

#[test]
fn a_broken_long_unicode_escape_is_a_syntax_error_too() {
    let mut fixture = Fixture::new();
    fixture.text("locales/pt-BR/broken.ftl", "a = { \"\\U0001é\" }\n");
    assert_eq!(
        fixture.errors(),
        [error(
            "locales/pt-BR/broken.ftl",
            "",
            Problem::TextSyntax { line: 1 }
        )]
    );
}

#[test]
fn a_map_field_that_is_not_an_object_says_what_it_expects() {
    let fixture = Fixture::new();
    let mut files = fixture.files();
    files.insert(
        "regions/r.json",
        r#"{"id": "region:r", "level": 0, "nationalities": 5}"#,
    );
    let detail = load_files(&files)
        .unwrap_err()
        .into_iter()
        .filter(|e| e.file == "regions/r.json")
        .find_map(|e| {
            if let Problem::InvalidValue { detail } = e.problem {
                Some(detail)
            } else {
                None
            }
        })
        .unwrap();
    assert!(detail.contains("expected an object"), "{detail}");
}

#[test]
fn a_repeated_key_is_an_error_in_maps_too() {
    let fixture = Fixture::new();
    let mut files = fixture.files();
    files.insert(
        "regions/r.json",
        r#"{"id": "region:r", "level": 0, "nationalities": {"nationality:kr": 1, "nationality:kr": 2}}"#,
    );
    let found: Vec<(String, Problem)> = load_files(&files)
        .unwrap_err()
        .into_iter()
        .map(|e| (e.file, e.problem))
        .collect();
    assert!(
        found.contains(&(
            "regions/r.json".to_owned(),
            Problem::DuplicateField {
                field: "nationality:kr".to_owned()
            }
        )),
        "{found:?}"
    );
}

#[test]
fn a_repeated_key_is_an_error_in_objects_and_lists() {
    let mut fixture = Fixture::new();
    let mut files = fixture.files();
    files.insert(
        "teams/a.json",
        r##"{"id": "team:a", "region": "region:r", "tag": "AAA", "colours": ["#000000", "#FFFFFF"], "reputation": 50, "id": "team:zz"}"##,
    );
    files.insert(
        "players/two.json",
        r#"[{"id": "player:p", "team": "team:a", "role": "role:mid"}, {"id": "player:q", "team": "team:a", "role": "role:mid", "role": "role:top"}]"#,
    );
    let found: Vec<(String, String, Problem)> = load_files(&files)
        .unwrap_err()
        .into_iter()
        .map(|e| (e.file, e.path, e.problem))
        .collect();
    assert!(
        found.contains(&(
            "teams/a.json".to_owned(),
            String::new(),
            Problem::DuplicateField {
                field: "id".to_owned()
            }
        )),
        "{found:?}"
    );
    assert!(
        found.contains(&(
            "players/two.json".to_owned(),
            "[1]".to_owned(),
            Problem::DuplicateField {
                field: "role".to_owned()
            }
        )),
        "{found:?}"
    );
    let _ = fixture.remove("teams/a.json");
}

#[test]
fn a_byte_order_mark_is_accepted_and_other_encodings_are_reported() {
    let fixture = Fixture::new();
    let mut files = fixture.files();
    let team = team("a").to_string();
    files.insert("teams/a.json", format!("\u{feff}{team}"));
    let text = format!("\u{feff}{}", fixture.texts["locales/en/names.ftl"]);
    files.insert("locales/en/names.ftl", text);
    let package = load_files(&files).unwrap();
    assert!(
        package
            .texts
            .iter()
            .all(|text| !text.source.starts_with('\u{feff}'))
    );
    files.insert("teams/a.json", vec![0xff, 0xfe, b'{', b'}']);
    assert!(
        load_files(&files)
            .unwrap_err()
            .contains(&error("teams/a.json", "", Problem::NotUtf8))
    );
}

#[test]
fn one_broken_entity_causes_no_cascade() {
    let mut fixture = Fixture::new();
    fixture.edit("regions/r.json", |region| {
        region["nationalities"]["Nationality:KR"] = json!(1);
    });
    let errors = fixture.errors();
    assert_eq!(
        errors,
        [error(
            "regions/r.json",
            "nationalities.Nationality:KR",
            Problem::InvalidId {
                id: "Nationality:KR".to_owned()
            }
        )]
    );
}

#[test]
fn a_broken_manifest_is_not_reported_missing() {
    let mut fixture = Fixture::new();
    let mut files = fixture.files();
    files.insert("manifest.json", "{ not json");
    let errors = load_files(&files).unwrap_err();
    assert!(
        !errors.iter().any(|e| e.problem == Problem::MissingFile),
        "{errors:?}"
    );
    assert!(matches!(errors[0].problem, Problem::Syntax { .. }));
    let _ = fixture.remove("world.json");
}

#[test]
fn a_manifest_with_one_mistake_still_has_its_text_checked() {
    let mut fixture = Fixture::new();
    fixture.edit("manifest.json", |m| m["version"] = json!("1.0"));
    let en = fixture.texts["locales/en/names.ftl"].replace("team-b = team-b\n", "");
    fixture.text("locales/en/names.ftl", &en);
    let problems: Vec<Problem> = fixture.errors().into_iter().map(|e| e.problem).collect();
    assert!(problems.contains(&Problem::InvalidFormat));
    assert!(problems.contains(&Problem::MissingText {
        message: "team-b".to_owned(),
        locale: "en".to_owned()
    }));
}

#[test]
fn too_many_subs_does_not_hide_duplicate_nicknames() {
    let mut fixture = Fixture::new();
    fixture
        .edit("roles/core.json", |set| set["subs"] = json!(6))
        .set(
            "players/both.json",
            json!([
                {"id": "player:a", "team": "team:a", "role": "role:mid", "nickname": "Same"},
                {"id": "player:b", "team": "team:b", "role": "role:mid", "nickname": "same"}
            ]),
        );
    let problems: Vec<Problem> = fixture.errors().into_iter().map(|e| e.problem).collect();
    assert!(
        problems
            .iter()
            .any(|p| matches!(p, Problem::TooManySubs { .. }))
    );
    assert!(
        problems
            .iter()
            .any(|p| matches!(p, Problem::DuplicateNickname { .. }))
    );
}

#[test]
fn a_role_set_without_roles_is_an_empty_role_set() {
    let mut fixture = Fixture::new();
    fixture.edit("roles/core.json", |set| set["roles"] = json!([]));
    let problems: Vec<Problem> = fixture.errors().into_iter().map(|e| e.problem).collect();
    assert!(
        problems.contains(&Problem::RoleSet(RoleSetError::Empty)),
        "{problems:?}"
    );
}

#[test]
fn invalid_role_ids_are_not_also_an_empty_role_set() {
    let mut fixture = Fixture::new();
    fixture.edit("roles/core.json", |set| {
        for role in set["roles"].as_array_mut().unwrap() {
            role["id"] = json!("Bad Id");
        }
    });
    let problems: Vec<Problem> = fixture.errors().into_iter().map(|e| e.problem).collect();
    assert!(
        !problems.contains(&Problem::RoleSet(RoleSetError::Empty)),
        "{problems:?}"
    );
    assert!(
        problems
            .iter()
            .all(|p| matches!(p, Problem::InvalidId { .. })),
        "{problems:?}"
    );
}

#[test]
fn a_pinned_nationality_needs_names() {
    let mut fixture = Fixture::new();
    fixture
        .edit("nationalities/all.json", |all| {
            all.as_array_mut()
                .unwrap()
                .push(json!({"id": "nationality:jp", "code": "JP", "name_order": "family_first"}));
        })
        .set(
            "players/p.json",
            json!({"id": "player:p", "team": "team:a", "role": "role:mid", "nationality": "nationality:jp", "given_name": "Taro"}),
        );
    fixture.text("locales/en/more.ftl", "nationality-jp = Japan\n");
    let problems: Vec<Problem> = fixture.errors().into_iter().map(|e| e.problem).collect();
    assert!(
        problems.contains(&Problem::EmptyNamePool {
            nationality: id("nationality:jp"),
            names: NameKind::Family
        }),
        "{problems:?}"
    );
    // Pinning both names still needs the pools: the generator draws them
    // anyway, so pinning never shifts another draw.
    fixture.edit("players/p.json", |p| p["family_name"] = json!("Sato"));
    let problems: Vec<Problem> = fixture.errors().into_iter().map(|e| e.problem).collect();
    assert!(
        problems.contains(&Problem::EmptyNamePool {
            nationality: id("nationality:jp"),
            names: NameKind::Given
        }),
        "{problems:?}"
    );
    // With pools, the package loads, and what loads generates.
    fixture.set(
        "name-pools/jp.json",
        json!({"id": "name_pool:jp", "nationality": "nationality:jp", "given": ["Ren"], "family": ["Ito"]}),
    );
    let package = fixture.load().unwrap();
    let world = esports::moba::generation::generate(
        package.template,
        &app::rng::RngProvider::new(domain::rng::WorldSeed::new(1)),
    )
    .unwrap();
    let pinned = world
        .players
        .iter()
        .find(|p| p.id == id("player:p"))
        .unwrap();
    assert_eq!(
        (pinned.given_name.as_str(), pinned.family_name.as_str()),
        ("Taro", "Sato")
    );
}

#[test]
fn a_nickname_factor_of_zero_is_out_of_range() {
    let mut fixture = Fixture::new();
    fixture.edit("generation/core.json", |g| {
        g["nickname_pool_factor"] = json!(0);
    });
    assert_eq!(
        fixture.errors(),
        [error(
            "generation/core.json",
            "nickname_pool_factor",
            Problem::OutOfRange
        )]
    );
}

#[test]
fn a_pinned_birth_date_after_the_start_is_out_of_range() {
    let mut fixture = Fixture::new();
    fixture.set(
        "players/p.json",
        json!({"id": "player:p", "team": "team:a", "role": "role:mid", "birth_date": "2030-01-01"}),
    );
    assert_eq!(
        fixture.errors(),
        [error("players/p.json", "birth_date", Problem::OutOfRange)]
    );
    fixture.edit("players/p.json", |p| p["birth_date"] = json!("2027-01-01"));
    assert!(fixture.load().is_ok());
}

#[cfg(unix)]
#[test]
fn unreadable_files_are_reported_by_path_and_links_are_followed() {
    use std::os::unix::fs::PermissionsExt;
    let root = std::env::temp_dir().join(format!("esm-unreadable-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&root);
    std::fs::create_dir_all(root.join("teams")).unwrap();
    let elsewhere = root.with_extension("players");
    std::fs::create_dir_all(&elsewhere).unwrap();
    std::fs::write(root.join("teams/secret.json"), "{}").unwrap();
    std::fs::set_permissions(
        root.join("teams/secret.json"),
        std::fs::Permissions::from_mode(0o000),
    )
    .unwrap();
    std::os::unix::fs::symlink(&elsewhere, root.join("players")).unwrap();
    std::fs::write(elsewhere.join("p.json"), "{}").unwrap();
    let (files, unreadable) = PackageFiles::read_dir_reporting(&root).unwrap();
    let paths: Vec<&str> = unreadable.iter().map(|(path, _)| path.as_str()).collect();
    // Root can read anything, so only check the link when running as root.
    if !paths.is_empty() {
        assert_eq!(paths, ["teams/secret.json"]);
    }
    assert!(files.iter().any(|(path, _)| path == "players/p.json"));
    let errors = load(&root).unwrap_err();
    if !paths.is_empty() {
        assert_eq!(errors[0].file, "teams/secret.json");
    }
    std::fs::set_permissions(
        root.join("teams/secret.json"),
        std::fs::Permissions::from_mode(0o644),
    )
    .unwrap();
    std::fs::remove_dir_all(&root).unwrap();
    std::fs::remove_dir_all(&elsewhere).unwrap();
}

#[test]
fn schema_pointers_load_on_single_objects() {
    // spec: PKG-013
    // Given
    let mut fixture = Fixture::new();
    fixture.edit("teams/a.json", |team| {
        team["$schema"] = json!("../schemas/team.schema.json");
    });
    // When
    let package = fixture.load();
    // Then
    assert_eq!(package.map(|p| p.template.teams.len()).ok(), Some(2));
}
