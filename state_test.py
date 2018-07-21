#!/usr/bin/env python3
import unittest
from coord import Coord
from state import *

class TestState(unittest.TestCase):

    def test_step_should_update_energy(self):
        S = State(0, False, [], [])
        S.step(2)
        self.assertEqual(S.energy, 24)

    def test_basic_matrix(self):
        m = Matrix(problem=1)
        c = Coord(8, 9, 10)
        self.assertTrue(m[c].is_void())
        m[c].set_full()
        self.assertTrue(m[c].is_full())
        self.assertFalse(m[c].is_grounded())
        m.yplane(9)[8,10].set_grounded()
        self.assertTrue(m[c].is_grounded())

        self.assertTrue(m[Coord(13, 5, 8)].is_model())

if __name__ == '__main__':
    unittest.main()
