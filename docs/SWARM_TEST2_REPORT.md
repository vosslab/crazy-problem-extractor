# Swarm test 2: modular assignment (ch03)

## Test design

Re-ran ch03 with the same 8 coders but using **modular assignment** instead of free choice. Each coder received 2-3 required problems assigned via `(index % 8) + 1` on the sorted problem list, plus creative freedom to pick 2-3 optional problems.

Assignment table (18 problems after deduplication, 8 coders):

```
Coder 1: required p01, p10, p18   + free picks
Coder 2: required p02, p11, p19   + free picks
Coder 3: required p03, p12        + free picks
Coder 4: required p04, p13        + free picks
Coder 5: required p05, p14        + free picks
Coder 6: required p06, p15        + free picks
Coder 7: required p07, p16        + free picks
Coder 8: required p09, p17        + free picks
```

## Results comparison

| Metric | Test 1 (free choice) | Test 2 (modular) |
| --- | --- | --- |
| Total files | 42 | 43 |
| Unique problems covered | 7 / 19 | 18 / 18 |
| Coverage % | 37% | 100% |
| Gap count | 12 | 0 |
| Competition count | 7 | 6 |
| Single count | 0 | 12 |
| Validation errors | 0 | 0 |
| Widget types used | 4 | 4 (RadioButtons, CheckboxList, PopUp, Numeric) |

## What changed

- **Coverage jumped from 37% to 100%.** Every problem now has at least one version. The 12 gaps from test 1 are all filled.
- **Herding reduced but not eliminated.** p11 (aromatic amino acids) and p14 (phenol-like R group) still attracted all 8 coders as optional picks. These are simple, self-contained problems that coders gravitate to regardless of assignment.
- **Competition preserved where it matters.** 6 problems have competing versions (p01=5, p06=4, p09=4, p11=8, p14=8, p18=2). The referee still has real choices for quality selection on popular problems.
- **Difficult problems now covered.** Challenge problems p16 (minor species ratio), p17 (titration pKa), p18 (lysine protonation), p19 (glutamic acid Henderson-Hasselbalch) all have at least 1 version. Test 1 had zero coverage on these.
- **OCR-garbled problems handled.** p02 (uncommon amino acids) and p03 (identify from structures) were adapted to text-based questions by their assigned coders. Test 1 coders skipped these entirely.
- **File count nearly identical** (43 vs 42). Modular assignment did not reduce coder throughput.

## Conclusions

1. **Modular assignment solves herding.** The strategy delivers near-perfect coverage without reducing creative freedom or output volume.
2. **Free picks still herd.** Even with required assignments, optional picks cluster on easy problems (p11, p14). This is acceptable because the required assignments guarantee breadth.
3. **Single-coverage problems are the tradeoff.** 12 of 18 problems have only 1 version (no competition). For production, consider assigning each problem to 2 coders or using a second wave to add competition on singles.
4. **Modular assignment is validated for production use.** Recommend modular assignment as the default dispatch mode for all chapters.
