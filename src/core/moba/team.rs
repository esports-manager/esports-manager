use uuid::Uuid;
use serde::{Serialize, Deserialize};
use super::mobaplayer::MobaPlayer;


#[derive(Clone, PartialEq, Deserialize, Serialize)]
pub struct Team {
    pub team_id: Uuid,
    pub name: String,
    pub nationality: String,
    pub roster: Vec<MobaPlayer>,
}

impl Team {
    pub fn new(team_id: Uuid, name: String, nationality: String, roster: Vec<MobaPlayer>) -> Self {
        Self {
            team_id,
            name,
            nationality,
            roster,
        }
    }
}