// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! Application layer: use cases, ports and view DTOs (ADR 0001).
//!
//! Adapters (the CLI, the desktop app) call use cases here and nothing else.

mod about;
pub mod content;
pub mod game;
pub mod locations;
pub mod messages;
pub mod rng;
pub mod saves;
pub mod views;

pub use about::{About, about};
