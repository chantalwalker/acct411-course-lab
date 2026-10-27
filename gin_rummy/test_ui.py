"""Streamlit integration checks; run with unittest alongside the engine tests."""
import json
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest
from engine import Game
from hand_layout import automatic_order

class InterfaceTests(unittest.TestCase):
    def test_drag_cpu_pickup_and_draw_sort(self):
        at=AppTest.from_file(str(Path(__file__).with_name('app.py')),default_timeout=30)
        g=Game(seed=0);g.phase='draw';g.turn=1
        at.session_state['game']=g
        at.run()
        self.assertFalse(at.exception)
        self.assertEqual(g.phase,'draw')
        top=g.pile[-1]
        # Move the leftmost card all the way to the right in one event.
        before=list(at.session_state['hand_order'])
        after=before[1:]+before[:1]
        hand_args=next(json.loads(c.proto.json_args) for c in at.get('component_instance')
                       if len(json.loads(c.proto.json_args)['cards'])==10)
        at.session_state['sliding_hand']={'event_id':'drag-across','context':hand_args['context'],
                                         'order':after,'selected':None}
        at.run()
        self.assertEqual(at.session_state['hand_order'],after)
        at.run() # A plain rerun must not undo the manual arrangement.
        self.assertEqual(at.session_state['hand_order'],after)
        # Click the CPU's face-up discard through the actual component payload.
        pile_args=next(json.loads(c.proto.json_args) for c in at.get('component_instance')
                       if len(json.loads(c.proto.json_args)['cards'])==1)
        self.assertTrue(pile_args['can_select'])
        at.session_state['discard_pickup']={'event_id':'take-cpu-discard','context':pile_args['context'],
                                          'order':[top],'selected':top}
        at.run()
        self.assertFalse(at.exception)
        self.assertIn(top,g.hands[0]);self.assertEqual(len(g.hands[0]),11)
        self.assertEqual(at.session_state['hand_order'],automatic_order(g.hands[0],'Suit'))
        self.assertTrue(next(b for b in at.button if b.label=='Take discard').disabled)
        # Sorting by rank reruns grouping; an ordinary theme change does not.
        next(r for r in at.radio if r.label=='Sort cards by').set_value('Rank').run()
        self.assertEqual(at.session_state['hand_order'],automatic_order(g.hands[0],'Rank'))
        at.run() # Old component events must not draw twice.
        self.assertEqual(len(g.hands[0]),11)

if __name__=='__main__':unittest.main()
