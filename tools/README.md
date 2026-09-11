# Live board tooling

`board.py` generates the two scoreboard pages from one match list:

- `live.html` (served at `/live`) — the real board, pre-event until the day
- `mock.html` (served at `/mock`) — a worked example with sample scores

Self-contained: `python3 tools/board.py` rewrites both pages. No arguments,
no external files.

## Running the day (Saturday)

The 20 pairings, handicaps and tee times are already in the `M` list. On the
day the only edits are each match's **state** and the page **mode**.

1. In `board.py`, set the `pre` build to `live` so `/live` shows the running
   score (`build('pre', ...)` -> `build('live', ...)`), and add a state to
   each match as its card comes in:
   - finished: `dict(done=1, up=+1, res="3&2")` (up>0 Europe won, <0 USA won,
     `res="halved"` for a half)
   - in progress: `dict(thru=14, up=-2)` (up>0 Europe up, <0 USA up, 0 A/S)
   - not started yet: leave the sample state or set `dict(thru=0, up=0)`
2. `python3 tools/board.py`
3. Commit and push. GitHub Pages redeploys in a minute or two. The front-page
   countdown flips to the red "Live" marker on its own once `/live` is live.

Golf rules live in the repo's CLAUDE.md / scorecard; strokes are already on
the draw sheet, not on this board.
