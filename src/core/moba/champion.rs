use super::attribute::Attribute;
use super::role::Role;
use chrono::NaiveDate;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Clone, PartialEq, Serialize, Deserialize)]
pub enum ChampionType {
    Tank,
    Fighter,
    Mage,
    Assassin,
    Support,
    Marksman,
    Healer,
    Burst,
    Controller,
}

#[derive(Serialize, Deserialize, Clone, PartialEq)]
pub enum ChampionDifficulty {
    Easy,
    Normal,
    Medium,
    Hard,
    Advanced,
}

#[derive(Clone, PartialEq, Serialize, Deserialize)]
pub struct ChampionAttributes {
    pub strength: i32,
    pub skill_shots: i32,
    pub scaling_factor: f32,
    pub max_scaling: f32,
}

impl Attribute for ChampionAttributes {
    fn get_overall(&mut self) -> i32 {
        self.strength
    }
}

impl ChampionAttributes {
    pub fn new(
        strength: i32,
        skill_shots: i32,
        scaling_factor: f32,
        max_scaling: f32,
    ) -> Self {
        Self {
            strength,
            skill_shots,
            scaling_factor,
            max_scaling,
        }
    }
}

#[derive(Clone, PartialEq, Serialize, Deserialize)]
pub struct Champion {
    pub champion_id: Uuid,
    pub name: String,
    pub attributes: ChampionAttributes,
    pub champion_type: ChampionType,
    pub secondary_champion_type: Option<ChampionType>,
    pub difficulty: ChampionDifficulty,
    pub release_date: NaiveDate,
    pub roles: Vec<Role>,
}
