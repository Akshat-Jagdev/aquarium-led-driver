# TP-06 — Fish Appearance Test (Qualitative)

> **Goal**: get a real human judgement of whether V0 actually makes
> ornamental fish look better (the primary product goal), and compare
> against a baseline light.
> **Phase**: D (optical validation, customer-research flavour).
> **Time**: ~2 hours per session.

## 1. Prerequisites

- TP-02 passed
- A second, baseline light available for comparison
  (generic LED strip, TICA Color Up if available, or just daylight)
- A tank with at least 3 ornamental fish of different species — colour
  enhancement is most visible on red/orange/blue species
- A small panel of unbiased observers (3–5 people who don't know which
  light is which)

## 2. Test protocol (paired comparison)

For each observer:

1. Seat the observer ~1 m from the tank.
2. Show two lighting conditions in random order:
   - **Condition 1**: V0 profile D (or whichever profile you want to
     test)
   - **Condition 2**: baseline light
3. For each condition, ask the observer to rate on a 1–5 scale:
   - **Overall fish attractiveness** (1 = dull, 5 = stunning)
   - **Colour vividness** (1 = washed out, 5 = vibrant)
   - **Naturalness** (1 = looks like a disco, 5 = looks like a river)
   - **Water clarity** (1 = tinted water, 5 = clear water)
4. Capture the ratings anonymously.

Repeat with 3–5 observers, and 2–3 lighting condition pairs (V0 vs
baseline, V0 profile D vs profile A, V0 vs TICA if available).

## 3. Pass criteria

- [ ] Mean "overall fish attractiveness" rating for V0 ≥ 4.0 (out of 5)
- [ ] Mean "colour vividness" rating for V0 > baseline by ≥ 0.5 points
- [ ] Mean "naturalness" rating for V0 ≥ 3.5 (don't want it to look
      obviously artificial)
- [ ] "Water clarity" rating for V0 ≥ 3.5 (don't tint the water)

## 4. Subjective observations

Note any qualitative feedback:
- "The red on the goldfish really pops" ✅
- "The water looks blue-ish" ❌ (too much blue)
- "Hard to see the bottom-dwelling fish" (light distribution issue)

## 5. What to record

Save to `test_procedures/results/TP-06_<date>/`:
- Raw ratings (CSV)
- Mean scores per condition (CSV or summary)
- Photos of the tank under each condition
- Any written observer comments

## 6. After TP-06

Use the ratings to:
- Validate the V0 profile mix is right
- Drive product claims ("8/10 observers preferred V0 over baseline")
- Decide if any channel needs adjustment

If a profile is consistently rated low, return to TP-03 and re-tune.

Next: **TP-07 (reliability soak)** for endurance validation. This can
run unattended and overlaps with the next phase.
