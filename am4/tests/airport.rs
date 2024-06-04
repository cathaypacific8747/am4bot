mod db;
use db::{AIRPORTS, AP_IDX};
use rstest::*;

#[rstest]
fn test_airports_ok() {
    assert_eq!(AP_IDX.index().len(), 15583);
    assert_eq!(AIRPORTS.data().len(), 3907);
}

#[rstest]
#[case("id:3500", "HKG")]
#[case("iata:Hkg", "HKG")]
#[case("icao:vhhh", "HKG")]
#[case("name:hong kong", "HKG")]
#[case("hong kong", "HKG")]
fn test_airport_search(#[case] inp: &str, #[case] iata: &str) {
    let ap = AP_IDX.search(inp).unwrap();
    assert_eq!(ap.iata.0, iata);
}

#[rstest]
#[case("VHHX  ", "HKG")]
#[case("hkgA", "HKG")]
#[case("VHHx", "HKG")]
#[case("hong kongg", "HKG")]
#[case("icao:hkgg", "HKG")] // cross suggest with iata
#[case("iata:vhhx", "HKG")] // cross suggest with icao
#[case("name:vhhx", "HKG")] // cross suggest with icao
fn test_airport_fail_and_suggest(#[case] inp: &str, #[case] iata: &str) {
    let ap_result = AP_IDX.search(inp);
    assert!(ap_result.is_err());

    let suggs = AP_IDX.suggest(inp);
    assert!(suggs.is_ok());
    assert_eq!(suggs.unwrap()[0].item.iata.0, iata);
}

#[rstest]
#[case("65590")]
#[case("id:65590")]
fn test_airport_stoi_overflow(#[case] inp: &str) {
    let result = AP_IDX.search(inp);
    assert!(result.is_err());
}
