use crate::airport::{Airport, AirportError, Iata, Icao, Id, Name};
use crate::utils::ParseError;
use crate::utils::{queue_suggestions, Suggestion, MAX_SUGGESTIONS};
use jaro_winkler::jaro_winkler;
use rkyv::{self, Deserialize};
use std::collections::BinaryHeap;
use std::collections::HashMap;
use std::convert::Into;
use std::fs::File;
use std::io::Read;
use std::str::FromStr;

use thiserror::Error;

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum SearchKey {
    Id(Id),
    Iata(Iata),
    Icao(Icao),
    Name(Name),
}

impl From<Id> for SearchKey {
    fn from(id: Id) -> Self {
        SearchKey::Id(id)
    }
}

impl From<Iata> for SearchKey {
    fn from(iata: Iata) -> Self {
        SearchKey::Iata(Iata(iata.0.to_uppercase()))
    }
}

impl From<Icao> for SearchKey {
    fn from(icao: Icao) -> Self {
        SearchKey::Icao(Icao(icao.0.to_uppercase()))
    }
}

impl From<Name> for SearchKey {
    fn from(name: Name) -> Self {
        SearchKey::Name(Name(name.0.to_uppercase()))
    }
}

#[derive(Debug)]
pub enum QueryKey {
    All(String),
    Id(Id),
    Iata(Iata),
    Icao(Icao),
    Name(Name),
}

#[derive(Debug)]
pub struct QueryCtx {
    pub key: QueryKey,
}

impl FromStr for QueryCtx {
    type Err = AirportSearchError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let s = s.trim();

        let key = match s.to_uppercase().split_once(':') {
            None => QueryKey::All(s.to_string()),
            Some((k, v)) => match k {
                "IATA" => QueryKey::Iata(Iata(v.to_string())),
                "ICAO" => QueryKey::Icao(Icao(v.to_string())),
                "NAME" => QueryKey::Name(Name(v.to_string())),
                "ID" => QueryKey::Id(Id::from_str(v)?),
                _ => return Err(AirportSearchError::InvalidQueryType),
            },
        };

        Ok(QueryCtx { key })
    }
}

impl From<QueryCtx> for Option<SearchKey> {
    fn from(val: QueryCtx) -> Self {
        match &val.key {
            QueryKey::All(s) => {
                if let Ok(v) = Id::from_str(s) {
                    Some(SearchKey::from(v))
                } else if let Ok(v) = Iata::from_str(s) {
                    Some(SearchKey::from(v))
                } else if let Ok(v) = Icao::from_str(s) {
                    Some(SearchKey::from(v))
                } else if let Ok(v) = Name::from_str(s) {
                    Some(SearchKey::from(v))
                } else {
                    None
                }
            }
            QueryKey::Id(id) => Some(SearchKey::from(id.clone())),
            QueryKey::Iata(iata) => Some(SearchKey::from(iata.clone())),
            QueryKey::Icao(icao) => Some(SearchKey::from(icao.clone())),
            QueryKey::Name(name) => Some(SearchKey::from(name.clone())),
        }
    }
}

#[derive(Debug)]
pub struct Airports {
    data: Vec<Airport>,
    index: HashMap<SearchKey, usize>,
}

impl Airports {
    pub fn from(file_path: &str) -> Result<Self, ParseError> {
        let mut file = File::open(file_path)?;
        let mut buffer = Vec::<u8>::new();
        file.read_to_end(&mut buffer)?;

        let archived = rkyv::check_archived_root::<Vec<Airport>>(&buffer)
            .map_err(|e| ParseError::ArchiveError(e.to_string()))?;

        let data: Vec<Airport> = archived
            .deserialize(&mut rkyv::Infallible)
            .map_err(|e| ParseError::DeserialiseError(e.to_string()))?;

        let mut index = HashMap::<SearchKey, usize>::new();

        for (i, ap) in data.iter().enumerate() {
            index.entry(SearchKey::from(ap.id.clone())).or_insert(i);
            index.entry(SearchKey::from(ap.iata.clone())).or_insert(i);
            index.entry(SearchKey::from(ap.icao.clone())).or_insert(i);
            index.entry(SearchKey::from(ap.name.clone())).or_insert(i);
        }

        Ok(Self { data, index })
    }

    /// Search for an airport
    pub fn search(&self, s: &str) -> Result<&Airport, AirportSearchError> {
        let ctx = QueryCtx::from_str(s)?;
        let key: Option<SearchKey> = ctx.into();
        let key = key.ok_or(AirportSearchError::InvalidQueryType)?;

        self.index
            .get(&key)
            .and_then(|&i| self.data.get(i))
            .ok_or(AirportSearchError::AirportNotFound)
    }

    pub fn suggest(&self, s: &str) -> Result<Vec<Suggestion<&Airport>>, AirportSearchError> {
        let ctx = QueryCtx::from_str(s)?;

        // TODO: this is a hack to get the uppercase version of the parsed query
        let key: Option<SearchKey> = ctx.into();
        let key = key.ok_or(AirportSearchError::InvalidQueryType)?;
        let su = match key {
            SearchKey::Iata(v) => v.0.clone(),
            SearchKey::Icao(v) => v.0.clone(),
            SearchKey::Name(v) => v.0.clone(),
            SearchKey::Id(v) => v.0.to_string(),
        };

        let mut heap = BinaryHeap::with_capacity(MAX_SUGGESTIONS);

        for (key, &i) in &self.index {
            // TODO: restrict to only search by shortname if ctx.key is shortname
            let s = match key {
                SearchKey::Iata(v) => &v.0,
                SearchKey::Icao(v) => &v.0,
                SearchKey::Name(v) => &v.0,
                _ => continue, // ignore searching by id
            };
            let similarity = jaro_winkler(s, &su);
            // Access data using the index
            queue_suggestions(&mut heap, &self.data[i], similarity);
        }

        Ok(heap.into_sorted_vec())
    }

    // getter only - no modification after building allowed
    pub fn data(&self) -> &Vec<Airport> {
        &self.data
    }

    pub fn index(&self) -> &HashMap<SearchKey, usize> {
        &self.index
    }
}

#[derive(Debug, Error)]
pub enum AirportSearchError {
    #[error("Invalid query type")]
    InvalidQueryType,
    #[error("Airport not found")]
    AirportNotFound,
    #[error(transparent)]
    Airport(#[from] AirportError),
}