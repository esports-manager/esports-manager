use chrono::naive::NaiveDate;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use uuid::Uuid;

use super::champion::Champion;
use super::role::Role;
use super::attribute::Attribute;

#[derive(Serialize, Deserialize, Clone, PartialEq)]
pub enum ChampionPoolRank {
    Bronze,
    Silver,
    Gold,
    Platinum,
    Diamond,
    Master
}

#[derive(Serialize, Deserialize, Clone, PartialEq)]
pub struct ChampionPool {
    pub champion_id: Uuid,
    pub champion_rank: ChampionPoolRank,
    pub total_exp: f32,
}

#[derive(Serialize, Deserialize, Clone, PartialEq)]
pub struct MobaPlayerOffensiveAttributes {
    pub aggressiveness: i32,
    pub positioning: i32,
    pub lane_pressure: i32,
    pub kill_instinct: i32,
}

#[derive(Serialize, Deserialize, Clone, PartialEq)]
pub struct MobaPlayerIntelligenceAttributes {
    pub map_awareness: i32,
    pub team_work: i32,
    pub shot_calling: i32,
}

#[derive(Serialize, Deserialize, Clone, PartialEq)]
pub struct MobaPlayerUtilityAttributes {
    pub vision_control: i32,
    pub utility: i32,
    pub positioning: i32,
}

#[derive(Serialize, Deserialize, Clone, PartialEq)]
pub struct MobaPlayerJungleAttributes {
    pub ganking: i32,
    pub objective_control: i32,
    pub pathing: i32,
}

#[derive(Serialize, Deserialize, Clone, PartialEq)]
pub struct MobaPlayerMechanics {
    pub mechanics: i32,
    pub reflexes: i32,
    pub speed: i32,
    pub skill_shot_accuracy: i32,
    pub farming: i32,
}

#[derive(Serialize, Deserialize, Clone, PartialEq)]
pub struct MobaPlayerAttributes {
    pub offensive: MobaPlayerOffensiveAttributes,
    pub intelligence: MobaPlayerIntelligenceAttributes,
    pub utility: MobaPlayerUtilityAttributes,
    pub jungle: MobaPlayerJungleAttributes,
    pub mechanics: MobaPlayerMechanics,
}

#[derive(Serialize, Deserialize, Clone, PartialEq)]
pub struct MobaPlayer {
    player_id: Uuid,
    pub first_name: String,
    pub last_name: String,
    pub nick_name: String,
    pub birth_date: NaiveDate,
    pub attributes: MobaPlayerAttributes,
    pub champions: Vec<ChampionPool>,
}

impl MobaPlayer {
    pub fn new(
        player_id: Uuid,
        first_name: String,
        last_name: String,
        nick_name: String,
        birth_date: NaiveDate,
        attributes: MobaPlayerAttributes,
        champions: Vec<ChampionPool>,
    ) -> Self {
        Self {
            player_id,
            first_name,
            last_name,
            nick_name,
            birth_date,
            attributes,
            champions,
        }
    }
}
