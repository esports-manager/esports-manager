// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! Genre modules of eSports Manager (ADR 0002).
//!
//! Each esport gets one module here. Only the MOBA exists for now.

mod genre;
pub mod moba;

pub use genre::{Genre, UnknownGenre};
