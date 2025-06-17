import unittest
from pathfinding import a_star

class TestAStar(unittest.TestCase):
    def test_simple_path(self):
        grid = [[1]*6 for _ in range(6)]
        path = a_star(grid, (0,0), (2,2))
        self.assertEqual(path, [(0,0), (1,1), (2,2)])

if __name__ == '__main__':
    unittest.main()
