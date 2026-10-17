// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! `schema.rs` must match the migrations (ADR 0004). Diesel's CLI writes it
//! (`just db-schema`); this test compares the committed copy with a database
//! migrated from scratch, so CI needs no CLI. It compares each table's
//! columns and types, its primary key, and the foreign keys Diesel records
//! as `joinable!`.

use std::collections::{BTreeMap, BTreeSet};

use diesel::prelude::*;
use diesel::sqlite::SqliteConnection;
use diesel_migrations::MigrationHarness;

use crate::store::MIGRATIONS;

/// One table as both sides describe it.
#[derive(Debug, Default, PartialEq, Eq)]
struct Table {
    /// `(name, Diesel type)`, in order.
    columns: Vec<(String, String)>,
    primary_key: Vec<String>,
}

#[derive(Debug, Default, PartialEq, Eq)]
struct Schema {
    tables: BTreeMap<String, Table>,
    /// `(table, column, referenced table)`.
    foreign_keys: BTreeSet<(String, String, String)>,
}

/// Reads the `diesel::table!` blocks and `joinable!` lines of `schema.rs`.
fn committed(source: &str) -> Schema {
    let mut schema = Schema::default();
    let mut current: Option<String> = None;
    for line in source.lines() {
        let trimmed = line.trim();
        if let Some(name) = current.as_ref() {
            if trimmed == "}" {
                current = None;
            } else if let Some((column, kind)) = trimmed.split_once(" -> ") {
                let table = schema.tables.entry(name.clone()).or_default();
                table
                    .columns
                    .push((column.to_owned(), kind.trim_end_matches(',').to_owned()));
            }
        } else if let Some(rest) = trimmed.strip_prefix("diesel::joinable!(") {
            // joinable!(child -> parent (column));
            let rest = rest.trim_end_matches(");");
            if let Some((child, rest)) = rest.split_once(" -> ")
                && let Some((parent, column)) = rest.split_once(" (")
            {
                schema.foreign_keys.insert((
                    child.to_owned(),
                    column.trim_end_matches(')').to_owned(),
                    parent.to_owned(),
                ));
            }
        } else if line.starts_with("    ")
            && trimmed.ends_with('{')
            && !trimmed.starts_with("diesel")
        {
            // name (key, key) {
            let (name, keys) = trimmed.split_once(" (").unwrap_or((trimmed, ""));
            let keys = keys.split_once(')').map_or("", |(keys, _)| keys);
            schema
                .tables
                .entry(name.to_owned())
                .or_default()
                .primary_key = keys.split(", ").map(str::to_owned).collect();
            current = Some(name.to_owned());
        }
    }
    schema
}

#[derive(QueryableByName)]
struct Column {
    #[diesel(sql_type = diesel::sql_types::Text)]
    name: String,
    #[diesel(sql_type = diesel::sql_types::Text)]
    #[diesel(column_name = type_)]
    kind: String,
    #[diesel(sql_type = diesel::sql_types::Integer)]
    notnull: i32,
    #[diesel(sql_type = diesel::sql_types::Integer)]
    pk: i32,
}

#[derive(QueryableByName)]
struct TableName {
    #[diesel(sql_type = diesel::sql_types::Text)]
    name: String,
}

#[derive(QueryableByName)]
struct ForeignKey {
    #[diesel(sql_type = diesel::sql_types::Text)]
    #[diesel(column_name = table_)]
    parent: String,
    #[diesel(sql_type = diesel::sql_types::Text)]
    #[diesel(column_name = from_)]
    column: String,
}

/// The schema of a database migrated from nothing, with SQL types mapped as
/// Diesel's CLI maps them for SQLite.
fn migrated() -> Schema {
    let mut connection = SqliteConnection::establish(":memory:").unwrap();
    connection.run_pending_migrations(MIGRATIONS).unwrap();
    let names: Vec<TableName> = diesel::sql_query(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' \
         AND name != '__diesel_schema_migrations' ORDER BY name",
    )
    .load(&mut connection)
    .unwrap();
    let mut schema = Schema::default();
    for TableName { name } in names {
        let mut columns: Vec<Column> = diesel::sql_query(format!(
            "SELECT name, type AS type_, \"notnull\", pk FROM pragma_table_info('{name}') ORDER BY cid"
        ))
        .load(&mut connection)
        .unwrap();
        let mut table = Table::default();
        for column in &columns {
            let kind = match column.kind.as_str() {
                "INTEGER" => "Integer",
                "BIGINT" => "BigInt",
                "TEXT" => "Text",
                "BLOB" => "Binary",
                "BOOLEAN" => "Bool",
                other => panic!("no Diesel mapping for SQL type {other}"),
            };
            let kind = if column.notnull == 1 {
                kind.to_owned()
            } else {
                format!("Nullable<{kind}>")
            };
            table.columns.push((column.name.clone(), kind));
        }
        columns.retain(|column| column.pk > 0);
        columns.sort_by_key(|column| column.pk);
        table.primary_key = columns.into_iter().map(|column| column.name).collect();
        let keys: Vec<ForeignKey> = diesel::sql_query(format!(
            "SELECT \"table\" AS table_, \"from\" AS from_ FROM pragma_foreign_key_list('{name}') \
             ORDER BY id, seq"
        ))
        .load(&mut connection)
        .unwrap();
        for key in keys {
            schema
                .foreign_keys
                .insert((name.clone(), key.column, key.parent));
        }
        schema.tables.insert(name, table);
    }
    schema
}

#[test]
fn schema_rs_matches_the_migrations() {
    let source = include_str!("schema.rs");
    assert_eq!(
        committed(source),
        migrated(),
        "crates/db/src/schema.rs is out of date; run `just db-schema` and commit the result"
    );
}

#[test]
fn the_reader_understands_tables_keys_and_joins() {
    let source = "diesel::table! {\n    a (id, n) {\n        id -> Text,\n        n -> Nullable<Integer>,\n    }\n}\n\
                  diesel::joinable!(a -> b (id));\n";
    let schema = committed(source);
    assert_eq!(
        schema.tables["a"].columns,
        [
            ("id".to_owned(), "Text".to_owned()),
            ("n".to_owned(), "Nullable<Integer>".to_owned())
        ]
    );
    assert_eq!(schema.tables["a"].primary_key, ["id", "n"]);
    assert_eq!(
        schema.foreign_keys,
        BTreeSet::from([("a".to_owned(), "id".to_owned(), "b".to_owned())])
    );
}
