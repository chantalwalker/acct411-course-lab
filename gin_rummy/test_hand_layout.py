"""Regressions for automatic grouping and CPU discard availability."""
import unittest
from engine import Game, analyze
from hand_layout import automatic_order

class HandLayoutTests(unittest.TestCase):
    def test_melds_left_deadwood_sorted(self):
        # 8s set, 3–5 clubs run, and deliberately unsorted loose cards.
        cards=[7,20,33,2,3,4,12,14,38,40]
        for mode in ('Rank','Suit'):
            hand=automatic_order(cards,mode)
            _, melds, loose=analyze(cards)
            n=sum(map(len,melds))
            self.assertEqual(set(hand[:n]),{c for g in melds for c in g})
            self.assertEqual(set(hand[n:]),set(loose))
            key=(lambda c:(c%13,c//13)) if mode=='Rank' else (lambda c:(c//13,c%13))
            self.assertEqual(hand[n:], sorted(loose,key=key))
            self.assertEqual(sorted(hand),sorted(cards))

    def test_draw_completes_set_and_moves_it_left(self):
        cards=[7,20,1,15,30,45,9,24,38,39]
        hand=automatic_order(cards+[33],'Rank')
        self.assertEqual(set(hand[:3]),{7,20,33})

    def test_cpu_discards_remain_available_until_player_draws(self):
        checked=0
        for seed in range(20):
            g=Game(seed=seed);g.phase='draw';g.turn=1
            g.cpu_turn('Medium')
            if g.phase=='over':continue
            self.assertEqual(g.turn,0)
            self.assertEqual(g.phase,'draw')
            card=g.pile[-1]
            before=list(g.hands[0])
            g.draw('discard')
            self.assertEqual(g.hands[0],before+[card])
            self.assertEqual(g.forbidden,card)
            with self.assertRaises(ValueError):g.draw('stock')
            checked+=1
        self.assertGreater(checked,10)

if __name__=='__main__':unittest.main()
