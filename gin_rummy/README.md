# Velvet Gin ♠

A complete, turn-based Gin Rummy game against an adjustable CPU, entirely in Streamlit.

## Deploy both games using one private app

Streamlit Community Cloud permits one private app per workspace. The repository's
`arcade.py` launcher contains both Velvet Gin and the existing Tetris game.

In Community Cloud, deploy with:

- Repository: `chantalwalker/acct411-course-lab`
- Branch: `extra`
- Main file path: `arcade.py`

If an existing private deployment occupies your slot, delete that deployment in
Community Cloud first (this does not delete GitHub files), then deploy the launcher.
Do not delete the repository or change its visibility. Both games appear in the sidebar.

For a standalone Gin Rummy deployment, use `gin_rummy/app.py` instead.

## Run locally

```bash
python -m pip install -r gin_rummy/requirements.txt
python -m streamlit run arcade.py
```

## Play

Choose Easy, Medium, or Hard in the sidebar. Pick one of four table atmospheres.
On the opening turn, take the face-up card or pass. If both players pass, draw stock.
After drawing, click a card button and then **Discard selected**. The CPU responds
automatically. To finish a hand, use **Discard & knock** when your remaining
deadwood is at most 10, or **Declare GIN!** at zero. The hint button selects a
suggested discard; it does not play it for you.

Melds and layoffs are calculated automatically. The UI shows round results and a
match scorecard. Your progress is held in Streamlit session state; reloading or
losing the browser session can reset it. A normal sidebar change preserves play.
Tetris's browser game can restart when switching pages.

## Rules and scoring

- 52 cards, no jokers, ten cards per player, aces low.
- Sets of 3–4 equal ranks; suited runs of 3+ cards; no card counts twice.
- Deadwood: ace 1, numbered cards their rank, faces 10.
- A face-up pickup cannot be returned immediately.
- Knock at 10 or less; defender may lay off onto knocker's melds.
- Gin: 25 + defender deadwood, no layoffs.
- Undercut (including a tie): 25 + deadwood difference for the defender.
- Otherwise knocker scores the deadwood difference.
- When stock reaches two after a non-knocking discard, the round ends scoreless.
- First player alternates; first to the chosen match target wins.
- Variant choices: 25-point bonuses; no big gin, box bonuses, or shutout bonuses.
- Automatic meld layout uses minimum deadwood; defender evaluates every own
  arrangement plus legal chained layoffs for minimum remaining deadwood.

## CPU levels

Easy makes occasional random legal discards and misses some useful pickups.
Medium optimizes immediate deadwood. Hard also values potential melds, remembers
public pickups, avoids helping those pickups, and adjusts its knock threshold.
All are heuristics, not tournament-level AI. CPU strategy receives its own hand
and public information only; it never reads your hidden hand or future stock.

## Code map

- `app.py`: commented Streamlit UI, card styling, controls and session state.
- `engine.py`: reusable rules, optimal meld search, layoffs, scoring, and CPU.
- `test_engine.py`: regression tests and 36 seeded simulated rounds.
- `../arcade.py`: shared entrypoint for both games.

Run tests from the repository root:

```bash
python -m unittest discover -s gin_rummy -v
```

Reference rules: https://bicyclecards.com/how-to-play/gin-rummy
Streamlit hosting: https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app
