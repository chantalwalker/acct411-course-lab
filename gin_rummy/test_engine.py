"""Run from this folder: python -m unittest -v"""
import unittest
from engine import *

def C(rank_value, suit_value=0): return suit_value*13+rank_value-1

class RulesTests(unittest.TestCase):
    def test_meld_rules(self):
        self.assertTrue(is_meld([C(1),C(2),C(3)]))
        self.assertTrue(is_meld([C(7,s) for s in range(4)]))
        self.assertFalse(is_meld([C(12),C(13),C(1)]))
        self.assertFalse(is_meld([C(7),C(7),C(7)]))

    def test_overlap_uses_optimal_arrangement(self):
        hand = [C(3),C(4),C(5),C(3,1),C(3,2),C(6),C(7)]
        self.assertEqual(analyze(hand)[0],0) # three threes + 4–7 clubs

    def test_chained_layoff(self):
        self.assertEqual(layoff((C(3),C(4)),((C(5),C(6),C(7)),)),())

    def test_gin_no_layoff(self):
        hand = [C(i) for i in range(1,11)]
        defender = [C(11), C(2,1)]
        result = settle(hand,defender)
        self.assertEqual(result['points'],37)
        self.assertEqual(result['laid'],())

    def test_tie_undercut(self):
        result = settle([C(1),C(2),C(3),C(7,1)], [C(7,2)])
        self.assertEqual(result['reason'],'Undercut')
        self.assertEqual(result['points'],25)

    def test_defender_can_break_own_meld_for_layoff(self):
        # Opponent's 4-6 clubs can all be laid off onto 7-9 clubs.
        result = settle([C(7),C(8),C(9),C(1,1)], [C(3),C(4),C(5),C(6)])
        self.assertEqual(result['defend_deadwood'],0)

    def test_opening_and_forbidden_return(self):
        g=Game(seed=1)
        with self.assertRaises(ValueError):g.draw('stock')
        g.pass_offer();g.pass_offer()
        self.assertEqual((g.turn,g.phase),(0,'forced'))
        g.draw('stock'); g.discard(g.hands[0][-1])
        g.draw('discard')
        with self.assertRaises(ValueError):g.discard(g.forbidden)

    def test_stock_exhaustion(self):
        g=Game(seed=3);g.phase='draw';g.stock=g.stock[:3]
        g.draw('stock');g.discard(g.hands[0][-1])
        self.assertEqual(g.phase,'over');self.assertEqual(g.result['points'],0)

    def test_simulated_games_preserve_cards_and_finish(self):
        for difficulty in ('Easy','Medium','Hard'):
            for seed in range(12):
                g=Game(seed=seed)
                actions=0
                while g.phase!='over':
                    if g.turn==1:g.cpu_turn(difficulty)
                    elif g.phase=='offer':g.pass_offer()
                    else:
                        g.draw('stock')
                        card=discard_choice(g.hands[0],g.forbidden,'Medium')
                        dead=analyze([c for c in g.hands[0] if c!=card])[0]
                        g.discard(card,knock=dead<=10)
                    cards=g.hands[0]+g.hands[1]+g.stock+g.pile
                    self.assertEqual(len(cards),52);self.assertEqual(len(set(cards)),52)
                    actions+=1;self.assertLess(actions,200)
                self.assertEqual([len(h) for h in g.hands],[10,10])

if __name__=='__main__':unittest.main()
