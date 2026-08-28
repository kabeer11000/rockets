# Rockets

Home-built amateur rocketry program. Research, design, data, and tooling for solid-propellant motors and small launch vehicles.

## Roadmap

1. **Foundations** — legal/safety baseline, sourcing materials, building a static test stand
2. **First propellant** — KNSU/KNDX (potassium nitrate + sugar). Learn grain geometry, nozzle ratios, burn rate
3. **Iterate** — design motors, static test, log everything, refine
4. **Composite propellants** — APCP-style (ammonium perchlorate + aluminum + binder) once KNSU is dialed in
5. **Airframe + flight** — full vehicle design with commercial motors, then transition to homemade
6. **Advanced** — only after the solid program is mature: hybrids, then liquids

## Repository structure

| Folder | Contents |
|---|---|
| `propellants/` | Propellant chemistry, recipes, burn rate data, sourcing notes |
| `motors/` | Motor designs (grain geometry, nozzle dimensions, casings) |
| `static-tests/` | Raw test data (CSV), analysis scripts, plots |
| `simulation/` | Trajectory and thermochemistry tools |
| `flight-data/` | Altimeter, accelerometer, GPS logs from flights |
| `firmware/` | Embedded code for data loggers, igniters, sensors |
| `docs/` | Safety procedures, references, methodology |
| `tasks/` | Roadmap checklist, lessons learned |

## Tooling

- **Trajectory sim**: [OpenRocket](https://openrocket.info/) (free, Java)
- **Thermochemistry**: [Rocket Propulsion Analysis](https://www.rocketpropulsionanalysis.com/) (free limited edition) or Python with CoolProp
- **Data analysis**: Python — numpy, scipy, matplotlib
- **Versioning**: git, optionally Git LFS for video/large data files

## Status

Pre-flight. Static test rig and first KNSU motor pending. See `tasks/todo.md` for the current checklist.

## Safety

Read `docs/safety.md` before doing anything with propellant. Joining [Tripoli Rocketry Association](https://www.tripoli.org/) or your local equivalent is the single best first step.
