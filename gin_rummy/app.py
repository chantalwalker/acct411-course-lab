"""Velvet Gin — run with: streamlit run gin_rummy/app.py"""
from pathlib import Path
import sys
# Ensure imports work both in Streamlit Cloud and from the repository root.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import streamlit as st
from engine import Game, analyze, discard_choice, label, suit, rank, RANKS, SUITS

st.set_page_config(page_title='Velvet Gin | Your private card room', page_icon='♠', layout='wide')

# Streamlit executes this script after every click. Session state preserves the
# deck, hands, scores, and random generator between those executions.
if 'game' not in st.session_state: st.session_state.game = Game()
game = st.session_state.game

THEMES = {
    'Emerald club': ('#081e1b','#123c32','#d4b977','#f4f0df'),
    'Midnight lounge': ('#0e152b','#202e50','#c8b9f5','#f1edf9'),
    'Rose salon': ('#2b1624','#4b2b3e','#e8b5bd','#fff0ed'),
    'Ocean terrace': ('#08212f','#124357','#8cd6dc','#edf7f5'),
}
with st.sidebar:
    st.markdown('## ♠ VELVET GIN')
    st.caption('A little strategy. A little luck.')
    difficulty = st.selectbox('CPU difficulty', ['Easy','Medium','Hard'], index=1)
    st.caption({'Easy':'Relaxed play, with occasional mistakes.', 'Medium':'Builds melds and minimizes deadwood.',
                'Hard':'Protects potential melds and tracks your visible pickups.'}[difficulty])
    theme = st.selectbox('Table atmosphere', list(THEMES))
    sort_by = st.radio('Arrange your cards', ['Suit','Rank'], horizontal=True)
    hints = st.checkbox('Show melds & hints', value=True)
    target = st.selectbox('Next match target', [50,100,150,200], index=1)
    # A confirmation checkbox prevents an accidental reset during a hand.
    reset_ok = st.checkbox('Allow restarting this match')
    if st.button('Start new match', disabled=not reset_ok, use_container_width=True):
        st.session_state.game = Game(target=target)
        st.session_state.pop('selected',None)
        st.rerun()
    st.caption('Settings apply immediately. The target changes with a new match. Progress lasts for this browser session.')

bg, felt, gold, ink = THEMES[theme]
# Cards are drawn with HTML/CSS; no image downloads or external assets required.
st.markdown(f'''<style>
.stApp {{background:radial-gradient(ellipse at 50% 15%,{felt},{bg} 75%);color:{ink};}}
[data-testid="stSidebar"] {{background:{bg};border-right:1px solid {gold}44;}}
h1,h2,h3,p,label,[data-testid="stMetricValue"],[data-testid="stMetricLabel"] {{color:{ink}!important;}}
h1,h2,h3 {{font-family:Georgia,serif!important;}}
.stButton>button {{border-radius:12px;border:1px solid {gold}88;background:{felt};color:{ink};min-height:44px;}}
.stButton>button:hover {{border-color:{gold};color:{gold};}}
.stButton>button[kind="primary"] {{background:{gold};color:{bg};font-weight:700;}}
.stButton>button:disabled {{opacity:.4;}}
.hero {{padding:16px 0 22px;border-bottom:1px solid {gold}44;margin-bottom:22px;}}
.eyebrow {{font-size:11px;letter-spacing:4px;color:{gold};text-transform:uppercase;}}
.hero h1 {{font-size:clamp(36px,5vw,62px);margin:4px 0;letter-spacing:-2px;}}
.sub {{color:{ink}bb;font-size:15px;}}
.cards {{display:flex;gap:9px;flex-wrap:wrap;margin:14px 0 20px;}}
.card {{width:69px;height:99px;border-radius:9px;background:#fffcf4;color:#243031;box-shadow:0 5px 12px #0004;position:relative;border:2px solid #fff6;}}
.card.red {{color:#b74758;}}
.card.meld {{border:2px solid {gold};box-shadow:0 0 0 2px {gold}55;}}
.card.selected {{transform:translateY(-9px);box-shadow:0 0 0 3px {gold};}}
.corner {{position:absolute;top:5px;left:7px;font:700 17px Georgia;}}
.pip {{position:absolute;inset:26px 0;text-align:center;font-size:34px;}}
.bottom {{position:absolute;bottom:4px;right:7px;transform:rotate(180deg);font:700 16px Georgia;}}
.card.back {{background:repeating-linear-gradient(45deg,{felt},{felt} 5px,{gold}55 6px,{felt} 7px);border:4px solid #eee6;}}
.card.back .pip {{color:{gold};font-size:25px;}}
.tablebox {{border:1px solid {gold}44;background:{felt}66;border-radius:18px;padding:16px 22px;}}
@media(max-width:640px) {{.cards{{gap:5px}}.card{{width:47px;height:74px}}.pip{{font-size:24px;inset:22px 0}}.corner,.bottom{{font-size:13px}}}}
</style>''', unsafe_allow_html=True)

def cards_html(cards, melded=(), selected=None, backs=False):
    """Render visual cards. Actual controls below are native accessible buttons."""
    output = '<div class="cards">'
    for c in cards:
        if backs:
            output += '<div class="card back" aria-label="Hidden CPU card"><div class="pip">♠</div></div>'
        else:
            classes = 'card'+(' red' if suit(c) in (1,2) else '')
            classes += ' meld' if c in melded else ''
            classes += ' selected' if c==selected else ''
            output += f'<div class="{classes}" title="{label(c)}"><span class="corner">{RANKS[rank(c)-1]}</span><span class="pip">{SUITS[suit(c)]}</span><span class="bottom">{RANKS[rank(c)-1]}</span></div>'
    return output+'</div>'

# CPU advances once per turn, not once per arbitrary widget change.
# A rerun refreshes the board after the CPU has completed its legal action.
if game.turn == 1 and game.phase != 'over':
    game.cpu_turn(difficulty)
    st.rerun()

st.markdown('<div class="hero"><div class="eyebrow">The private card room</div><h1>Velvet Gin<span style="color:'+gold+'"> ♠</span></h1><div class="sub">Find your runs. Keep your cool. Beat the house.</div></div>',unsafe_allow_html=True)
cols = st.columns(4)
for col, title, number in zip(cols, ['YOUR SCORE','CPU SCORE','PLAYING TO','ROUND'], [*game.scores,game.target,game.round]):
    col.metric(title,number)
st.progress(min(max(game.scores)/game.target,1.0))

st.markdown('### Across the table')
st.caption(f'{difficulty} CPU · '+('Cards revealed' if game.phase=='over' else '10 cards · hidden hand'))
st.markdown(cards_html(game.hands[1], backs=game.phase!='over'),unsafe_allow_html=True)

if game.phase=='over':
    result = game.result
    if result['winner'] is None: st.info(result['reason'])
    else:
        winner = 'You' if result['winner']==0 else 'CPU'
        st.success(f"{result['reason']}! {winner} +{result['points']} points.")
        st.caption(f"Knocker deadwood: {result['knock_deadwood']} · Defender after layoffs: {result['defend_deadwood']}")
        for role in ('knock','defend'):
            who = result['knocker'] if role=='knock' else 1-result['knocker']
            groups = [' '.join(map(label,g)) for g in result[role+'_melds']]
            st.write(('You' if who==0 else 'CPU')+' melds: '+(' / '.join(groups) or 'None'))
        if result['laid']: st.write('Defender laid off: '+', '.join(map(label,result['laid'])))
    if game.match_over:
        st.balloons() if result['winner']==0 else None
        st.markdown('### '+('You won the match! ✨' if game.scores[0]>=game.target else 'The CPU won this match. Rematch?'))
        if st.button('Play again', type='primary'):
            st.session_state.game = Game(target=target); st.rerun()
    elif st.button('Deal next round',type='primary'):
        game.deal(); st.session_state.pop('selected',None); st.rerun()
else:
    left, right = st.columns([1,2])
    with left:
        st.markdown('#### The discard pile')
        if game.pile: st.markdown(cards_html([game.pile[-1]]),unsafe_allow_html=True)
        else: st.caption('Empty until your discard')
        st.caption(f'{len(game.stock)} cards remain in the stock')
    with right:
        if game.phase=='offer':
            st.markdown('#### Opening choice')
            st.write('Take the face-up card, or pass and offer it to the CPU.')
        elif game.phase=='forced':
            st.markdown('#### Both players passed')
            st.write('Draw from the stock to begin.')
        elif game.phase=='draw':
            st.markdown('#### ① Draw a card')
            st.write('Take the known discard or try your luck with the stock.')
        else:
            st.markdown('#### ② Choose your discard')
            st.write('Select a card below, then discard or knock.')
        a,b,c = st.columns(3)
        if a.button('Draw stock', disabled=game.phase not in ('draw','forced'),use_container_width=True):
            game.draw('stock'); st.session_state.pop('selected',None); st.rerun()
        if b.button('Take discard',disabled=game.phase not in ('draw','offer'),use_container_width=True):
            game.draw('discard'); st.session_state.pop('selected',None); st.rerun()
        if c.button('Pass',disabled=game.phase!='offer',use_container_width=True):
            game.pass_offer(); st.rerun()

hand = sorted(game.hands[0],key=(lambda c:(suit(c),rank(c))) if sort_by=='Suit' else (lambda c:(rank(c),suit(c))))
dead, melds, loose = analyze(hand)
selected = st.session_state.get('selected')
if selected not in hand: selected = None
st.markdown('### Your hand')
st.caption('Gold outlines mark your best melds.' if hints else 'Build sets of equal ranks and runs of the same suit.')
st.markdown(cards_html(hand, {c for group in melds for c in group} if hints else (),selected),unsafe_allow_html=True)

if game.phase=='discard':
    # Two short rows keep card buttons usable on smaller screens.
    for start in range(0,len(hand),6):
        row = st.columns(min(6,len(hand)-start))
        for col, card in zip(row,hand[start:start+6]):
            if col.button(label(card), key=f'card_{card}', disabled=card==game.forbidden,
                          type='primary' if card==selected else 'secondary',use_container_width=True):
                st.session_state.selected=card; st.rerun()
    if game.forbidden is not None: st.caption(f'{label(game.forbidden)} was just taken from the discard pile and cannot be returned this turn.')
    after = analyze([c for c in hand if c!=selected])[0] if selected is not None else None
    if after is not None: st.write(f'Selected: **{label(selected)}** · Deadwood after discarding: **{after}**')
    a,b,c=st.columns(3)
    if a.button('Discard selected',disabled=selected is None,type='primary',use_container_width=True):
        game.discard(selected); st.session_state.pop('selected',None); st.rerun()
    if b.button('Declare GIN!' if after==0 else 'Discard & knock',disabled=after is None or after>10,use_container_width=True):
        game.discard(selected,knock=True); st.session_state.pop('selected',None); st.rerun()
    if hints and c.button('Suggest a discard',use_container_width=True):
        st.session_state.selected=discard_choice(hand,game.forbidden,'Medium'); st.rerun()
if hints:
    st.caption(f'Deadwood: {dead} points'+(' before your discard' if len(hand)==11 else '')+' · Knock with 10 or fewer after discarding; gin with zero.')
    if melds: st.write('**Your melds:** '+' / '.join(' '.join(map(label,group)) for group in melds))

with st.expander('How to play & scoring'):
    st.markdown('''- You and the CPU each receive **10 cards**. Draw one, then discard one.
- **Sets:** 3 or 4 of a rank (7♣ 7♦ 7♥). **Runs:** 3+ consecutive cards of one suit (4♠ 5♠ 6♠). Aces are low; Q–K–A does not count.
- Unmatched cards are **deadwood**: ace = 1; number cards = face value; J/Q/K = 10.
- Select a discard, then **knock** when your remaining deadwood is 10 or less. You may also keep playing. Zero deadwood is **gin**.
- On a knock, the defender automatically lays off eligible cards onto the knocker's melds. The lower-deadwood knocker earns the difference. A defender who ties or beats the knocker earns the difference **plus 25** (undercut).
- Gin earns **25 plus the defender's deadwood**, with no layoffs. This game uses 25-point bonuses, no big-gin or end-of-match box bonuses; first to the target wins.
- The opening upcard is offered to each player. If both pass, the first player draws stock. First player alternates each round.
- A face-up card cannot be discarded immediately after picking it up. When only 2 stock cards remain after a discard, the round is a draw unless that discard ends in a knock/gin.
- Meld arrangements and defender layoffs are automatic. The CPU uses only its hand and public cards, never your hidden cards. Difficulty can change during a match.
- Refreshing or disconnecting may reset your session. Use the in-app buttons to keep playing.''')
with st.expander('Recent moves',expanded=False):
    for entry in reversed(game.log[-16:]): st.write(entry)
if game.history:
    with st.expander('Match scorecard'):
        st.dataframe(game.history,hide_index=True,use_container_width=True)
st.caption('VELVET GIN  /  A quiet table. A sharper hand.')
