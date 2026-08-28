# Firmware

Embedded code for data loggers, igniters, and sensors.

## Platform

**Arduino** (Uno, Nano, or Pro Micro) for most applications.
- Simple, well-documented, large ecosystem
- 16 MHz AVR sufficient for most logging tasks

**Alternatives:**
- ESP32 (WiFi / Bluetooth for live telemetry)
- Teensy (faster, more RAM, more analog inputs)
- STM32 (for high-speed applications)

## Common modules

### Load cell interface
- HX711 amplifier + 24-bit ADC
- Sample rate: 10-80 Hz typical
- Output: force in N (calibrated against known mass)

### Pressure transducer
- 0-5000 PSI strain-gauge transducer (e.g., Honeywell, US186 series)
- Amplifier + Arduino analog input
- Sample rate: 100+ Hz recommended for transient capture

### Altimeter
- BMP280 / MS5607 barometer
- I2C interface
- Sample at 50+ Hz

### Ignition system
- E-match + MOSFET driven by Arduino
- **Always** with safety interlock (physical switch + relay)
- **Never** trigger ignition without remote signal — physical isolation from operator

## Code structure

```
firmware/
  static-test-rig/        # Arduino code for DAQ on test stand
    src/
    README.md
  altimeter/              # Flight altimeter
    src/
    README.md
  igniter/                # Safe ignition controller with interlocks
    src/
    README.md
```

## Safety

- Ignition code **must** require physical arm + remote trigger
- Test ignition logic without pyrogen or propellant first
- All high-current circuits fused
- Battery isolation when not in use

## TODO

- [ ] Static test rig: HX711 + pressure transducer + SD card logging
- [ ] Altimeter: barometer + apogee detection + pyro channel
- [ ] Igniter: physical safety switch + remote arm/fire
