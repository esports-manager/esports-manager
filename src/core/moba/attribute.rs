use serde::{Serialize, Deserialize};
use anyhow::{Result};
use thiserror::Error;

#[derive(Error, Debug)]
pub enum RankError {
    #[error("Invalid value. Value must be in range 0-100")]
    InvalidValue,
    #[error("Unknown error")]
    Unknown,
}

#[derive(Clone, Copy, PartialEq, PartialOrd, Serialize, Deserialize)]
pub enum Rank {
    F,
    D,
    C,
    B,
    A,
    S
}

impl Rank {
    pub fn get_rank(value: i32) -> Result<Rank, RankError> {
        match value {
            0..=29 => Ok(Rank::F),
            30..=49 => Ok(Rank::D),
            50..=69 => Ok(Rank::C),
            70..=82 => Ok(Rank::B),
            83..=91 => Ok(Rank::A),
            92..=100 => Ok(Rank::S),
            _ => Err(RankError::InvalidValue)
        }
    }
}

pub trait Attribute {
    fn get_overall(&mut self) -> i32;
    fn get_rank(&mut self, value: i32) -> Result<Rank, RankError> {
        Rank::get_rank(value)
    }
}
