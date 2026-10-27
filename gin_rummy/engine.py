"""Gin Rummy rules and CPU strategy, independent of the Streamlit interface."""
from functools import lru_cache
from itertools import combinations
import random

# Each card is an integer: suit * 13 + rank - 1. Aces are always low.
SUITS = '♣♦♥♠'
RANKS = ('A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K')
def rank(card): return card % 13 + 1
def suit(card): return card // 13
def value(card): return min(rank(card), 10)
def label(card): return RANKS[rank(card)-1] + SUITS[suit(card)]

def is_meld(cards):
    """A meld is a set of 3–4 equal ranks or a same-suit run of 3+ cards."""
    cards = sorted(cards)
    if len(cards) < 3 or len(set(cards)) != len(cards): return False
    if len(cards) <= 4 and len({rank(c) for c in cards}) == 1: return True
    return len({suit(c) for c in cards}) == 1 and all(b == a+1 for a,b in zip(cards,cards[1:]))

@lru_cache(maxsize=8192)
def arrangements(hand):
    """Enumerate nonoverlapping meld arrangements, including leaving cards unmatched.

    Looking at every arrangement matters: a card can fit both a set and a run,
    but cannot be used twice. Hands have only 10 or 11 cards, so this is small.
    """
    melds = []
    for size in range(3, len(hand)+1):
        for candidate in combinations(hand, size):
            if is_meld(candidate): melds.append(candidate)
    results = []
    def visit(start, remaining, chosen):
        results.append((tuple(chosen), tuple(sorted(remaining))))
        for i in range(start, len(melds)):
            group = melds[i]
            if set(group) <= remaining:
                visit(i+1, remaining-set(group), chosen+[group])
    visit(0, set(hand), [])
    return tuple(results)

def analyze(hand):
    """Input: card IDs. Output: minimum deadwood points, melds, unmatched cards."""
    melds, loose = min(arrangements(tuple(sorted(hand))),
                       key=lambda item: (sum(value(c) for c in item[1]), len(item[1])))
    return sum(value(c) for c in loose), melds, loose

@lru_cache(maxsize=8192)
def layoff(loose, melds):
    """Find the best legal layoff, including chained extensions (e.g. 4 then 3).

    Return the remaining unmatched cards; only the non-knocker may lay off.
    """
    best = loose
    for card in loose:
        for i, group in enumerate(melds):
            extended = tuple(sorted(group+(card,)))
            if is_meld(extended):
                next_groups = melds[:i]+(extended,)+melds[i+1:]
                rest = layoff(tuple(c for c in loose if c != card), next_groups)
                if sum(map(value,rest)) < sum(map(value,best)): best = rest
    return best

def settle(knocker, defender):
    """Score the hand using 25-point gin and 25-point undercut bonuses.

    Melds are arranged automatically. The defender can reorganize their hand
    to minimize deadwood AFTER layoffs. No layoffs are allowed against gin.
    """
    kd, km, kl = analyze(knocker)
    if kd > 10: raise ValueError('Knocking requires at most 10 deadwood points.')
    choices = []
    for dm, dl in arrangements(tuple(sorted(defender))):
        remaining = dl if kd == 0 else layoff(dl, km)
        choices.append((sum(map(value,remaining)), dm, remaining, tuple(c for c in dl if c not in remaining)))
    dd, dm, dl, laid = min(choices, key=lambda x:x[0])
    if kd == 0: winner, points, reason = 'knocker', 25+dd, 'Gin'
    elif dd <= kd: winner, points, reason = 'defender', 25+kd-dd, 'Undercut'
    else: winner, points, reason = 'knocker', dd-kd, 'Knock'
    return dict(winner=winner, points=points, reason=reason, knock_deadwood=kd,
                defend_deadwood=dd, knock_melds=km, defend_melds=dm,
                knock_loose=kl, defend_loose=dl, laid=laid)

def connected(a,b):
    return rank(a)==rank(b) or (suit(a)==suit(b) and abs(rank(a)-rank(b))<=2)

def discard_choice(hand, forbidden=None, difficulty='Medium', known=(), seen=(), rng=None):
    """CPU receives its own hand and public information only—never your hand.

    Easy sometimes makes a random legal move. Medium minimizes deadwood.
    Hard also preserves promising pairs and avoids helping known pickups.
    """
    rng = rng or random
    legal = [c for c in hand if c != forbidden]
    if difficulty == 'Easy' and rng.random() < .45: return rng.choice(legal)
    scores = []
    for card in legal:
        rest = [c for c in hand if c != card]
        dead, _, loose = analyze(rest)
        score = float(dead)
        if difficulty == 'Hard':
            # Count unseen cards that could connect two loose cards into a meld.
            unseen = set(range(52))-set(hand)-set(seen)
            outs = {c for c in unseen for a,b in combinations(loose,2) if is_meld((a,b,c))}
            danger = sum(connected(card,k) for k in known)
            score += 5*danger - .7*len(outs)
        scores.append((score, -value(card), card))
    return min(scores)[2]

def wants_upcard(hand, card, difficulty, known=(), seen=(), rng=None):
    rng = rng or random
    discard = discard_choice(hand+[card], card, difficulty, known, seen, rng)
    before = analyze(hand)[0]
    after = analyze([c for c in hand+[card] if c != discard])[0]
    if difficulty == 'Easy': return after < before and rng.random() < .75
    if difficulty == 'Hard' and after == before:
        return sum(connected(card,c) for c in hand) >= 2
    return after < before

class Game:
    """One session's match. UI reruns keep this object in st.session_state."""
    def __init__(self, target=100, seed=None):
        self.rng = random.Random(seed)
        self.target = target
        self.scores = [0,0]  # Index 0 is you; index 1 is the CPU.
        self.round = 0
        self.history = []
        self.deal()

    def deal(self):
        self.round += 1
        deck = list(range(52)); self.rng.shuffle(deck)
        self.hands = [deck[:10], deck[10:20]]
        self.stock = deck[21:]
        self.pile = [deck[20]]
        self.seen = {deck[20]}
        self.known = [set(),set()]  # Public face-up pickups still held by each player.
        self.turn = (self.round-1)%2  # Alternate the first player each round.
        self.first = self.turn
        self.phase = 'offer'
        self.passes = 0
        self.forbidden = None
        self.result = None
        self.log = ['New deal. The first player may take the upcard or pass.']

    @property
    def match_over(self): return max(self.scores) >= self.target

    def pass_offer(self):
        if self.phase != 'offer': raise ValueError('Only the opening upcard may be passed.')
        self.log.append(('You' if self.turn==0 else 'CPU')+' passed the opening upcard.')
        self.passes += 1
        self.turn = 1-self.turn
        if self.passes == 2: self.phase = 'forced' # Original first player must draw stock.

    def draw(self, source):
        if self.phase not in ('offer','draw','forced'): raise ValueError('Discard before drawing again.')
        if source not in ('stock','discard'): raise ValueError('Unknown draw source.')
        if self.phase == 'offer' and source != 'discard': raise ValueError('Take the upcard or pass.')
        if self.phase == 'forced' and source != 'stock': raise ValueError('Both players passed; draw stock.')
        if source == 'stock' and len(self.stock) <= 2: raise ValueError('Stock is exhausted.')
        card = self.pile.pop() if source=='discard' else self.stock.pop()
        self.hands[self.turn].append(card)
        self.forbidden = card if source=='discard' else None
        if source=='discard': self.known[self.turn].add(card)
        who = 'You' if self.turn==0 else 'CPU'
        self.log.append(f'{who} drew '+(label(card)+' from discards.' if source=='discard' else 'from the stock.'))
        self.phase = 'discard'

    def discard(self, card, knock=False):
        if self.phase != 'discard': raise ValueError('Draw a card first.')
        if card not in self.hands[self.turn] or card == self.forbidden: raise ValueError('That card cannot be discarded.')
        remaining = [c for c in self.hands[self.turn] if c != card]
        if knock and analyze(remaining)[0] > 10: raise ValueError('Too much deadwood to knock.')
        self.hands[self.turn] = remaining
        self.pile.append(card); self.seen.add(card)
        self.known[self.turn].discard(card)
        self.log.append(('You' if self.turn==0 else 'CPU')+' discarded '+label(card)+'.')
        self.forbidden = None
        if knock:
            outcome = settle(remaining, self.hands[1-self.turn])
            winner = self.turn if outcome['winner']=='knocker' else 1-self.turn
            self.scores[winner] += outcome['points']
            outcome.update(winner=winner, knocker=self.turn)
            self.result = outcome
            self.history.append({'Round':self.round,'Result':outcome['reason'],
                                 'Winner':'You' if winner==0 else 'CPU','Points':outcome['points']})
            self.phase = 'over'
        elif len(self.stock)<=2:
            self.phase = 'over'
            self.result = {'reason':'Stock exhausted — no points awarded','points':0,'winner':None}
            self.history.append({'Round':self.round,'Result':'Draw','Winner':'—','Points':0})
        else:
            self.turn = 1-self.turn
            self.phase = 'draw'

    def cpu_turn(self, difficulty):
        """Advance only CPU actions. Opening passes may return play to you."""
        if self.turn != 1 or self.phase == 'over': return
        hand = self.hands[1]
        take = self.phase != 'forced' and wants_upcard(hand,self.pile[-1],difficulty,
                    self.known[0],self.seen,self.rng)
        if self.phase == 'offer' and not take:
            self.pass_offer(); return
        self.draw('discard' if take else 'stock')
        card = discard_choice(self.hands[1],self.forbidden,difficulty,self.known[0],self.seen,self.rng)
        dead = analyze([c for c in self.hands[1] if c!=card])[0]
        # Hard waits for a cleaner knock early, but closes faster as stock runs out.
        threshold = 5 if difficulty=='Hard' and len(self.stock)>12 else 10
        self.discard(card, knock=dead<=threshold)
