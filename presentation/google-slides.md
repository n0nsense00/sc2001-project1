# Presentation handoff

[Open SC2001 Project 1 - Hybrid Merge Sort in Google Slides](https://docs.google.com/presentation/d/1xcD_j9SiE7MKP3iQ7dYprbrnjnh-WGXluFaTKWdEfbY/edit).

The team-edited deck contained 18 slides when exported on 2026-09-14. Slides 2-7
were refreshed in place with 14 code images from the current beginner-friendly
`algorithms.py`, plus explanations in speaker notes. The Google deck is the place
for ongoing group edits. No sharing settings or invitations were changed by this
refresh; sharing is managed by the owner separately from the private GitHub repo.

## Current files

- `SC2001-Project1.pdf`: 18-page snapshot exported from Google Slides after the refresh.
- `SC2001-Project1-current.pptx`: the matching Google export, including editable
  slide text and speaker notes. Code panels and charts are images.
- `code-images/`: 14 replacement PNGs. `manifest.json` records the source hash,
  functions, slide mapping, image hashes and positions checked against the export.
- `code-slide-notes.md`: the six updated notes, with suggested timings and a small demo.
- `qa.md`: original inspection record and the dated code-slide refresh check.

Code panels omit comments/docstrings and wrap a few long lines with equivalent
parentheses. Their parsed Python syntax trees were checked against the source
excerpts. The executable sorting logic is unchanged by the display formatting.
To replace a panel again, select the image in Slides and choose **Replace image >
Upload from computer**, selecting its matching file from `code-images/`.

The full benchmark results remain measurements of commit `25fc591`. The readable
code comes from `422d067` and has its own correctness checks and smoke results;
the full benchmark was not rerun for this refresh. The updated notes disclose this.

The later naming update changes the merge indices to `left`, `right`, and `output`.
Slides 2 and 3 now show these names and explain that they hold indices. Slides 4-7
need no changes for this rename. The PDF and current PowerPoint include this update.

## Original presentation assets

`SC2001-Project1-final.pptx` remains the original 11-slide PowerPoint, with six native
charts, embedded chart workbooks, two native tables and 11 note parts. It is useful
for chart-data editing. `presentation.md` and `content.json` describe that original
version, not the later team layout. Keep the original if native chart editing matters.

Run `python analyze.py --results results/full --out plots/full` from the project folder
to recreate PNG/SVG plots. `python build_slide_content.py` regenerates the original
local content and notes; it does not edit the cloud deck or run benchmarks.

## Export and rehearsal

After later cloud edits, use **File > Download > PDF Document** to refresh the PDF,
or **File > Download > Microsoft PowerPoint** for a converted editable snapshot.
The saved files here are snapshots and do not synchronize automatically.

Reserve 480 seconds for explanation/demo and 120 seconds for Q&A. The updated
code-slide notes suggest 160 seconds in total, including the optional small demo.
The team-expanded deck needs a timed rehearsal; the original 8-main-slide timing
does not automatically apply to 18 slides. Preopen a terminal for `python demo.py`.
Every member should read `../docs/walkthrough-and-qa.md` and explain all algorithms,
the counting rule, fair timing, threshold choice, and the measured hybrid regression.
