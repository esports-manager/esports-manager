// SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
//
// SPDX-License-Identifier: GPL-3.0-or-later

//! MOBA skills, and the attributes that count toward overall (attributes
//! spec).

use domain::attributes::CoreAttributes;
use domain::rating::Rating;

/// The trainable MOBA skills.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum MobaSkill {
    Mechanics,
    Laning,
    GameSense,
    Awareness,
    Positioning,
    ChampionPoolBreadth,
    Shotcalling,
}

impl MobaSkill {
    pub const ALL: [Self; 7] = [
        Self::Mechanics,
        Self::Laning,
        Self::GameSense,
        Self::Awareness,
        Self::Positioning,
        Self::ChampionPoolBreadth,
        Self::Shotcalling,
    ];
}

/// A player's MOBA skills.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct MobaSkills {
    pub mechanics: Rating,
    pub laning: Rating,
    pub game_sense: Rating,
    pub awareness: Rating,
    pub positioning: Rating,
    pub champion_pool_breadth: Rating,
    pub shotcalling: Rating,
}

impl MobaSkills {
    #[must_use]
    pub const fn uniform(rating: Rating) -> Self {
        Self {
            mechanics: rating,
            laning: rating,
            game_sense: rating,
            awareness: rating,
            positioning: rating,
            champion_pool_breadth: rating,
            shotcalling: rating,
        }
    }

    /// The skill itself, to change it.
    pub const fn get_mut(&mut self, skill: MobaSkill) -> &mut Rating {
        match skill {
            MobaSkill::Mechanics => &mut self.mechanics,
            MobaSkill::Laning => &mut self.laning,
            MobaSkill::GameSense => &mut self.game_sense,
            MobaSkill::Awareness => &mut self.awareness,
            MobaSkill::Positioning => &mut self.positioning,
            MobaSkill::ChampionPoolBreadth => &mut self.champion_pool_breadth,
            MobaSkill::Shotcalling => &mut self.shotcalling,
        }
    }

    #[must_use]
    pub const fn get(&self, skill: MobaSkill) -> Rating {
        match skill {
            MobaSkill::Mechanics => self.mechanics,
            MobaSkill::Laning => self.laning,
            MobaSkill::GameSense => self.game_sense,
            MobaSkill::Awareness => self.awareness,
            MobaSkill::Positioning => self.positioning,
            MobaSkill::ChampionPoolBreadth => self.champion_pool_breadth,
            MobaSkill::Shotcalling => self.shotcalling,
        }
    }
}

/// The attributes that count toward overall: the seven skills plus Teamwork
/// and Composure. Aggression is a style, Work Ethic drives growth, and hidden
/// attributes would leak through a visible number, so none of them count.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum OverallAttribute {
    Skill(MobaSkill),
    Teamwork,
    Composure,
}

impl OverallAttribute {
    pub const ALL: [Self; 9] = [
        Self::Skill(MobaSkill::Mechanics),
        Self::Skill(MobaSkill::Laning),
        Self::Skill(MobaSkill::GameSense),
        Self::Skill(MobaSkill::Awareness),
        Self::Skill(MobaSkill::Positioning),
        Self::Skill(MobaSkill::ChampionPoolBreadth),
        Self::Skill(MobaSkill::Shotcalling),
        Self::Teamwork,
        Self::Composure,
    ];

    /// Position in [`Self::ALL`].
    #[must_use]
    pub const fn index(self) -> usize {
        match self {
            Self::Skill(MobaSkill::Mechanics) => 0,
            Self::Skill(MobaSkill::Laning) => 1,
            Self::Skill(MobaSkill::GameSense) => 2,
            Self::Skill(MobaSkill::Awareness) => 3,
            Self::Skill(MobaSkill::Positioning) => 4,
            Self::Skill(MobaSkill::ChampionPoolBreadth) => 5,
            Self::Skill(MobaSkill::Shotcalling) => 6,
            Self::Teamwork => 7,
            Self::Composure => 8,
        }
    }
}

/// Everything a MOBA player is rated on.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct MobaAttributes {
    pub core: CoreAttributes,
    pub skills: MobaSkills,
}

impl MobaAttributes {
    #[must_use]
    pub const fn uniform(rating: Rating) -> Self {
        Self {
            core: CoreAttributes::uniform(rating),
            skills: MobaSkills::uniform(rating),
        }
    }

    #[must_use]
    pub const fn get(&self, attribute: OverallAttribute) -> Rating {
        match attribute {
            OverallAttribute::Skill(skill) => self.skills.get(skill),
            OverallAttribute::Teamwork => self.core.teamwork,
            OverallAttribute::Composure => self.core.composure,
        }
    }

    /// The attribute itself, to change it.
    pub const fn get_mut(&mut self, attribute: OverallAttribute) -> &mut Rating {
        match attribute {
            OverallAttribute::Skill(skill) => self.skills.get_mut(skill),
            OverallAttribute::Teamwork => &mut self.core.teamwork,
            OverallAttribute::Composure => &mut self.core.composure,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn rating(points: u32) -> Rating {
        Rating::from_points(points).unwrap()
    }

    fn distinct() -> MobaAttributes {
        MobaAttributes {
            core: CoreAttributes {
                teamwork: rating(81),
                aggression: rating(82),
                composure: rating(83),
                work_ethic: rating(84),
                consistency: rating(85),
                potential: rating(86),
            },
            skills: MobaSkills {
                mechanics: rating(71),
                laning: rating(72),
                game_sense: rating(73),
                awareness: rating(74),
                positioning: rating(75),
                champion_pool_breadth: rating(76),
                shotcalling: rating(77),
            },
        }
    }

    #[test]
    fn each_skill_reads_its_own_field() {
        let skills = distinct().skills;
        let values: Vec<u8> = MobaSkill::ALL
            .iter()
            .map(|&s| skills.get(s).display())
            .collect();
        assert_eq!(values, [71, 72, 73, 74, 75, 76, 77]);
    }

    #[test]
    fn overall_attributes_read_skills_teamwork_and_composure() {
        let attributes = distinct();
        let values: Vec<u8> = OverallAttribute::ALL
            .iter()
            .map(|&a| attributes.get(a).display())
            .collect();
        assert_eq!(values, [71, 72, 73, 74, 75, 76, 77, 81, 83]);
    }

    #[test]
    fn get_mut_changes_the_attribute_get_reads() {
        let mut attributes = MobaAttributes::uniform(rating(30));
        for (points, attribute) in (40..).zip(OverallAttribute::ALL) {
            *attributes.get_mut(attribute) = rating(points);
        }
        let values: Vec<u8> = OverallAttribute::ALL
            .iter()
            .map(|&a| attributes.get(a).display())
            .collect();
        assert_eq!(values, [40, 41, 42, 43, 44, 45, 46, 47, 48]);
    }

    #[test]
    fn indexes_match_the_order_of_all() {
        for (position, attribute) in OverallAttribute::ALL.iter().enumerate() {
            assert_eq!(attribute.index(), position);
        }
    }

    #[test]
    fn uniform_sets_every_skill() {
        let attributes = MobaAttributes::uniform(rating(30));
        assert!(
            OverallAttribute::ALL
                .iter()
                .all(|&a| attributes.get(a) == rating(30))
        );
        assert_eq!(attributes.core, CoreAttributes::uniform(rating(30)));
    }
}
