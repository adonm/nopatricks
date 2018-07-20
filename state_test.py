import unittest
from coord import Coord
from state import State
class TestState(unittest.TestCase):

    def test_step_should_update_energy(self):
        S = State(0, False, [], [])
        S.step(2)
        self.assertEqual(S.energy, 24)

if __name__ == '__main__':
    unittest.main()