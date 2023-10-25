use serde::{Serialize, Deserialize};
use std::collections::HashMap;


#[derive(Copy, Clone, Hash, PartialEq, Eq, Serialize, Deserialize)]
pub enum Role {
    Top,
    Jng,
    Mid,
    Adc,
    Sup,
}
