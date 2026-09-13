# Collaboration and integration

Use [the private GitHub workflow](github-collaboration.md) to obtain access,
clone the project, make changes and review pull requests. Google Slides access
is granted separately by its owner.

These are **suggested responsibilities**, not claims of completed member
contributions. Use your TA-assigned team; do not invent names or authorship.
Every member should run the demo, trace insertion and merge, and answer all Q&A.

| Suggested owner | Primary review | Cross-review |
|---|---|---|
| Member A | Algorithms, counting and correctness | Reproduce a plotted result |
| Member B | Experiment protocol, seeds, timing and integrity | Explain the recurrence |
| Member C | Theory, plots and interpretation | Trace the code and counting |
| Member D (if four members) | Slides, notes and rehearsal | Reproduce tests and benchmarks |

With three members, divide presentation preparation among A/B/C. Allocate speaking
by understanding and timing, not by who wrote a file. Keep a genuine contribution
log containing date, person, activity and evidence; it is intentionally not
prepopulated. All members are responsible for verifying this prepared work and
understanding it before presenting it as their project.

## Shared conventions

- [lo,hi), floor midpoint, stable ties, positive integer S (bool rejected).
- Key comparisons are only evaluated data-order checks; terminating false checks count.
- One reusable buffer, no recursive slicing or skip-merge optimization.
- CPU time in seconds from uncounted runs. Blank metrics mean unmeasured.
- RNG seeds and configurations committed; large raw input arrays are reproducible and excluded.
- Results folders are immutable experiment identities: never append changed code/config to them.
- Use new output folders for a fresh machine/interpreter/run; no concurrent comparative sorts.
- Review theory labels and units whenever changing charts. Do not infer winners from smoke data.

## Integration checklist

- [ ] Each member can trace [5,2,4,1,3,6] at S=3 and explain all 10 comparisons.
- [ ] Run `python -m unittest discover -s tests -v` and `python demo.py`.
- [ ] Run or inspect smoke protocol and verify resume adds no duplicate rows.
- [ ] Read the full configuration, environment metadata and final three paired seeds.
- [ ] Check `results/full/audit.json`, `plots/full/findings.md` and raw CSV agree.
- [ ] Explain why CPU-selected S can differ from comparison-selected S.
- [ ] Confirm plots and slides regenerated from the same full data.
- [ ] Rehearse within 8 minutes; reserve 2 minutes for questions.
- [ ] Each member answers one question from every topic in `walkthrough-and-qa.md`.
- [ ] Open local PDF and the Google Slides copy before the lab; check charts and notes.
- [ ] Bring precomputed results and a working offline demo; do not start 10-million sorts live.

Suggested rehearsal: one person presents; a second interrupts as the TA; a third
checks claims against raw results; rotate roles. Fill the checkboxes only after
the group actually performs each activity.
