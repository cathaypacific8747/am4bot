#include <iostream>
#include <algorithm>
#include <string>

#include "include/db.hpp"
#include "include/airport.hpp"
#include "include/route.hpp"

using std::string;
using namespace duckdb;

Airport::Airport() : valid(false) {}

Airport::Airport(const duckdb::DataChunk& chunk, idx_t row) :
    id(chunk.GetValue(0, row).GetValue<uint16_t>()),
    name(chunk.GetValue(1, row).GetValue<string>()),
    fullname(chunk.GetValue(2, row).GetValue<string>()),
    country(chunk.GetValue(3, row).GetValue<string>()),
    continent(chunk.GetValue(4, row).GetValue<string>()),
    iata(chunk.GetValue(5, row).GetValue<string>()),
    icao(chunk.GetValue(6, row).GetValue<string>()),
    lat(chunk.GetValue(7, row).GetValue<double>()),
    lng(chunk.GetValue(8, row).GetValue<double>()),
    rwy(chunk.GetValue(9, row).GetValue<uint16_t>()),
    market(chunk.GetValue(10, row).GetValue<uint8_t>()),
    hub_cost(chunk.GetValue(11, row).GetValue<uint32_t>()),
    rwy_codes(chunk.GetValue(12, row).GetValue<string>()),
    valid(true) {}

Airport Airport::_from_id(uint16_t id) {
    auto result = Database::Client()->get_airport_by_id->Execute(id);
    CHECK_SUCCESS(result);
    auto chunk = result->Fetch();
    if (!chunk || chunk->size() == 0) return Airport();

    return Airport(*chunk, 0);
}

Airport Airport::_from_iata(const string& s) {
    auto result = Database::Client()->get_airport_by_iata->Execute(s.c_str()); // note: std::string somehow converts to BLOB
    CHECK_SUCCESS(result);
    auto chunk = result->Fetch();
    if (!chunk || chunk->size() == 0) return Airport();

    return Airport(*chunk, 0);
}

Airport Airport::_from_icao(const string& s) {
    auto result = Database::Client()->get_airport_by_icao->Execute(s.c_str());
    CHECK_SUCCESS(result);
    auto chunk = result->Fetch();
    if (!chunk || chunk->size() == 0) return Airport();

    return Airport(*chunk, 0);
}

Airport Airport::_from_name(const string& s) {
    auto result = Database::Client()->get_airport_by_name->Execute(s.c_str());
    CHECK_SUCCESS(result);
    auto chunk = result->Fetch();
    if (!chunk || chunk->size() == 0) return Airport();

    return Airport(*chunk, 0);
}

Airport Airport::_from_all(const string& s) {
    auto result = Database::Client()->get_airport_by_all->Execute(s.c_str());
    CHECK_SUCCESS(result);
    auto chunk = result->Fetch();
    if (!chunk || chunk->size() == 0) return Airport();

    return Airport(*chunk, 0);
}


std::vector<Airport> Airport::_suggest_iata(const string& s) {
    std::vector<Airport> airports;
    auto result = Database::Client()->suggest_airport_by_iata->Execute(s.c_str());
    CHECK_SUCCESS(result);
    while (auto chunk = result->Fetch()) {
        for (idx_t i = 0; i < chunk->size(); i++) {
            airports.emplace_back(*chunk, i);
        }
    }
    return airports;
}

std::vector<Airport> Airport::_suggest_icao(const string& s) {
    std::vector<Airport> airports;
    auto result = Database::Client()->suggest_airport_by_icao->Execute(s.c_str());
    CHECK_SUCCESS(result);
    while (auto chunk = result->Fetch()) {
        for (idx_t i = 0; i < chunk->size(); i++) {
            airports.emplace_back(*chunk, i);
        }
    }
    return airports;
}

std::vector<Airport> Airport::_suggest_name(const string& s) {
    std::vector<Airport> airports;
    auto result = Database::Client()->suggest_airport_by_name->Execute(s.c_str());
    CHECK_SUCCESS(result);
    while (auto chunk = result->Fetch()) {
        for (idx_t i = 0; i < chunk->size(); i++) {
            airports.emplace_back(*chunk, i);
        }
    }
    return airports;
}

// TODO: remove duplicates
std::vector<Airport> Airport::_suggest_all(const string& s) {
    std::vector<Airport> airports;
    std::vector<AirportSuggestion> suggestions;
    for (auto& stmt : {
        Database::Client()->suggest_airport_by_iata.get(),
        Database::Client()->suggest_airport_by_icao.get(),
        Database::Client()->suggest_airport_by_name.get(),
    }) {
        auto result = stmt->Execute(s.c_str());
        CHECK_SUCCESS(result);
        auto chunk = result->Fetch();
        if (!chunk || chunk->size() == 0) continue;

        for (idx_t i = 0; i < chunk->size(); i++) {
            suggestions.emplace_back(
                Airport(*chunk, i),
                chunk->GetValue(13, i).GetValue<double>()
            );
        }
    }

    std::partial_sort(suggestions.begin(), suggestions.begin() + 5, suggestions.end(), [](const AirportSuggestion& a, const AirportSuggestion& b) {
        return a.score > b.score;
    });

    for (size_t i = 0; i < std::min<size_t>(5, suggestions.size()); i++) {
        airports.push_back(std::move(suggestions[i].ap));
    }

    return airports;
}

Airport Airport::from_auto(string s) {
    Airport ap;
    Airport::SearchType search_type = Airport::SearchType::ALL;

    string s_upper = s;
    std::transform(s_upper.begin(), s_upper.end(), s_upper.begin(), ::toupper);

    // search airports
    if (s_upper.substr(0, 5) == "IATA:") {
        search_type = Airport::SearchType::IATA;
        s = s_upper.substr(5);
        ap = Airport::_from_iata(s);
    } else if (s_upper.substr(0, 5) == "ICAO:") {
        search_type = Airport::SearchType::ICAO;
        s = s_upper.substr(5);
        ap = Airport::_from_icao(s);
    } else if (s_upper.substr(0, 5) == "NAME:") {
        search_type = Airport::SearchType::NAME;
        s = s_upper.substr(5);
        ap = Airport::_from_name(s);
    } else if (s_upper.substr(0, 3) == "ID:") {
        search_type = Airport::SearchType::ID;
        s = s.substr(3);
        try {
            ap = Airport::_from_id(std::stoi(s));
        } catch (std::invalid_argument& e) {
        } catch (std::out_of_range& e) { // silently skipping, empty suggestions will be thrown later on
        }
    } else if (s_upper.substr(0, 4) == "ALL:") {
        s = s_upper.substr(4);
        ap = Airport::_from_all(s);
    } else {
        s = s_upper;
        ap = Airport::_from_all(s);
    }

    if (ap.valid) return ap;
    
    // empty airports, suggest and throw error
    std::vector<Airport> airports;
    switch (search_type) {
        case Airport::SearchType::ALL:
            airports = Airport::_suggest_all(s);
            break;
        case Airport::SearchType::IATA:
            airports = Airport::_suggest_iata(s);
            break;
        case Airport::SearchType::ICAO:
            airports = Airport::_suggest_icao(s);
            break;
        case Airport::SearchType::NAME:
            airports = Airport::_suggest_name(s);
            break;
    }

    throw AirportNotFoundException(search_type, s, airports);
}

const string Airport::repr() {
    return "<Airport id=" + std::to_string(id) + " name='" + name + "' fullname='" + fullname + "' country='" + country + "' continent='" + continent + "' iata='" + iata + "' icao='" + icao + "' lat=" + std::to_string(lat) + " lng=" + std::to_string(lng) + " rwy=" + std::to_string(rwy) + " market=" + std::to_string(market) + " hub_cost=" + std::to_string(hub_cost) + " rwy_codes='" + rwy_codes + "'>";
}