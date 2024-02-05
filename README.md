# ![logo](src/am4bot/assets/img/logo-small.png) am4bot

[![](https://dcbadge.vercel.app/api/server/4tVQHtf?style=flat)](https://discord.gg/4tVQHtf) [![CI](https://github.com/cathaypacific8747/am4bot/actions/workflows/ci.yml/badge.svg)](https://github.com/cathaypacific8747/am4bot/actions/workflows/ci.yml)

A discord bot for the game [Airline Manager 4](airlinemanager.com), used on our [server](https://discord.gg/4tVQHtf).

Our bot is currently running legacy code under [`src-old`](./src-old/) and is being rewritten completely:
- [x] core calculations rewritten in C++ for bettter performance ([`src/am4utils`](./src/am4utils/))
- [ ] api written in Python ([`src/am4api (under construction)`](./src/am4api/))
- [ ] discord bot written in Python ([`src/am4bot (under construction)`](./src/am4bot/))
- [ ] [`am4help.com`](https://am4help.com/) utilising this codebase ([`src/am4web (under construction)`](./src/am4web/)to be developed)

![overview](src/am4bot/assets/img/overview.drawio.svg)


## Features
Old bot:
- calculates essential statistics
    - most distance-efficient stopovers
    - route demands, best seat configurations, best ticket prices, estimated income
    - player rank, mode, achievements, fleet
    - alliance rank, share value, contribution
    - aircraft characteristics and profit
    - airport characteristics
- CSV export for route queries
- fuel/CO2 notifications
- aircraft characteristics comparisons
- internal *Star Alliance* tools (now disbanded)
    - adding competitor alliances to watchlist
    - alliance comparisons over time: value, contribution/day, rate of changes
    - realtime alliance-member comparisons: SV/contribution distribution
    - member tracking: cheat detection tools, departure pattern identification

## AM4Utils Development
Recommended: C++17 compliant compiler, python3.9+

### C++ debug executable
install [vcpkg](https://vcpkg.io/en/getting-started.html) and set envvar `VCPKG_ROOT`
```sh
sudo apt-get install build-essential bison flex
vcpkg install arrow
# optionally install vtune for profiling

cd src/am4utils
mkdir build
cd build
cmake .. && cmake --build . --target _core_executable && ./_core_executable
```

### Python bindings
```sh
sudo apt-get install python3-dev
virtualenv .venv
source .venv/bin/activate

python3 -m pip install --verbose "src/am4utils/.[dev]" --config-settings=cmake.define.COPY_DATA=1
pytest
cd src/am4utils
python3 generate-stubs.py
pip3 uninstall am4utils -y
```
### Build wheel
```sh
mkdir wheelhouse
python3 -m pip wheel . --wheel-dir=wheelhouse no-deps -v
pip install wheelhouse/am4utils-*.whl --force-reinstall
```

## AM4 Bot development
```bash
pip3 install --verbose ".[dev]"
cp config.example.json config.production.json
PRODUCTION=1 python3 main.py
```

## Commands (for old bot - to be updated!)

### Public
- `$route|stop <airport> <airport> <aircraft> [flights_per_day] [reputation]`: finds the best route between two airports
  
  ![route](src/am4bot/assets/img/route.png)
- `$routes <airport> <aircraft> <max_distance> <flights_per_day> [reputation]`: finds the best destinations from a certain airport, sorted by decreasing estimated income
  
  ![routes](src/am4bot/assets/img/routes.png)
- `$user [player]`: shows player (and associated alliance if found) statistics
  
  ![user](src/am4bot/assets/img/user.png)
- `$fleet [player]`: shows player fleet and estimated income
  
  ![fleet](src/am4bot/assets/img/fleet.png)
- `$info <aircraft>`: shows basic aircraft information and rough profit estimations
  
  ![info](src/am4bot/assets/img/info.png)
- `$compare <aircraft>`: compares two aircrafts
  
  ![compare](src/am4bot/assets/img/compare.png)
- `$search <aircraft>`: finds the associated aircraft shortname for aircraft commands
  
  ![search](src/am4bot/assets/img/search.png)
- `$airport <airport>`: shows airport information
  
  ![airport](src/am4bot/assets/img/airport.png)
- `$price f[fuel_price] c[co2_price]`: notifies everyone for the fuel price
  
  ![price](src/am4bot/assets/img/price.png)

### Internal Alliance Tools
- `$memberCompare <player> <player>`: compares descending structure of contribution/day and SV
  
  ![member-compare](src/am4bot/assets/img/member-compare.png)
- `$alliance <alliance>`: shows AV progression and d(AV)/dt.
  
  ![alliance](src/am4bot/assets/img/alliance.png)
- `$allianceCompare <alliance> <alliance>`: compares AV progression and gap difference over time, shows 48h/12h-average contribution/day graphs
  
  ![alliance-compare](src/am4bot/assets/img/alliance-compare.png)
- `$member <player> [player[]]` shows contribution/day, total contribution and SV history for 1+ members
  
  ![member](src/am4bot/assets/img/member.png)
- `$actions <player> [maxResults]`: shows log of estimated departures, contributions and income
  
  ![member-compare](src/am4bot/assets/img/member-compare.png)
- `$watchlist [add|+, remove|rm|-] [alliance]`: shows, adds or remove alliance(s) to the watchlist