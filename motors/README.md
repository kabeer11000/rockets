# Motors

Motor designs, grain geometry, nozzle specifications, casing details.

## Anatomy

A solid rocket motor has four main components:

1. **Casing** — contains combustion pressure (cardboard, fiberglass, aluminum)
2. **Propellant grain** — shaped charge that determines burn profile
3. **Nozzle** — accelerates exhaust gases (convergent-divergent for supersonic flow)
4. **Ignition system** — initiates combustion (e-match + pyrogen or similar)

## Grain geometries

Common amateur grain designs:

- **BATES** — multiple cylindrical grains stacked; end-burning + radial-burning faces. Simplest to cast.
- **Star** — cross or multi-pointed star inside cylinder; progressive burn.
- **End-burner** — only the end face burns; long duration, low thrust.
- **Core-burner** — hollow cylinder, burning inward; high thrust, shorter duration.

For KNSU/KNDX first motor, **BATES** is simplest to cast and most forgiving.

## Key parameters

| Parameter | Symbol | Notes |
|---|---|---|
| Throat diameter | Dt | Primary throttle control; smaller = more thrust, more pressure |
| Exit diameter | De | Determines expansion ratio |
| Expansion ratio | ε = (De/Dt)² | >6 for sea-level optimization, but sea-level losses are real |
| Chamber pressure | Pc | For KNSU: 500-1500 PSI typical |
| Burn rate | r | Function of pressure: r = a * P^n (Vieille's law) |
| Grain web thickness | web | Determines burn time |
| Port-to-throat ratio | Port/Dt | Affects grain burn progression |

## Design approach

1. Estimate propellant mass and target burn time
2. Pick grain geometry and web thickness to match burn time
3. Calculate throat diameter for desired chamber pressure
4. Size casing for peak pressure (with safety factor, typically 2-3x)
5. Validate with static test

## Nozzle materials

- **Phenolic** (paper-reinforced resin) — easiest to machine, common in amateur motors
- **Graphite** — high temperature resistance, machined from rod stock
- **Steel** — durable but heavier; machined or cast
- **Ceramic** — best temperature performance, harder to source

For KNSU, phenolic or graphite is sufficient. Steel is overkill.

## Motor design files

Each motor should have its own folder:

```
motors/
  motor-001/
    README.md             # design rationale, expected performance
    dimensions.md         # all dimensions
    parts.md              # sourcing list for components
    static-test-results.md  # link to static-tests/
```

## Safety margins

- Case burst pressure should be at minimum 2x expected max operating pressure
- Always include mechanical vent path or burst disc as last-resort relief
- Nozzle retention: epoxied or mechanically retained, never friction-fit alone
