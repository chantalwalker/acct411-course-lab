# Theme Drop — a Tetris-style Streamlit game

Eight themes: **Y2K, Cottagecore, Ocean, Cyberpunk, Cosmic, Candyland,
Autumn, and Arcade**. Themes change the background, palette, block texture,
line-clear particles, messages, typography, and optional synthesized sounds.
Switch worlds during play without losing your board.

## Put it on GitHub and Streamlit

1. Unzip this download.
2. Create a GitHub repository (or use a repository you own).
3. Upload `app.py`, `requirements.txt`, and this `README.md` to the repository's
   root. Upload the extracted files, **not the ZIP**. Commit the files.
4. In Streamlit Community Cloud, create an app from that repository and branch.
5. Set **Main file path** to **`app.py`** and deploy.
   If you uploaded an enclosing folder instead, use `tetris/app.py`.
6. Open the app, choose a world, and press **Start game**.

GitHub stores the code; Streamlit runs it. No API keys or paid assets are needed.
The exact filename matters: `app.py`, including the `.py` extension.

## Run on your own computer

Use Python 3.10 or newer, then run these commands in the extracted folder:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Controls

| Key | Action |
| --- | --- |
| Left / Right or A / D | Move |
| Down or S | Soft drop: 1 point per cell |
| Up / W / X | Rotate clockwise |
| Z | Rotate counterclockwise |
| Space | Hard drop: 2 points per cell |
| C / Shift | Hold or swap (once per piece) |
| P / Escape | Pause / resume |

Touch buttons provide the same actions. Tap once per move. Click the board to
restore keyboard focus after interacting elsewhere. Switching browser tabs or
losing frame focus pauses the game; resume when ready.

## Rules and features

- 10-column, 20-row playfield; all seven tetrominoes.
- Seven-bag shuffle, three-piece preview, hold, and ghost landing outline.
- Clear 1 / 2 / 3 / 4 rows for 100 / 300 / 500 / 800 × current level.
- Every ten cleared rows raises the level and speeds up gravity.
- 500 ms lock delay; up to 15 grounded-move resets per piece.
- Simplified wall/floor kicks, not official competitive SRS.
- No T-spin bonuses, multiplayer, or online leaderboard.
- Best score is saved locally when browser storage permits. This is per
  browser/origin, not a shared account score. Refresh resets the active run.
- Sound is off initially. Effects respect the initial reduced-motion preference
  and can be switched off manually.

## How the code works (start here)

`app.py` is deliberately self-contained and heavily commented:

1. **Python wrapper:** configures Streamlit and embeds `GAME_HTML`.
2. **HTML:** defines the buttons, status panels, and canvas surfaces.
3. **CSS:** handles layout, mobile presentation, and theme variables.
4. **JavaScript section 1:** theme records and live theme switching.
5. **Section 2:** board state, piece shapes, shuffle, spawn, and statistics.
6. **Section 3:** movement, collision, rotation, hold, scoring, and row removal.
7. **Section 4:** draws blocks, previews, ghost, and themed particles.
8. **Section 5:** creates short musical notes in the browser.
9. **Section 6:** connects keyboard, buttons, and automatic pause.
10. **Section 7:** advances gravity and redraws with `requestAnimationFrame`.

Python hosts the game, while JavaScript handles animation locally in the
browser. Sending every animation frame through Streamlit's Python reruns would
be slow and reset browser state. No separate frontend build is required.

To customize a world, edit its record in `THEMES`. Palette entries correspond
to I, J, L, O, S, T, Z pieces. Edit `COLS`, `ROWS`, canvas dimensions, and layout
together if changing board size. The current pixel layout assumes 10 × 20.

Streamlit embedding reference:
https://docs.streamlit.io/develop/concepts/custom-components/components-v1/intro

This is an unofficial educational falling-block project, not an official
Tetris product. No external fonts, images, music, or network APIs are loaded.
