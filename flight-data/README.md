# Flight Data

Logs from actual rocket flights — altitude, acceleration, GPS, recovery system deployment.

## Sensors

**Altimeters** (apogee detection + data logging):
- Featherweight Raven / Stratologger
- Eggtimer altimeters
- DIY: Arduino + BMP280 / MS5607 barometer

**Accelerometers** (high-G for boost phase):
- DIY: Arduino + ADXL375 (200g) or similar

**GPS trackers** (recovery aid):
- DIY: Arduino + u-blox module
- Commercial: Eggfinder, Featherweight GPS

**Recovery deployment:**
- Black powder or CO2 ejection
- Drogue + main parachute (two-stage recovery)

## Data format

```
flight-data/
  flight-001/
    README.md         # conditions, vehicle, motor, result
    altitude.csv      # timestamp, altitude_m
    accel.csv         # timestamp, accel_g
    gps.csv           # timestamp, lat, lon, alt
    plots/
      altitude-vs-time.png
      velocity-vs-time.png
```

## Workflow

1. Design flight in OpenRocket, predict apogee and acceleration profile
2. Build vehicle with chosen recovery system
3. Static test motor (separate, in `static-tests/`)
4. Integrate flight hardware, verify sensors working on the pad
5. Launch, recover airframe and electronics
6. Download data, plot, compare to simulation
7. Update airframe design if discrepancies

## Safety

- Never recover near people without coordination
- Track landing zone, GPS-tag every flight
- File FAA waiver (US) or equivalent for high-altitude flights in or near restricted airspace
