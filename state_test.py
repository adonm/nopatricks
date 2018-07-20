import unittest
from coord import Coord
from state import State, step, flip
class TestState(unittest.TestCase):

    def test_step_should_update_energy(self):
        S = State(0, False, [], [])
        step(S, 2)
        self.assertEqual(S.energy, 24)

    def test_flip(self):
        S = State(0, False, [], [])
        flip(S)
        self.assertEqual(S.harmonics, True)

    def test_fission(self):
        S = State(0, False, [], [])
        flip(S)
        self.assertEqual(S.harmonics, True)

if __name__ == '__main__':
    unittest.main()