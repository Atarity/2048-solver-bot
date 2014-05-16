import numpy as np

class TopLeftToRightIterator:
    def __init__(self, array2d):
        self.array2d = array2d
        #self.array2d = np.array
        self.x, self.y = 0, 0
        x, y = self.array2d.shape
        self.size = x if (x == y) else 0


    def next(self):
        if (self.x < 0 or self.y < 0 or self.x >= self.size or self.y >= self.size):
            raise StopIteration()
        result = self.array2d[self.y, self.x]

        self.x, self.y = self.__nextcoords()

        return result


    def nextcoords(self):
        if (self.x < 0 or self.y < 0 or self.x >= self.size or self.y >= self.size):
            raise StopIteration ()
        result = (self.x, self.y)

        self.x, self.y = self.__nextcoords()

        return result


    def __nextcoords(self):
        x, y = self.x, self.y
        if (x + 1 < self.size and y % 2 == 0):
            x += 1
        elif (x - 1 >= 0 and y % 2 == 1):
            x -= 1
        else :
            y += 1

        return x, y

        


class Direction:
    TL_R, TL_B, TR_B, TR_L, BR_L, BR_T, BL_T, BL_R = range(8)


class SnakeUnfolder:
    def __init__(self, array2d, dir = None):
        self.array2d = array2d
        self.dir = dir


    def __iter__(self):
        return TopLeftToRightIterator(self.array2d)




