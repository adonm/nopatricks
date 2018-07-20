import unittest
from coord import Coord
class TestCoords(unittest.TestCase):

    def test_upper(self):
        c = Coord(1,1,1)
        acs = c.adjacent_coords()
        self.assertEqual(len(acs), 6)

if __name__ == '__main__':
    unittest.main()