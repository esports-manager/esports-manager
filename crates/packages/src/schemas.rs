// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! JSON Schemas for package files, generated from [`defs`](crate::defs)
//! (ADR 0005). The committed copies live in `content/schemas/`.

use schemars::{JsonSchema, schema_for};

use crate::defs::{
    CompetitionDef, GenerationDef, ManifestDef, NamePoolDef, NationalityDef, NicknamePoolDef,
    OneOrMany, PlayerDef, RegionDef, RoleSetDef, TeamDef, WorldDef,
};

/// Every schema, as `(file name, JSON text)`, in file-name order.
#[must_use]
pub fn all() -> Vec<(&'static str, String)> {
    vec![
        ("competition.schema.json", content::<CompetitionDef>()),
        ("generation.schema.json", content::<GenerationDef>()),
        ("manifest.schema.json", render(&schema_for!(ManifestDef))),
        ("name-pool.schema.json", content::<NamePoolDef>()),
        ("nationality.schema.json", content::<NationalityDef>()),
        ("nickname-pool.schema.json", content::<NicknamePoolDef>()),
        ("player.schema.json", content::<PlayerDef>()),
        ("region.schema.json", content::<RegionDef>()),
        ("role-set.schema.json", content::<RoleSetDef>()),
        ("team.schema.json", content::<TeamDef>()),
        ("world.schema.json", render(&schema_for!(WorldDef))),
    ]
}

/// The pattern every content id follows: `<kind>:<slug>`.
const ID_PATTERN: &str = "^[a-z_]+:[a-z0-9_]+$";

/// A content file holds one entity or a list of them. The schema is titled
/// and described after the entity, which is what editors show.
fn content<T: JsonSchema>() -> String {
    let mut schema = serde_json::to_value(schema_for!(OneOrMany<T>)).unwrap_or_default();
    let name = T::schema_name();
    let description = schema["$defs"][name.as_ref()]["description"].clone();
    schema["title"] = serde_json::Value::String(name.into_owned());
    schema["description"] = description;
    if let Some(defs) = schema["$defs"].as_object_mut() {
        for definition in defs.values_mut() {
            if let Some(id) = definition.pointer_mut("/properties/id")
                && id["type"] == "string"
            {
                id["pattern"] = serde_json::Value::String(ID_PATTERN.to_owned());
            }
        }
    }
    let mut text = serde_json::to_string_pretty(&schema).unwrap_or_default();
    text.push('\n');
    text
}

fn render(schema: &schemars::Schema) -> String {
    let mut text = serde_json::to_string_pretty(schema).unwrap_or_default();
    text.push('\n');
    text
}

#[cfg(test)]
mod tests {
    use std::path::Path;

    /// The committed schemas must match the types (ADR 0005). Set
    /// `UPDATE_SCHEMAS=1` to rewrite them (`just schemas`).
    #[test]
    fn json_schemas_are_up_to_date() {
        let dir = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../content/schemas");
        let update = std::env::var_os("UPDATE_SCHEMAS").is_some();
        if update {
            std::fs::create_dir_all(&dir).unwrap();
        }
        let mut stale = Vec::new();
        for (name, generated) in super::all() {
            let path = dir.join(name);
            if update {
                std::fs::write(&path, &generated).unwrap();
            }
            if std::fs::read_to_string(&path).unwrap_or_default() != generated {
                stale.push(name);
            }
        }
        let committed: Vec<String> = std::fs::read_dir(&dir)
            .map(|entries| {
                entries
                    .filter_map(Result::ok)
                    .map(|entry| entry.file_name().to_string_lossy().into_owned())
                    .collect()
            })
            .unwrap_or_default();
        let expected: Vec<&str> = super::all().into_iter().map(|(name, _)| name).collect();
        let extra: Vec<&String> = committed
            .iter()
            .filter(|name| !expected.contains(&name.as_str()))
            .collect();
        assert!(
            stale.is_empty() && extra.is_empty(),
            "content/schemas is out of date (stale: {stale:?}, extra: {extra:?}); run `just schemas` and commit the result"
        );
    }

    #[test]
    fn content_schemas_are_titled_after_their_entity() {
        for (name, text) in super::all() {
            let value: serde_json::Value = serde_json::from_str(&text).unwrap();
            assert_ne!(value["title"], "OneOrMany", "{name}");
        }
        let team: serde_json::Value =
            serde_json::from_str(&super::content::<crate::defs::TeamDef>()).unwrap();
        assert_eq!(team["title"], "TeamDef");
        assert_eq!(team["description"], "A team, in `teams/`.");
        assert_eq!(
            team["$defs"]["TeamDef"]["properties"]["id"]["pattern"],
            super::ID_PATTERN
        );
    }

    #[test]
    fn every_schema_is_valid_json() {
        for (name, text) in super::all() {
            let value: serde_json::Value = serde_json::from_str(&text).unwrap();
            assert!(value.is_object(), "{name}");
        }
    }
}
