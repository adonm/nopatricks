import unittest
from coord import Coord
class TestCoords(unittest.TestCase):

    def test_upper(self):
        c = Coord(1,1,1)
        print(c.adjacent_coords())
        # self.assertEqual('foo'.upper(), 'FOO')

if __name__ == '__main__':
    unittest.main()