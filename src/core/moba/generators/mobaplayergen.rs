use std::collections::HashMap;
use rand;

use crate::core::moba::champion::Champion;
use crate::core::moba::mobaplayer::MobaPlayer;

use super::Generator;

pub struct MobaPlayerGenerator {
    champions: Vec<Champion>,
    names: HashMap<String, String>,
    nick_names: Vec<String>,
}

impl MobaPlayerGenerator {
    pub fn new(champions: Vec<Champion>, names: HashMap<String, String>, nick_names: Vec<String>) -> Self {
        Self {
            champions,
            names,
            nick_names,
        }
    }
}