# Roadmap Checklist

## Phase 0 — Foundations
- [ ] Read Tripoli Safety Code (or local equivalent)
- [ ] Join Tripoli / UKRA / local rocketry association
- [ ] Verify local laws on amateur motors and propellant storage
- [ ] Identify a legal launch site

## Phase 1 — Sourcing
- [ ] Acquire KNO3 (stump remover, 100% potassium nitrate)
- [ ] Acquire sugar (sucrose) and/or dextrose
- [ ] Source casing material (cardboard tubes, sonotubes)
- [ ] Source nozzle material (phenolic rod, graphite)
- [ ] Acquire epoxy, RTV silicone for sealing
- [ ] Acquire ignition source (e-match + electric initiator, NOT improvised)

## Phase 2 — Static Test Stand
- [ ] Build load cell mount (steel frame, anchored)
- [ ] Wire load cell to data acquisition (Arduino + HX711 or similar)
- [ ] Add pressure transducer to motor case
- [ ] Build remote ignition system (long cable, e-stop)
- [ ] Set up high-speed camera (240 fps minimum)

## Phase 3 — First Motor (KNSU/KNDX)
- [ ] Decide KNSU vs KNDX (KNSU easier to source, KNDX burns cleaner)
- [ ] Pick initial motor dimensions (start small: ~50g propellant, low chamber pressure)
- [ ] Design grain geometry (BATES end-burner is simplest)
- [ ] Cast first motor
- [ ] Static test — log to `static-tests/test-001/`
- [ ] Analyze thrust curve, pressure trace, visual from camera
- [ ] Iterate: adjust nozzle throat, grain, propellant ratio

## Phase 4 — Analysis Tooling
- [x] Python thrust curve fitting script (`simulation/thrust_fit.py`)
- [x] Burn rate calculation from pressure data
- [x] Isp estimation from propellant mass + integrated thrust
- [ ] Nozzle flow / 1D isentropic analysis (`simulation/nozzle_flow.py`) — done
- [ ] Oxygen balance / recipe analysis (`simulation/c_balance.py`) — done
- [ ] Plot library (`static-tests/plots/`)
- [ ] Run pytest once requirements are installed

## Phase 5 — Composite Propellants
- [ ] Source ammonium perchlorate (regulated in some jurisdictions)
- [ ] Source aluminum powder (fine spherical, <50 micron)
- [ ] Source HTPB or alternative binder
- [ ] Acquire or build small pellet press
- [ ] Repeat Phase 3 design/test cycle with composite

## Phase 6 — Airframe and Flight
- [ ] Design airframe around motor (use OpenRocket)
- [ ] Build recovery system (parachute, deployment charge)
- [ ] Integrate commercial motor for first flights
- [ ] Transition to homemade motors in proven airframe

## Phase 7 — Advanced (Optional)
- [ ] Hybrid motor (gaseous oxidizer + solid fuel)
- [ ] Liquid engine (cryogenic or storable bi-prop)

## Status notes

Update this file as items are completed. Significant design choices should be documented in `docs/decisions.md` (to be created when needed).
