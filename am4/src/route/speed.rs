use derive_more::{Add, Display, Into};

/// Flight speed, km/h
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd, Add, Into, Display)]
pub struct Speed(f32);

impl Speed {
    pub fn get(&self) -> f32 {
        self.0
    }
}
