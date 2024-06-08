pub mod custom;
pub mod db;

use rkyv::{Archive as Ra, Deserialize as Rd, Serialize as Rs};
use serde::{Deserialize, Serialize};
use std::fmt;
use std::str::FromStr;
use thiserror::Error;

#[cfg(feature = "wasm")]
use wasm_bindgen::prelude::*;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Ra, Rd, Rs)]
#[cfg_attr(feature = "wasm", wasm_bindgen(getter_with_clone, inspectable))]
#[archive(check_bytes)]
pub struct Aircraft {
    pub id: AcId,
    pub shortname: ShortName,
    pub manufacturer: String,
    pub name: AcName,
    #[serde(rename = "type")]
    pub ac_type: AircraftType,
    pub priority: EnginePriority,
    pub eid: u16,
    pub ename: String,
    pub speed: f32,
    pub fuel: f32,
    pub co2: f32,
    pub cost: u32,
    pub capacity: u32,
    pub rwy: u16,
    pub check_cost: u32,
    pub range: u16,
    pub ceil: u16,
    pub maint: u16,
    pub pilots: u8,
    pub crew: u8,
    pub engineers: u8,
    pub technicians: u8,
    pub img: String,
    pub wingspan: u8,
    pub length: u8,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash, Ra, Rd, Rs)]
#[archive(check_bytes)]
#[cfg_attr(feature = "wasm", wasm_bindgen)]
pub struct AcId(pub u16);

impl FromStr for AcId {
    type Err = AircraftError;

    fn from_str(id: &str) -> Result<Self, Self::Err> {
        id.parse::<u16>()
            .map(Self)
            .map_err(AircraftError::InvalidID)
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash, Ra, Rd, Rs)]
#[archive(check_bytes)]
#[cfg_attr(feature = "wasm", wasm_bindgen(getter_with_clone))]
pub struct ShortName(pub String);

impl FromStr for ShortName {
    type Err = AircraftError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.len() {
            1..=20 => Ok(Self(s.to_string())), // actual max 11, but not invalidating because we want fuzzy search to not be too strict
            _ => Err(AircraftError::InvalidShortName),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash, Ra, Rd, Rs)]
#[archive(check_bytes)]
#[cfg_attr(feature = "wasm", wasm_bindgen(getter_with_clone))]
pub struct AcName(pub String);

impl FromStr for AcName {
    type Err = AircraftError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.len() {
            1..=40 => Ok(Self(s.to_string())), // actual max 28
            _ => Err(AircraftError::InvalidName),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash, Ra, Rd, Rs)]
#[archive(check_bytes)]
#[cfg_attr(feature = "wasm", wasm_bindgen)]
pub struct EnginePriority(pub u8);

impl FromStr for EnginePriority {
    type Err = AircraftError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        s.parse::<u8>()
            .map(Self)
            .map_err(AircraftError::InvalidPriority)
    }
}

impl fmt::Display for EnginePriority {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "{}", self.0)
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Ra, Rd, Rs)]
#[archive(check_bytes)]
#[serde(rename_all = "lowercase")]
#[cfg_attr(feature = "wasm", wasm_bindgen)]
#[repr(u8)]
pub enum AircraftType {
    Pax = 0,
    Cargo = 1,
    Vip = 2,
}

impl FromStr for AircraftType {
    type Err = AircraftError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_uppercase().as_str() {
            "PAX" => Ok(Self::Pax),
            "CARGO" => Ok(Self::Cargo),
            "VIP" => Ok(Self::Vip),
            _ => Err(AircraftError::InvalidAircraftType),
        }
    }
}

#[derive(Debug, Error)]
pub enum AircraftError {
    #[error("Invalid aircraft ID: {0}")]
    InvalidID(#[source] std::num::ParseIntError),
    #[error("Invalid short name: must be between 1 and 20 characters")]
    InvalidShortName,
    #[error("Invalid name: must be between 1 and 40 characters")]
    InvalidName,
    #[error("Invalid aircraft type")]
    InvalidAircraftType,
    #[error("Invalid engine priority: {0}")]
    InvalidPriority(#[source] std::num::ParseIntError),
}
