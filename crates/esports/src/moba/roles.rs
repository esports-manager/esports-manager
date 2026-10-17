// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! The role set, overall, and role bias (attributes spec).
//!
//! Roles are package data: the core package has five, but a package can
//! define any non-empty set. Each role's weights are the single source of
//! what that role values, read both by overall and by the generator's bias.

use std::collections::{BTreeMap, BTreeSet};

use domain::id::ContentId;
use domain::rating::{Rating, weighted_mean};

use super::attributes::{MobaAttributes, OverallAttribute};

/// How many attributes count toward overall, for the role's mean weight.
const ATTRIBUTE_COUNT: f64 = 9.0;

/// One role and the weight it gives each attribute that counts toward
/// overall.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Role {
    id: ContentId,
    weights: [u32; 9],
    /// The sum of the weights, in `u64` so large weights can't saturate it.
    total: u64,
}

/// The roles of a world, in display order.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct RoleSet {
    roles: Vec<Role>,
}

/// Why a role set can't be used.
#[derive(Debug, Clone, PartialEq, Eq, thiserror::Error)]
pub enum RoleSetError {
    #[error("the role set has no roles")]
    Empty,
    #[error("role `{0}` appears more than once")]
    DuplicateRole(ContentId),
    #[error("role `{role}` has no weight for {attribute:?}")]
    MissingWeight {
        role: ContentId,
        attribute: OverallAttribute,
    },
    #[error("role `{0}` has weights that sum to zero")]
    ZeroWeights(ContentId),
}

impl RoleSet {
    /// Builds a role set from each role's weights, reporting every problem.
    ///
    /// # Errors
    ///
    /// When there are no roles, a role repeats, a role lacks a weight for an
    /// attribute that counts toward overall, or its weights sum to zero.
    pub fn new(
        definitions: Vec<(ContentId, BTreeMap<OverallAttribute, u32>)>,
    ) -> Result<Self, Vec<RoleSetError>> {
        if definitions.is_empty() {
            return Err(vec![RoleSetError::Empty]);
        }
        let mut errors = Vec::new();
        let mut seen = BTreeSet::new();
        let mut roles = Vec::new();
        for (id, weights) in definitions {
            if !seen.insert(id.clone()) {
                errors.push(RoleSetError::DuplicateRole(id));
                continue;
            }
            match Role::new(id, &weights) {
                Ok(role) => roles.push(role),
                Err(mut role_errors) => errors.append(&mut role_errors),
            }
        }
        if errors.is_empty() {
            Ok(Self { roles })
        } else {
            Err(errors)
        }
    }

    #[must_use]
    pub fn roles(&self) -> &[Role] {
        &self.roles
    }

    #[must_use]
    pub fn get(&self, id: &ContentId) -> Option<&Role> {
        self.roles.iter().find(|role| &role.id == id)
    }
}

impl Role {
    fn new(
        id: ContentId,
        weights: &BTreeMap<OverallAttribute, u32>,
    ) -> Result<Self, Vec<RoleSetError>> {
        let mut row = [0; 9];
        let mut errors = Vec::new();
        for attribute in OverallAttribute::ALL {
            match weights.get(&attribute) {
                Some(&weight) => row[attribute.index()] = weight,
                None => errors.push(RoleSetError::MissingWeight {
                    role: id.clone(),
                    attribute,
                }),
            }
        }
        let total: u64 = row.iter().map(|&weight| u64::from(weight)).sum();
        if errors.is_empty() && total == 0 {
            errors.push(RoleSetError::ZeroWeights(id.clone()));
        }
        if errors.is_empty() {
            Ok(Self {
                id,
                weights: row,
                total,
            })
        } else {
            Err(errors)
        }
    }

    #[must_use]
    pub const fn id(&self) -> &ContentId {
        &self.id
    }

    #[must_use]
    pub const fn weight(&self, attribute: OverallAttribute) -> u32 {
        self.weights[attribute.index()]
    }

    /// The overall of a player whose main role this is: the weighted mean of
    /// the attributes that count, with this role's weights.
    #[must_use]
    pub fn overall(&self, attributes: &MobaAttributes) -> Rating {
        let terms = OverallAttribute::ALL
            .map(|attribute| (attributes.get(attribute), self.weight(attribute)));
        // The weights sum to more than zero, so there is always a mean.
        weighted_mean(terms).unwrap_or(Rating::MIN)
    }

    /// How far above or below a player's base the generator draws an
    /// attribute for this role: `scale × (w − w̄) / w̄`, where `w̄` is this
    /// role's mean weight. Attributes the role values more come out higher.
    #[must_use]
    pub fn bias(&self, attribute: OverallAttribute, scale: f64) -> f64 {
        #[expect(
            clippy::cast_precision_loss,
            reason = "a sum of nine u32 weights is far below 2^53, so an f64 holds it exactly"
        )]
        let total = self.total as f64;
        let mean = total / ATTRIBUTE_COUNT;
        scale * (f64::from(self.weight(attribute)) - mean) / mean
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::moba::attributes::MobaSkill;

    const MECHANICS: OverallAttribute = OverallAttribute::Skill(MobaSkill::Mechanics);
    const SHOTCALLING: OverallAttribute = OverallAttribute::Skill(MobaSkill::Shotcalling);

    fn id(text: &str) -> ContentId {
        ContentId::parse(text).unwrap()
    }

    fn rating(points: u32) -> Rating {
        Rating::from_points(points).unwrap()
    }

    fn weights(row: [u32; 9]) -> BTreeMap<OverallAttribute, u32> {
        OverallAttribute::ALL.into_iter().zip(row).collect()
    }

    /// The role weight table of the attributes spec, in `OverallAttribute`
    /// order.
    fn core_roles() -> RoleSet {
        RoleSet::new(vec![
            (id("role:top"), weights([16, 18, 14, 10, 12, 6, 4, 10, 10])),
            (id("role:jungle"), weights([14, 6, 20, 14, 8, 6, 14, 10, 8])),
            (id("role:mid"), weights([20, 16, 14, 10, 12, 8, 6, 6, 8])),
            (id("role:bot"), weights([20, 18, 10, 10, 16, 6, 4, 8, 8])),
            (
                id("role:support"),
                weights([10, 12, 14, 16, 12, 6, 14, 10, 6]),
            ),
        ])
        .unwrap()
    }

    fn role(set: &RoleSet, text: &str) -> Role {
        set.get(&id(text)).unwrap().clone()
    }

    fn with(attribute: OverallAttribute, points: u32, base: u32) -> MobaAttributes {
        let mut attributes = MobaAttributes::uniform(rating(base));
        match attribute {
            OverallAttribute::Skill(MobaSkill::Mechanics) => {
                attributes.skills.mechanics = rating(points);
            }
            OverallAttribute::Skill(MobaSkill::Shotcalling) => {
                attributes.skills.shotcalling = rating(points);
            }
            OverallAttribute::Skill(_)
            | OverallAttribute::Teamwork
            | OverallAttribute::Composure => {
                unreachable!("only used for Mechanics and Shotcalling")
            }
        }
        attributes
    }

    #[test]
    fn the_attribute_count_matches_the_attributes() {
        assert!((ATTRIBUTE_COUNT - 9.0).abs() < f64::EPSILON);
        assert_eq!(OverallAttribute::ALL.len(), 9);
    }

    #[test]
    fn every_core_role_sums_to_100() {
        for role in core_roles().roles() {
            assert_eq!(role.total, 100, "{}", role.id());
        }
    }

    #[test]
    fn roles_keep_their_display_order() {
        let set = core_roles();
        let order: Vec<&str> = set.roles().iter().map(|role| role.id().slug()).collect();
        assert_eq!(order, ["top", "jungle", "mid", "bot", "support"]);
        assert_eq!(set.get(&id("role:coach")), None);
    }

    #[test]
    fn overall_is_the_role_weighted_mean() {
        // spec: ATTR-001
        // Given
        let mid = role(&core_roles(), "role:mid");
        let player = with(MECHANICS, 90, 70);
        // When
        let overall = mid.overall(&player);
        // Then
        assert_eq!(overall, rating(74));
    }

    #[test]
    fn attributes_outside_the_formula_do_not_move_overall() {
        // spec: ATTR-002
        // Given
        let mid = role(&core_roles(), "role:mid");
        let mut player = with(MECHANICS, 90, 70);
        assert_eq!(mid.overall(&player), rating(74));
        // When
        player.core.aggression = rating(1);
        player.core.work_ethic = rating(99);
        player.core.consistency = rating(1);
        player.core.potential = rating(99);
        // Then
        assert_eq!(mid.overall(&player), rating(74));
    }

    #[test]
    fn the_main_role_picks_the_weights() {
        // spec: ATTR-003
        // Given
        let set = core_roles();
        let player = with(MECHANICS, 90, 70);
        // When
        let as_mid = role(&set, "role:mid").overall(&player);
        let as_support = role(&set, "role:support").overall(&player);
        // Then
        assert_eq!(as_mid, rating(74));
        assert_eq!(as_support, rating(72));
    }

    #[test]
    fn weights_come_from_the_role_set() {
        // spec: ATTR-005
        // Given
        let mut only_mechanics = [0; 9];
        only_mechanics[MECHANICS.index()] = 100;
        let set = RoleSet::new(vec![(id("role:mid"), weights(only_mechanics))]).unwrap();
        let player = with(MECHANICS, 87, 40);
        // When
        let overall = role(&set, "role:mid").overall(&player);
        // Then
        assert_eq!(overall, player.skills.mechanics);
    }

    #[test]
    fn every_problem_with_a_role_set_is_reported() {
        let mut missing = weights([1; 9]);
        missing.remove(&OverallAttribute::Composure);
        let errors = RoleSet::new(vec![
            (id("role:support"), weights([0; 9])),
            (id("role:jungle"), missing),
            (id("role:support"), weights([1; 9])),
        ])
        .unwrap_err();
        assert_eq!(
            errors,
            [
                RoleSetError::ZeroWeights(id("role:support")),
                RoleSetError::MissingWeight {
                    role: id("role:jungle"),
                    attribute: OverallAttribute::Composure
                },
                RoleSetError::DuplicateRole(id("role:support")),
            ]
        );
    }

    #[test]
    fn a_role_set_needs_a_role() {
        assert_eq!(RoleSet::new(vec![]), Err(vec![RoleSetError::Empty]));
    }

    #[test]
    fn a_role_missing_weights_is_not_also_reported_as_zero() {
        let errors = RoleSet::new(vec![(id("role:mid"), BTreeMap::new())]).unwrap_err();
        assert_eq!(errors.len(), 9);
        assert!(!errors.contains(&RoleSetError::ZeroWeights(id("role:mid"))));
    }

    #[test]
    fn bias_favours_what_the_role_values() {
        let mid = role(&core_roles(), "role:mid");
        // Mean weight 100 / 9; Mechanics 20 and Shotcalling 6.
        assert!(
            (mid.bias(MECHANICS, 8.0) - 8.0 * (20.0 - 100.0 / 9.0) / (100.0 / 9.0)).abs() < 1e-12
        );
        assert!((mid.bias(MECHANICS, 8.0) - 6.4).abs() < 1e-12);
        assert!((mid.bias(SHOTCALLING, 8.0) - (-3.68)).abs() < 1e-12);
    }

    #[test]
    fn a_role_with_equal_weights_has_no_bias() {
        let set = RoleSet::new(vec![(id("role:flex"), weights([3; 9]))]).unwrap();
        let flex = role(&set, "role:flex");
        for attribute in OverallAttribute::ALL {
            assert!(flex.bias(attribute, 8.0).abs() < 1e-12);
        }
    }

    #[test]
    fn shotcalling_weighs_most_for_support_and_jungle() {
        let set = core_roles();
        let support = role(&set, "role:support");
        let mid = role(&set, "role:mid");
        assert!(support.bias(SHOTCALLING, 8.0) > mid.bias(SHOTCALLING, 8.0));
        assert_eq!(support.weight(SHOTCALLING), 14);
        let shot_with = with(SHOTCALLING, 99, 50);
        assert!(support.overall(&shot_with) > mid.overall(&shot_with));
    }
}
