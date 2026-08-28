# Propellants

Recipes, chemistry, sourcing, and safety data for each propellant used in the program.

## Active propellants

### KNSU (Potassium Nitrate + Sucrose)
Classic amateur rocket propellant. Easy to source, melt-castable, low chamber pressure (~500-1000 PSI), forgiving.

**Ratio (oxidizer-rich, by mass):** 65% KNO3 / 35% sucrose (most common starting point)

**Chemistry:**
- Oxidizer: KNO3 decomposes to release oxygen
- Fuel: C12H22O11 + O2 → CO2 + H2O
- Products: CO2, H2O, N2, K2O (potassium oxide smoke)
- Theoretical Isp: ~120-150 s (depending on conditions)

**Sourcing:**
- KNO3: hardware store "stump remover" (verify 100% KNO3, no additives)
- Sucrose: grocery store table sugar

**Processing:** melt-cast only. Never grind dry KNO3 and sugar together — friction-sensitive.

**Safety:**
- Autoignition: ~400°C
- Direct flame on mixture: kitchen fires. Use double boiler, water bath between heat source and pot.
- Confined without vent: detonation risk. Always ensure nozzle path is clear.

### KNDX (Potassium Nitrate + Dextrose)
Variant of KNSU with dextrose (corn sugar) replacing sucrose. Slightly cleaner burn, less hygroscopic.

**Ratio:** 65/35 KNO3/dextrose by mass

**Sourcing:**
- Dextrose: brewing supply stores, pharmacies (glucose tablets), corn sugar
- Slightly harder to find than sucrose but better properties

**Differences from KNSU:**
- Less moisture absorption
- Slightly higher burn rate
- Cleaner exhaust (less smoke)

## Planned propellants

### APCP (Ammonium Perchlorate + Aluminum + HTPB)
Composite propellant. Much higher performance (~250 s Isp), but requires:
- Ammonium perchlorate (regulated, sourcing is hard)
- Spherical aluminum powder (fine, <50 micron)
- HTPB binder (with IPDI or similar curative)
- Pellet press or careful casting techniques

### Hybrid (N2O or LOX + solid fuel)
Liquid or gaseous oxidizer over a solid fuel grain. Significantly more complex than solids due to oxidizer handling.

### Liquid bi-propellant
Highest performance but orders of magnitude harder. Cryogenic handling, turbopumps (or pressure-fed), ignition systems. Deferred until solid program is mature.

## Safety

Always store oxidizers and fuels **separately** until ready to mix. Mix only the quantity you intend to use immediately. See `docs/safety.md`.

## Folder structure

Each propellant should have its own subfolder as work develops:

```
propellants/
  KNSU/
    recipe.md
    burn-rate.md
    notes.md
  KNDX/
    ...
```
