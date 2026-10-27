"""Display order only: moving cards never changes scoring or meld membership."""
from engine import analyze, rank, suit


def automatic_order(cards, sort_by='Suit'):
    """Group complete melds on the left, then sort deadwood by rank or suit.

    Keep each set/run together, using the engine's non-overlapping best melds.
    This is called on a deal, draw, discard, or a change of the sorting setting;
    manual reordering is otherwise preserved through ordinary UI reruns.
    """
    key = (lambda c: (rank(c), suit(c))) if sort_by == 'Rank' else (lambda c: (suit(c), rank(c)))
    _, melds, loose = analyze(cards)
    groups = sorted((sorted(group, key=key) for group in melds), key=lambda group: key(group[0]))
    return [card for group in groups for card in group] + sorted(loose, key=key)
