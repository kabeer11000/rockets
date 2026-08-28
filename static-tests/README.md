# Static Tests

Ground-based motor firings, instrumentation, and data analysis. **Every motor must be static tested before flight.**

## Test rig requirements

- **Load cell** — measure thrust (500 kg range sufficient for KNSU motors)
- **Pressure transducer** — measure chamber pressure (5000 PSI range typical)
- **High-speed camera** — minimum 240 fps, ideally 1000+ fps for ignition transient
- **Thermocouples** — optional, for casing temperature data
- **Data acquisition** — Arduino + HX711 (load cell) + analog input (pressure), logged to SD card or streamed to laptop

## Setup

```
[Ignition] --long cable--> [Motor on stand] --load cell--> [Fixed frame]
                              |--- pressure transducer --> DAQ
                              |--- high-speed camera --->
```

**Critical:** operator must be far enough away that motor failure (case rupture, shrapnel) cannot reach them. Minimum 10-20 m for small motors, more for larger.

## Test procedure

1. Mount motor to stand, verify all fasteners
2. Connect pressure transducer, verify reading
3. Calibrate load cell (known mass, record offset)
4. Connect igniter, run wire to safe distance
5. Start data acquisition
6. Start high-speed camera
7. Arm ignition
8. Stand clear, verify clear area
9. Fire
10. After motor cooldown, retrieve data, photograph results

## Data format

Each test gets its own folder:

```
static-tests/
  test-001/
    README.md           # conditions, motor ID, expected vs actual
    thrust.csv          # timestamp, thrust (N)
    pressure.csv        # timestamp, pressure (PSI)
    camera/             # video frames or video file (use Git LFS)
    plots/
      thrust-curve.png
      pressure-curve.png
      combined.png
```

CSV format:

```
time_s,thrust_n
0.000,0.0
0.001,12.3
...
```

## Analysis scripts

- `simulation/thrust_fit.py` — fits burn rate coefficient and exponent from pressure data
- `simulation/isp_calc.py` — integrates thrust over burn time, divides by propellant mass
- `simulation/plot_test.py` — generates standard plots from CSV

## Safety

- **Never fire unconfined.** Always mount to stand.
- **Never fire near people.** Designated range only.
- **Never fire near flammable material.** Vegetation, structures, vehicles.
- **Inspect casing post-fire.** Look for burn-through, deformation, evidence of over-pressure.
