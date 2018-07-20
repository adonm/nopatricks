import unittest
from coord import Coord
class TestCoords(unittest.TestCase):

    def test_adj_6(self):
        c = Coord(1,1,1)
        acs = c.adjacent(10)
        self.assertEqual(len(acs), 6)

    def test_adj_5(self):
        c = Coord(0,1,1)
        acs = c.adjacent(10)
        self.assertEqual(len(acs), 5)

if __name__ == '__main__':
    unittest.main()
