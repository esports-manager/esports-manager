// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! Construction of deterministic random streams (ADR 0003).

use domain::rng::{StreamLabel, StreamSource, WorldSeed, derive_stream_seed};
use rand_chacha::ChaCha8Rng;
use rand_core::SeedableRng;

/// Hands out the random streams of one world.
///
/// This is the only place generators are constructed. Domain and genre code
/// receive a stream; they never create one.
#[derive(Debug, PartialEq, Eq)]
pub struct RngProvider {
    seed: WorldSeed,
}

impl RngProvider {
    #[must_use]
    pub const fn new(seed: WorldSeed) -> Self {
        Self { seed }
    }

    /// The stream for `label`. Asking twice gives two generators that produce
    /// the same sequence.
    #[must_use]
    pub fn stream(&self, label: &StreamLabel) -> ChaCha8Rng {
        ChaCha8Rng::from_seed(derive_stream_seed(self.seed, label))
    }
}

impl StreamSource for RngProvider {
    type Stream = ChaCha8Rng;

    fn stream(&self, label: &StreamLabel) -> ChaCha8Rng {
        Self::stream(self, label)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use rand_core::Rng;

    fn first_values(rng: &mut ChaCha8Rng) -> [u64; 4] {
        [
            rng.next_u64(),
            rng.next_u64(),
            rng.next_u64(),
            rng.next_u64(),
        ]
    }

    #[test]
    fn the_same_label_replays_the_same_sequence() {
        let provider = RngProvider::new(WorldSeed::new(7));
        let label = StreamLabel::new("match:1");
        assert_eq!(
            first_values(&mut provider.stream(&label)),
            first_values(&mut provider.stream(&label)),
        );
    }

    #[test]
    fn using_one_stream_does_not_shift_another() {
        let provider = RngProvider::new(WorldSeed::new(7));
        let fixture = StreamLabel::new("match:1");
        let untouched = first_values(&mut provider.stream(&fixture));

        let mut other = provider.stream(&StreamLabel::new("generator:season:1"));
        let _ = first_values(&mut other);

        assert_eq!(first_values(&mut provider.stream(&fixture)), untouched);
    }

    #[test]
    fn the_stream_source_hands_out_the_same_streams() {
        let provider = RngProvider::new(WorldSeed::new(7));
        let label = StreamLabel::new("generator:team:team:a");
        assert_eq!(
            first_values(&mut StreamSource::stream(&provider, &label)),
            first_values(&mut provider.stream(&label)),
        );
    }

    #[test]
    fn different_labels_give_different_sequences() {
        let provider = RngProvider::new(WorldSeed::new(7));
        assert_ne!(
            first_values(&mut provider.stream(&StreamLabel::new("match:1"))),
            first_values(&mut provider.stream(&StreamLabel::new("match:2"))),
        );
    }

    /// Pins the generator. If this fails, the PRNG or its seeding changed,
    /// which breaks every existing save (ADR 0003).
    #[test]
    fn generator_output_is_pinned() {
        let provider = RngProvider::new(WorldSeed::new(42));
        let mut rng = provider.stream(&StreamLabel::new("match:1"));
        assert_eq!(first_values(&mut rng), PINNED_VALUES);
    }

    const PINNED_VALUES: [u64; 4] = [
        0x28dd_6187_a15c_26c5,
        0x1709_840d_db00_9c17,
        0x794f_bf30_2fad_c7ff,
        0xafb6_eadd_a773_2047,
    ];
}
