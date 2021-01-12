import math


class vector_t:
    def __init__(self, vec=(0, 0)):
        self.x = vec[0]
        self.y = vec[1]

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def __float__(self):
        return self.length()

    def __add__(self, other):
        return vector_t((self.x + other.x, self.y + other.y))

    def __sub__(self, other):
        return vector_t((self.x - other.x, self.y - other.y))

    def __mul__(self, other):
        return vector_t((self.x * other, self.y * other))

    def __truediv__(self, other):
        return vector_t((self.x / other, self.y / other))

    def __str__(self):
        return '({x}, {y})'.format(x=self.x, y=self.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __tuple__(self):
        return tuple((int(self.x), int(self.y)))
