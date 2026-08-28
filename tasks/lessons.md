# Lessons Learned

Living document of corrections, surprises, and rules-of-thumb learned from the program. Update after every non-trivial mistake or correction.

## Format

```
## YYYY-MM-DD — Short title

**What happened:**
<description of the incident, mistake, or correction>

**Why:**
<root cause>

**Rule going forward:**
<concrete, actionable rule to prevent recurrence>
```

## Entries

## 2026-08-28 — Bisection branches both monotonic, but sign rule must match f(lo)

**What happened:**
`mach_from_area_ratio` returned the upper bound (Mach = 20.0) for any
supersonic A/A* > 1. The supersonic branch's bisection had the lo/hi
update inverted: when f(mid) was positive, it set `lo = mid` (moving the
search upward, away from the root).

**Why:**
The supersonic A/A* function is monotonically *increasing* in M, while
the subsonic branch is monotonically *decreasing*. Both branches have a
single root per A/A* > 1, but the bisection update direction depends on
which branch you're on. The original code had different update rules
per branch and the supersonic one was wrong. Worse, the test suite
didn't catch it because the `area_mach_ratio` inverse round-trip test
used the result of `area_mach_ratio` itself (which would obviously
round-trip) rather than independently checking the Mach value.

**Rule going forward:**
When writing bisection on a monotonic function: f(mid) having the same
sign as f(lo) means the root is between mid and hi, regardless of branch.
Both branches can use the same `f > 0: hi = mid / f < 0: lo = mid` rule.
Always test the bisection with explicit Mach value assertions, not just
round-trip through the forward function.

## 2026-08-28 — Derive choked mass flow from first principles before coding

**What happened:**
The choked mass flow formula in `analyze_nozzle` had a stray
`(2/(gamma+1))^((gamma+1)/(gamma-1))` factor inside the sqrt. This
gave mass flow ~50% of the correct value, which propagated into Isp
calculations that looked ~40% too high.

**Why:**
I wrote the formula by combining p_star, t_star, and the standard
choked-flow expression without checking that the exponents simplified
correctly. The algebraic identity (p_star / sqrt(t_star)) equals
(2/(gamma+1))^((gamma+1)/(2*(gamma-1))) was missed, so the exponent
ended up doubled.

**Rule going forward:**
When combining multiple standard formulas (p_star, t_star, choked flow),
substitute the definitions and simplify before writing code. Verify
the result against a known case: gamma=1.4, T=300K, R=287, At=1e-4
should give m_dot = 0.529 kg/s at Pc=1 MPa. If the formula gives
something else, it's wrong.

## 2026-08-28 — Validate example data against physical models

**What happened:**
The example `example_thrust.csv` had peak thrust of 150 N for a 50 g
motor, giving Isp = 740 s — physically impossible for KNSU
(realistic: 110-160 s). The data was written by hand without checking
that it was consistent with the chamber pressure and throat area in
the matching `example_pressure.csv`.

**Why:**
Example data should be realistic enough to demonstrate the tools
without misleading the user. Hand-writing "shaped" thrust curves
without computing total impulse first leads to nonsense numbers that
test fine but teach wrong intuition.

**Rule going forward:**
Before writing any example CSV, compute the expected total impulse
(Isp * mass) and verify the curve area is consistent. For propellant
mass M and target Isp, total impulse = M * Isp * g0. Burn time and
profile shape then constrain peak thrust.
