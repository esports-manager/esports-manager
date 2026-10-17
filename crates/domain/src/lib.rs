// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! Genre-agnostic core of eSports Manager.
//!
//! Pure Rust: no IO, no wall-clock, no global randomness (ADR 0001, ADR 0003).
//! Concepts specific to one esport belong in the `esports` crate (ADR 0002).

pub mod attributes;
pub mod date;
pub mod generation;
pub mod id;
pub mod random;
pub mod rating;
pub mod rng;
pub mod world;
