# Presentation handoff

[Open SC2001 Project 1 - Hybrid Merge Sort in Google Slides](https://docs.google.com/presentation/d/1xcD_j9SiE7MKP3iQ7dYprbrnjnh-WGXluFaTKWdEfbY/edit).

The native Google Slides document was created in the signed-in account, renamed,
and verified as saved to Drive. General access was checked as **Restricted**,
with only the owner listed. No invitations, publication, or sharing changes were made.

## Files and editability

- `SC2001-Project1.pdf`: the 11-page PDF exported from that Google Slides document.
- `SC2001-Project1-final.pptx`: the original editable PowerPoint, with six native
  charts, embedded chart workbooks, two native tables and 11 speaker-note parts.
- `presentation.md`: complete slide content, source references and timed notes.
- `content.json`: chart data and slide content derived from the saved full results.
- `qa.md`: completed export and visual-inspection record.

Google Slides retains editable slide text, two tables and speaker notes. Its
PowerPoint conversion turned the six native charts into images. Those charts
cannot be edited as data series in the Google deck. The original local PowerPoint
retains chart-data editing; do not replace it with a downloaded Google copy if
you need that capability. This is the remaining format limitation.

For graph updates, run `python analyze.py --results results/full --out plots/full`
from the project folder. The PNG/SVG exports are in `plots/full`. Replace the
relevant image in Google Slides, or edit the native PowerPoint chart's data.
`python build_slide_content.py` regenerates local content and notes; it does not
automatically change the cloud deck. No benchmark runs from those commands.

After editing Google Slides, use File > Download > PDF Document to refresh the
portable copy. Use File > Download > Microsoft PowerPoint when a converted copy
is useful, remembering its charts are images. To import the original elsewhere,
open Google Slides, choose the file picker and Upload, and select the final PPTX.
Conversion may again rasterize native charts.

## Delivery and rehearsal

Present slides 1-8 in 480 seconds, including the small live demo; reserve 120
seconds for Q&A. Slides 9-11 are appendices for questions. Speaker notes are in
the deck and in `presentation.md` with exact time windows. Use Presenter view to
see the notes and timer. Preopen a terminal in `project1` for `python demo.py`.
Keep the PDF available as the offline presentation fallback.

Every group member should read `../docs/walkthrough-and-qa.md`, run the demo and
explain the final regression. The role allocation is a suggestion, not a record
of contributions. A timed human rehearsal and checking the actual classroom
projector remain group activities. No PowerPoint desktop inspection is claimed.
