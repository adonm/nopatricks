import unittest
from coord import Coord
from state import State, step
class TestState(unittest.TestCase):

    def test_step_should_update_energy(self):
        S = State(0, False, [], [])
        step(S, 2)
        self.assertEqual(S.energy, 24)

if __name__ == '__main__':
    unittest.main()