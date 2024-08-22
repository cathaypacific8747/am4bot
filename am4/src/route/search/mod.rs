/*!
 * Implements utilities for searching optimal destinations from an origin [Airport].
 *
 * We adopt a layered, modular approach to "eliminate" candidates for each rule.
 * This allows us to branch off any layer and perform multiple queries.
 *
 * ```txt
 * origin
 *   |
 *   +--- (direct distance) --- destination
 *   |
 *   v
 * AbstractRoute
 *   |
 *   +--- aircraft
 *   +--- user game mode
 *   |
 *   filter: range  --> too short
 *   filter: runway --> too short
 *   |
 * ConcreteRoute ------------> Sell airport optimisation
 *   |                |------> Contribution optimisation
 *   |
 *   +--- user settings
 *   +--- demand
 *   |
 *   filter: demand --> too low
 *   filter(toggleable): stopover finding --> no stopover
 *   |                         |
 *   +---- stopover -----------|
 *   |
 *   v
 * Route
 *   |
 *   +---- configuration
 *   |
 * Itinerary
 * ```
 */

#![allow(dead_code)] // temp

mod profit;

// TODO: const generic to silently ignore errors
use crate::airport::{db::Airports, Airport};
use thiserror::Error;

use crate::aircraft::Aircraft;
use crate::user::GameMode;

#[derive(Debug, Clone, Error)]
pub enum RouteError<'a> {
    // this shouldn't happen, but just in case downstream users create custom airports
    #[error("airport `{0:?}` not found in the database")]
    AirportNotFound(&'a Airport),
    #[error("destination `{0:?}` cannot be the same as the origin")]
    SelfReferential(&'a Airport),
    #[error("distance to `{0:?}` is too short ({1:.2} km < 100 km)")]
    DistanceTooShort(&'a Airport, f32),
    #[error("distance to `{0:?}` is above aircraft maximum range ({1:.2} km > {2:.2} km)")]
    DistanceAboveRange(&'a Airport, f32, f32),
    #[error("runway length at `{0:?}` is too short")]
    RunwayTooShort(&'a Airport),
}

// NOTE: not using struct of arrays for now. keeping it simple
/// A generic routelist, holding destinations from a given origin.
/// For performance, details ([Routes::routes]) are kept as minimal as possible
/// unless the user explicitly requests more.
#[derive(Debug, Clone)]
pub struct Routes<'a, R, C> {
    routes: Vec<R>,
    errors: Vec<RouteError<'a>>,
    config: C,
}

impl<'a, R, C> Routes<'a, R, C> {
    /// Get the list of routes (e.g. [AbstractRoutes])
    pub fn routes(&self) -> &[R] {
        &self.routes
    }

    /// Get details about routing failures (e.g. insufficient range, runway too short etc.)
    pub fn errors(&self) -> &[RouteError] {
        &self.errors
    }

    /// Get the metadata (e.g. [AbstractConfig], [ConcreteConfig])
    pub fn config(&self) -> &C {
        &self.config
    }
}

pub type AbstractRoutes<'a> = Routes<'a, AbstractRoute<'a>, AbstractConfig<'a>>;

#[derive(Debug, Clone)]
pub struct AbstractRoute<'a> {
    /// index into airports array
    destination: CheckedAirport<'a>,
    direct_distance: f32,
}

/// A valid airport that is guaranteed to exist in the demand table.
#[derive(Debug, Clone)]
pub struct CheckedAirport<'a> {
    airport: &'a Airport,
    /// Used to index into [Demands].
    idx: usize,
}

impl<'a> CheckedAirport<'a> {
    /// Check if the given airport is in the database.
    pub fn new(airports: &Airports, airport: &'a Airport) -> Result<Self, RouteError<'a>> {
        let idx = airports
            .index()
            .get(&(airport.idx.into()))
            .ok_or(RouteError::AirportNotFound(airport))
            .copied()?;
        Ok(Self { airport, idx })
    }
}

impl<'a> AbstractRoute<'a> {
    /// Create a direct [AbstractRoute] from the origin to the destination.
    /// Errors if the destination is the same as the origin, or if it doesn't exist in the database.
    fn new(
        airports: &'a Airports,
        origin: &'a Airport,
        destination: &'a Airport,
    ) -> Result<Self, RouteError<'a>> {
        if destination.idx == origin.idx {
            Err(RouteError::SelfReferential(destination))
        } else {
            let destination_checked = CheckedAirport::new(airports, destination)?;
            let distance = origin.location.distance_to(&destination.location);
            if distance < 100.0 {
                return Err(RouteError::DistanceTooShort(destination, distance));
            }
            Ok(Self {
                destination: destination_checked,
                direct_distance: distance,
            })
        }
    }
}

#[derive(Debug, Clone)]
pub struct AbstractConfig<'a> {
    airports: &'a Airports,
    origin: CheckedAirport<'a>,
}

impl<'a> AbstractRoutes<'a> {
    /// Create a routelist from an origin airport to multiple destination airports.
    pub fn new(
        airports: &'a Airports,
        origin: &'a Airport,
        destinations: &'a [Airport],
    ) -> Result<Self, RouteError<'a>> {
        let origin = CheckedAirport::new(airports, origin)?;
        let mut routes = Vec::new();
        let mut errors = Vec::new();
        for destination in destinations {
            match AbstractRoute::new(airports, origin.airport, destination) {
                Ok(route) => routes.push(route),
                Err(e) => errors.push(e),
            }
        }
        Ok(Self {
            routes,
            errors,
            config: AbstractConfig { airports, origin },
        })
    }
}

// NOTE: routes are abstract, but checked.
pub type ConcreteRoutes<'a> = Routes<'a, AbstractRoute<'a>, ConcreteConfig<'a>>;

#[derive(Debug, Clone)]
pub struct ConcreteConfig<'a> {
    airports: &'a Airports,
    origin: CheckedAirport<'a>,
    aircraft: &'a Aircraft,
    game_mode: &'a GameMode,
}

fn runway_valid(route: &AbstractRoute, aircraft: &Aircraft, game_mode: &GameMode) -> bool {
    match game_mode {
        GameMode::Easy => true,
        GameMode::Realism => route.destination.airport.rwy >= aircraft.rwy,
    }
}

fn distance_valid(route: &AbstractRoute, aircraft: &Aircraft) -> bool {
    route.direct_distance < aircraft.range as f32 * 2.0
}

impl<'a> AbstractRoutes<'a> {
    /// Prune routes that do not meet the aircraft's range and runway constraints,
    /// making [AbstractRoutes] into [ConcreteRoutes].
    pub fn with_aircraft(
        mut self, // consume the abstract routelist.
        aircraft: &'a Aircraft,
        game_mode: &'a GameMode,
    ) -> ConcreteRoutes<'a> {
        self.routes.retain(|route| {
            if !distance_valid(route, aircraft) {
                self.errors.push(RouteError::DistanceAboveRange(
                    route.destination.airport,
                    route.direct_distance,
                    aircraft.range as f32 * 2.0,
                ));
                return false;
            }
            if !runway_valid(route, aircraft, game_mode) {
                self.errors
                    .push(RouteError::RunwayTooShort(route.destination.airport));
                return false;
            }
            true
        });
        ConcreteRoutes {
            routes: self.routes,
            errors: self.errors,
            config: ConcreteConfig {
                airports: self.config.airports,
                origin: self.config.origin,
                aircraft,
                game_mode,
            },
        }
    }
}