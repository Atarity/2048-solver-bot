import unittest
import solverbot2048 as s2048
import snake
import numpy as np

class TestFuncTests(unittest.TestCase):
    def test_getPerfectList(self):
        self.assertEqual(s2048.getPerfectList([2, 4, 8, 4]), [2, 4, 8, 4])
        self.assertEqual(s2048.getPerfectList([8, 4, 2, 4]), [8, 4, 4, 2])


    def test_getPerfectDiff(self):
        self.assertEqual(s2048.getPerfectDiff([2, 4, 8, 4]), 0)
        self.assertEqual(s2048.getPerfectDiff([4, 2, 8, 4]), -5)


    def test_snake(self):
        a = np.ndarray((4,4), int)
        s = snake.SnakeUnfolder(a)
        siter = iter(s)

        for i in range(4*4):
            x,y = siter.nextcoords()
            a[y,x] = i

        print a


if __name__ == '__main__':
    unittest.main()