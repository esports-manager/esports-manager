// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! SQLite adapter (ADR 0004): one file per save, implementing the
//! application's save port. Diesel types never leave this crate (ADR 0001).

#[cfg(test)]
mod drift;
pub mod environment;
mod rows;
mod schema;
mod slug;
mod store;

pub use store::{EXTENSION, SqliteSave, SqliteSaveStore};
