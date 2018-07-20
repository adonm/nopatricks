import unittest
from coord import Coord, Line
class TestCoords(unittest.TestCase):

    def test_adj_6(self):
        c = Coord(1,1,1)
        acs = c.adjacent(10)
        self.assertEqual(len(acs), 6)

    def test_adj_5(self):
        c = Coord(0,1,1)
        acs = c.adjacent(10)
        self.assertEqual(len(acs), 5)

    def test_line_1(self):
        line = Line(Coord(1,1,1), Coord(5,1,1))
        self.assertTrue(line.contains(Coord(3,1,1)))
        self.assertFalse(line.contains(Coord(3,2,1)))

if __name__ == '__main__':
    unittest.main()
