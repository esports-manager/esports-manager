// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! Seed material for deterministic random streams (ADR 0003).
//!
//! A world has one [`WorldSeed`]. Each consumer of randomness derives its own
//! stream from that seed and a stable [`StreamLabel`], so adding a consumer
//! never shifts the sequence another consumer sees. This module only derives
//! seed material; building the generator is the application layer's job.

/// The seed a world is created with. It is stored in the save.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub struct WorldSeed(u64);

impl WorldSeed {
    #[must_use]
    pub const fn new(value: u64) -> Self {
        Self(value)
    }

    #[must_use]
    pub const fn value(self) -> u64 {
        self.0
    }
}

/// The stable name of a random stream, such as `match:42` or `generator:season:3`.
///
/// Labels are part of the save format: renaming one changes every value its
/// stream produces.
#[derive(Debug, Clone, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub struct StreamLabel(String);

impl StreamLabel {
    #[must_use]
    pub fn new(label: impl Into<String>) -> Self {
        Self(label.into())
    }

    #[must_use]
    pub fn as_str(&self) -> &str {
        &self.0
    }
}

/// Hands out the random stream for a label. Domain and genre code take one
/// of these and never build a generator themselves; the application layer's
/// RNG provider is the implementation (ADR 0003).
pub trait StreamSource {
    type Stream: rand_core::Rng;

    /// The stream for `label`. Asking twice gives the same sequence.
    fn stream(&self, label: &StreamLabel) -> Self::Stream;
}

/// Length of the seed material: a 256-bit key, as the `ChaCha` family expects.
pub const STREAM_SEED_LEN: usize = 32;

/// Derives the seed material for one stream of a world.
///
/// The derivation is part of the save format. Changing it changes every
/// random outcome of every existing save, so it needs its own ADR.
#[must_use]
pub fn derive_stream_seed(world: WorldSeed, label: &StreamLabel) -> [u8; STREAM_SEED_LEN] {
    let mut state = world.0 ^ fnv1a_64(label.0.as_bytes());
    let mut seed = [0_u8; STREAM_SEED_LEN];
    for chunk in seed.as_chunks_mut::<8>().0 {
        *chunk = splitmix64(&mut state).to_le_bytes();
    }
    seed
}

const FNV_OFFSET_BASIS: u64 = 0xcbf2_9ce4_8422_2325;
const FNV_PRIME: u64 = 0x0000_0100_0000_01b3;

/// 64-bit FNV-1a: a tiny hash whose output is fixed by its definition, unlike
/// `std`'s hashers, which may change between Rust releases.
fn fnv1a_64(bytes: &[u8]) -> u64 {
    bytes.iter().fold(FNV_OFFSET_BASIS, |hash, &byte| {
        (hash ^ u64::from(byte)).wrapping_mul(FNV_PRIME)
    })
}

/// One step of `SplitMix64`, used to expand a 64-bit state into seed material.
fn splitmix64(state: &mut u64) -> u64 {
    *state = state.wrapping_add(0x9e37_79b9_7f4a_7c15);
    let mut z = *state;
    z = (z ^ (z >> 30)).wrapping_mul(0xbf58_476d_1ce4_e5b9);
    z = (z ^ (z >> 27)).wrapping_mul(0x94d0_49bb_1331_11eb);
    z ^ (z >> 31)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn world_seed_keeps_its_value() {
        assert_eq!(WorldSeed::new(42).value(), 42);
    }

    #[test]
    fn stream_label_keeps_its_text() {
        assert_eq!(StreamLabel::new("match:7").as_str(), "match:7");
    }

    #[test]
    fn fnv1a_matches_reference_vectors() {
        assert_eq!(fnv1a_64(b""), 0xcbf2_9ce4_8422_2325);
        assert_eq!(fnv1a_64(b"a"), 0xaf63_dc4c_8601_ec8c);
        assert_eq!(fnv1a_64(b"foobar"), 0x8594_4171_f739_67e8);
    }

    #[test]
    fn splitmix64_matches_reference_sequence() {
        let mut state = 0;
        assert_eq!(splitmix64(&mut state), 0xe220_a839_7b1d_cdaf);
        assert_eq!(splitmix64(&mut state), 0x6e78_9e6a_a1b9_65f4);
    }

    #[test]
    fn same_world_and_label_give_the_same_seed() {
        let label = StreamLabel::new("match:1");
        assert_eq!(
            derive_stream_seed(WorldSeed::new(42), &label),
            derive_stream_seed(WorldSeed::new(42), &label),
        );
    }

    #[test]
    fn different_labels_give_different_seeds() {
        let world = WorldSeed::new(42);
        assert_ne!(
            derive_stream_seed(world, &StreamLabel::new("match:1")),
            derive_stream_seed(world, &StreamLabel::new("match:2")),
        );
    }

    #[test]
    fn different_worlds_give_different_seeds() {
        let label = StreamLabel::new("match:1");
        assert_ne!(
            derive_stream_seed(WorldSeed::new(1), &label),
            derive_stream_seed(WorldSeed::new(2), &label),
        );
    }

    #[test]
    fn every_byte_of_the_seed_is_filled() {
        let seed = derive_stream_seed(WorldSeed::new(0), &StreamLabel::new(""));
        for chunk in seed.as_chunks::<8>().0 {
            assert_ne!(chunk, &[0_u8; 8]);
        }
    }

    /// Pins the derivation. If this fails, the change breaks every existing
    /// save (ADR 0003) and needs an ADR, not a new expected value.
    #[test]
    fn derivation_is_pinned() {
        let seed = derive_stream_seed(WorldSeed::new(42), &StreamLabel::new("match:1"));
        assert_eq!(seed, PINNED_SEED);
    }

    const PINNED_SEED: [u8; STREAM_SEED_LEN] = [
        0x7a, 0x40, 0x05, 0x36, 0x96, 0xb3, 0xdf, 0x3f, 0x18, 0x47, 0x46, 0xfa, 0x4d, 0xa4, 0x73,
        0x79, 0x77, 0x71, 0xe1, 0x05, 0x49, 0x62, 0xb7, 0x8d, 0xb1, 0xea, 0x14, 0x32, 0xa6, 0x8d,
        0xf7, 0xe7,
    ];
}
