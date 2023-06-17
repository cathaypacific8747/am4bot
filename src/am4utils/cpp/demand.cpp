#include "include/demand.hpp"
#include <cmath>

PaxDemand::PaxDemand() : y(0), j(0), f(0) {};
PaxDemand::PaxDemand(uint16_t y, uint16_t j, uint16_t f) : y(y), j(j), f(f) {};
PaxDemand::PaxDemand(const duckdb::unique_ptr<duckdb::DataChunk>& chunk, idx_t row) :
    y(chunk->GetValue(0, row).GetValue<uint16_t>()),
    j(chunk->GetValue(1, row).GetValue<uint16_t>()),
    f(chunk->GetValue(2, row).GetValue<uint16_t>()) {};

CargoDemand::CargoDemand() : l(0), h(0) {};
CargoDemand::CargoDemand(uint32_t l, uint32_t h) : l(l), h(h) {};
CargoDemand::CargoDemand(const PaxDemand& pax_demand) : l(lround(pax_demand.y / 2.0F) * 1000), h(pax_demand.j * 1000) {};


const string PaxDemand::repr(const PaxDemand& demand) {
    return "<PaxDemand " + to_string(demand.y) + "|" + to_string(demand.j) + "|" + to_string(demand.f) + ">";
};

const string CargoDemand::repr(const CargoDemand& demand) {
    return "<CargoDemand " + to_string(demand.l) + "|" + to_string(demand.h) + ">";
};