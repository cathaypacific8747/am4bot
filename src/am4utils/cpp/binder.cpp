#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "include/db.hpp"
#include "include/game.hpp"
#include "include/ticket.hpp"
#include "include/demand.hpp"

#include "include/airport.hpp"
#include "include/aircraft.hpp"
#include "include/route.hpp"

#ifdef VERSION_INFO
    string version = MACRO_STRINGIFY(VERSION_INFO);
#else
    string version = "dev";
#endif

namespace py = pybind11;
using namespace pybind11::literals;
using std::string;
using std::shared_ptr;

PYBIND11_MODULE(_core, m) {
    py::module_ m_db = m.def_submodule("db");
    py::module_ m_game = m.def_submodule("game");
    py::module_ m_ticket = m.def_submodule("ticket");
    py::module_ m_demand = m.def_submodule("demand");
    py::module_ m_ac = m.def_submodule("aircraft");
    py::module_ m_ap = m.def_submodule("airport");
    py::module_ m_route = m.def_submodule("route");

    /*** DATABASE ***/
    m_db
        .def("init", &init)
        .def("_debug_query", &_debug_query);

    py::register_exception<DatabaseException>(m_db, "DatabaseException");

    /*** GAME ***/
    py::class_<User> user_class(m_game, "User");
    py::enum_<User::GameMode>(user_class, "GameMode")
        .value("EASY", User::GameMode::EASY)
        .value("REALISM", User::GameMode::REALISM);
    user_class
        .def(py::init<>())
        .def_readonly("id", &User::id)
        .def_readonly("game_id", &User::game_id)
        .def_readonly("ign", &User::ign)
        .def_readonly("game_mode", &User::game_mode)
        .def_readonly("l_training", &User::l_training)
        .def_readonly("h_training", &User::h_training)
        .def_readonly("fuel_price", &User::fuel_price)
        .def_readonly("co2_price", &User::co2_price)
        .def_readonly("fuel_training", &User::fuel_training)
        .def_readonly("co2_training", &User::co2_training)
        .def_readonly("override_load", &User::override_load)
        .def_readonly("load", &User::load)
        .def("__repr__", &User::repr);
    
    py::class_<Campaign> campaign_class(m_game, "Campaign");
    py::enum_<Campaign::Airline>(campaign_class, "Airline")
        .value("C4_4HR", Campaign::Airline::C4_4HR).value("C4_8HR", Campaign::Airline::C4_8HR).value("C4_12HR", Campaign::Airline::C4_12HR).value("C4_16HR", Campaign::Airline::C4_16HR).value("C4_20HR", Campaign::Airline::C4_20HR).value("C4_24HR", Campaign::Airline::C4_24HR)
        .value("C3_4HR", Campaign::Airline::C3_4HR).value("C3_8HR", Campaign::Airline::C3_8HR).value("C3_12HR", Campaign::Airline::C3_12HR).value("C3_16HR", Campaign::Airline::C3_16HR).value("C3_20HR", Campaign::Airline::C3_20HR).value("C3_24HR", Campaign::Airline::C3_24HR)
        .value("C2_4HR", Campaign::Airline::C2_4HR).value("C2_8HR", Campaign::Airline::C2_8HR).value("C2_12HR", Campaign::Airline::C2_12HR).value("C2_16HR", Campaign::Airline::C2_16HR).value("C2_20HR", Campaign::Airline::C2_20HR).value("C2_24HR", Campaign::Airline::C2_24HR)
        .value("C1_4HR", Campaign::Airline::C1_4HR).value("C1_8HR", Campaign::Airline::C1_8HR).value("C1_12HR", Campaign::Airline::C1_12HR).value("C1_16HR", Campaign::Airline::C1_16HR).value("C1_20HR", Campaign::Airline::C1_20HR).value("C1_24HR", Campaign::Airline::C1_24HR)
        .value("NONE", Campaign::Airline::NONE);
    py::enum_<Campaign::Eco>(campaign_class, "Eco")
        .value("C_4HR", Campaign::Eco::C_4HR).value("C_8HR", Campaign::Eco::C_8HR).value("C_12HR", Campaign::Eco::C_12HR).value("C_16HR", Campaign::Eco::C_16HR).value("C_20HR", Campaign::Eco::C_20HR).value("C_24HR", Campaign::Eco::C_24HR)
        .value("NONE", Campaign::Eco::NONE);
    campaign_class
        .def_readonly("pax_activated", &Campaign::pax_activated)
        .def_readonly("cargo_activated", &Campaign::cargo_activated)
        .def_readonly("eco_activated", &Campaign::eco_activated)
        .def_static("Default", &Campaign::Default)
        .def_static("parse", &Campaign::parse, "s"_a)
        .def("estimate_pax_reputation", &Campaign::estimate_pax_reputation, "base_reputation"_a = 45)
        .def("estimate_cargo_reputation", &Campaign::estimate_cargo_reputation, "base_reputation"_a = 45);


    /*** TICKET ***/
    py::class_<PaxTicket>(m_ticket, "PaxTicket")
        .def_readonly("y", &PaxTicket::y)
        .def_readonly("j", &PaxTicket::j)
        .def_readonly("f", &PaxTicket::f)
        .def_static("from_optimal", &PaxTicket::from_optimal, "distance"_a, py::arg_v("game_mode", User::GameMode::EASY, "am4utils._core.game.User.GameMode")) // https://pybind11.readthedocs.io/en/stable/advanced/functions.html?highlight=default%20argument#default-arguments-revisited
        .def("__repr__", &PaxTicket::repr);

    py::class_<CargoTicket>(m_ticket, "CargoTicket")
        .def_readonly("l", &CargoTicket::l)
        .def_readonly("h", &CargoTicket::h)
        .def_static("from_optimal", &PaxTicket::from_optimal, "distance"_a, py::arg_v("game_mode", User::GameMode::EASY, "am4utils._core.game.User.GameMode"))
        .def("__repr__", &CargoTicket::repr);
    
    py::class_<VIPTicket>(m_ticket, "VIPTicket")
        .def_readonly("y", &VIPTicket::y)
        .def_readonly("j", &VIPTicket::j)
        .def_readonly("f", &VIPTicket::f)
        .def_static("from_optimal", &VIPTicket::from_optimal, "distance"_a)
        .def("__repr__", &VIPTicket::repr);
    
    py::class_<Ticket>(m_ticket, "Ticket")
        .def_readonly("pax_ticket", &Ticket::pax_ticket)
        .def_readonly("cargo_ticket", &Ticket::cargo_ticket)
        .def_readonly("vip_ticket", &Ticket::vip_ticket);
    

    /*** DEMAND ***/
    py::class_<PaxDemand>(m_demand, "PaxDemand")
        .def(py::init<>())
        .def(py::init<int, int, int>(), "y"_a, "j"_a, "f"_a)
        .def_readonly("y", &PaxDemand::y)
        .def_readonly("j", &PaxDemand::j)
        .def_readonly("f", &PaxDemand::f)
        .def("__repr__", &PaxDemand::repr);
    
    py::class_<CargoDemand>(m_demand, "CargoDemand")
        .def(py::init<>())
        .def(py::init<int, int>(), "l"_a, "h"_a)
        .def(py::init<const PaxDemand&>(), "pax_demand"_a)
        .def_readonly("l", &CargoDemand::l)
        .def_readonly("h", &CargoDemand::h)
        .def("__repr__", &CargoDemand::repr);


    /*** AIRCRAFT ***/
    py::class_<Aircraft, shared_ptr<Aircraft>> ac_class(m_ac, "Aircraft");
    py::enum_<Aircraft::Type>(ac_class, "Type")
        .value("PAX", Aircraft::Type::PAX)
        .value("CARGO", Aircraft::Type::CARGO)
        .value("VIP", Aircraft::Type::VIP);
    ac_class
        .def_readonly("id", &Aircraft::id)
        .def_readonly("shortname", &Aircraft::shortname)
        .def_readonly("manufacturer", &Aircraft::manufacturer)
        .def_readonly("name", &Aircraft::name)
        .def_readonly("type", &Aircraft::type)
        .def_readonly("priority", &Aircraft::priority)
        .def_readonly("eid", &Aircraft::eid)
        .def_readonly("ename", &Aircraft::ename)
        .def_readonly("speed", &Aircraft::speed)
        .def_readonly("fuel", &Aircraft::fuel)
        .def_readonly("co2", &Aircraft::co2)
        .def_readonly("cost", &Aircraft::cost)
        .def_readonly("capacity", &Aircraft::capacity)
        .def_readonly("rwy", &Aircraft::rwy)
        .def_readonly("check_cost", &Aircraft::check_cost)
        .def_readonly("range", &Aircraft::range)
        .def_readonly("ceil", &Aircraft::ceil)
        .def_readonly("maint", &Aircraft::maint)
        .def_readonly("pilots", &Aircraft::pilots)
        .def_readonly("crew", &Aircraft::crew)
        .def_readonly("engineers", &Aircraft::engineers)
        .def_readonly("technicians", &Aircraft::technicians)
        .def_readonly("img", &Aircraft::img)
        .def_readonly("wingspan", &Aircraft::wingspan)
        .def_readonly("length", &Aircraft::length)
        .def_readonly("valid", &Aircraft::valid)
        .def("__repr__", &Aircraft::repr);
    py::enum_<Aircraft::SearchType>(ac_class, "SearchType")
        .value("ALL", Aircraft::SearchType::ALL)
        .value("ID", Aircraft::SearchType::ID)
        .value("SHORTNAME", Aircraft::SearchType::SHORTNAME)
        .value("NAME", Aircraft::SearchType::NAME);
    py::class_<Aircraft::ParseResult>(ac_class, "ParseResult")
        .def(py::init<Aircraft::SearchType, const std::string&>())
        .def_readonly("search_type", &Aircraft::ParseResult::search_type)
        .def_readonly("search_str", &Aircraft::ParseResult::search_str);
    py::class_<Aircraft::SearchResult>(ac_class, "SearchResult")
        .def(py::init<shared_ptr<Aircraft>, Aircraft::ParseResult>())
        .def_readonly("ac", &Aircraft::SearchResult::ac)
        .def_readonly("parse_result", &Aircraft::SearchResult::parse_result);
    py::class_<Aircraft::Suggestion>(ac_class, "Suggestion")
        .def(py::init<shared_ptr<Aircraft>, double>())
        .def_readonly("ac", &Aircraft::Suggestion::ac)
        .def_readonly("score", &Aircraft::Suggestion::score);
    ac_class
        .def_static("search", &Aircraft::search, "s"_a)
        .def_static("suggest", &Aircraft::suggest, "s"_a);
    
    /*** PURCHASED AIRCRAFT ***/
    py::class_<PaxConfig> pc_class(m_ac, "PaxConfig");
    py::enum_<PaxConfig::Algorithm>(pc_class, "Algorithm")
        .value("FJY", PaxConfig::Algorithm::FJY).value("FYJ", PaxConfig::Algorithm::FYJ)
        .value("JFY", PaxConfig::Algorithm::JFY).value("JYF", PaxConfig::Algorithm::JYF)
        .value("YJF", PaxConfig::Algorithm::YJF).value("YFJ", PaxConfig::Algorithm::YFJ)
        .value("NONE", PaxConfig::Algorithm::NONE);
    pc_class
        .def_readonly("y", &PaxConfig::y)
        .def_readonly("j", &PaxConfig::j)
        .def_readonly("f", &PaxConfig::f)
        .def_readonly("valid", &PaxConfig::valid)
        .def_readonly("algorithm", &PaxConfig::algorithm);

    py::class_<CargoConfig> cc_class(m_ac, "CargoConfig");
    py::enum_<CargoConfig::Algorithm>(cc_class, "Algorithm")
        .value("L", CargoConfig::Algorithm::L).value("H", CargoConfig::Algorithm::H)
        .value("NONE", CargoConfig::Algorithm::NONE);
    cc_class
        .def_readonly("l", &CargoConfig::l)
        .def_readonly("h", &CargoConfig::h)
        .def_readonly("valid", &CargoConfig::valid)
        .def_readonly("algorithm", &CargoConfig::algorithm);

    py::class_<PurchasedAircraft, shared_ptr<PurchasedAircraft>, Aircraft> p_ac_class(m_ac, "PurchasedAircraft");
    py::class_<PurchasedAircraft::Config>(p_ac_class, "Config")
        .def_readonly("pax_config", &PurchasedAircraft::Config::pax_config)
        .def_readonly("cargo_config", &PurchasedAircraft::Config::cargo_config);
    p_ac_class
        .def_readonly("config", &PurchasedAircraft::config)
        .def("__repr__", &PurchasedAircraft::repr);


    /*** AIRPORT ***/
    py::class_<Airport, shared_ptr<Airport>> ap_class(m_ap, "Airport");
    ap_class
        .def_readonly("id", &Airport::id)
        .def_readonly("name", &Airport::name)
        .def_readonly("fullname", &Airport::fullname)
        .def_readonly("country", &Airport::country)
        .def_readonly("continent", &Airport::continent)
        .def_readonly("iata", &Airport::iata)
        .def_readonly("icao", &Airport::icao)
        .def_readonly("lat", &Airport::lat)
        .def_readonly("lng", &Airport::lng)
        .def_readonly("rwy", &Airport::rwy)
        .def_readonly("market", &Airport::market)
        .def_readonly("hub_cost", &Airport::hub_cost)
        .def_readonly("rwy_codes", &Airport::rwy_codes)
        .def_readonly("valid", &Airport::valid)
        .def("__repr__", &Airport::repr);
    
    py::enum_<Airport::SearchType>(ap_class, "SearchType")
        .value("ALL", Airport::SearchType::ALL)
        .value("IATA", Airport::SearchType::IATA)
        .value("ICAO", Airport::SearchType::ICAO)
        .value("NAME", Airport::SearchType::NAME)
        .value("ID", Airport::SearchType::ID);
    
    py::class_<Airport::ParseResult>(ap_class, "ParseResult")
        .def(py::init<Airport::SearchType, const std::string&>())
        .def_readonly("search_type", &Airport::ParseResult::search_type)
        .def_readonly("search_str", &Airport::ParseResult::search_str);

    py::class_<Airport::SearchResult>(ap_class, "SearchResult")
        .def(py::init<shared_ptr<Airport>, Airport::ParseResult>())
        .def_readonly("ap", &Airport::SearchResult::ap)
        .def_readonly("parse_result", &Airport::SearchResult::parse_result);

    py::class_<Airport::Suggestion>(ap_class, "Suggestion")
        .def(py::init<shared_ptr<Airport>, double>())
        .def_readonly("ap", &Airport::Suggestion::ap)
        .def_readonly("score", &Airport::Suggestion::score);

    ap_class
        .def_static("search", &Airport::search, "s"_a)
        .def_static("suggest", &Airport::suggest, "s"_a);

    /*** ROUTE ***/
    py::class_<AircraftRoute> acr_class(m_route, "AircraftRoute");
    
    py::class_<Route>(m_route, "Route")
        .def_readonly("origin", &Route::origin)
        .def_readonly("destination", &Route::destination)
        .def_readonly("pax_demand", &Route::pax_demand)
        .def_readonly("direct_distance", &Route::direct_distance)
        .def_readonly("valid", &Route::valid)
        .def_static("create", &Route::create, "ap1"_a, "ap2"_a)
        .def("assign", &Route::assign, "ac"_a, "trips_per_day"_a = 1, py::arg_v("user", User(), "am4utils._core.game.User()"))
        .def("__repr__", &Route::repr);
    
    acr_class
        .def_readonly("route", &AircraftRoute::route)
        .def_readonly("aircraft", &AircraftRoute::aircraft)
        .def_readonly("ticket", &AircraftRoute::ticket)
        .def_readonly("income", &AircraftRoute::income)
        .def_static("create", &AircraftRoute::from, "route"_a, "ac"_a, "trips_per_day"_a = 1, py::arg_v("user", User(), "am4utils._core.game.User()"))
        .def("__repr__", &Route::repr);

    m.attr("__version__") = version;
}