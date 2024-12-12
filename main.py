import numpy as np

class camera:
    def __init__(self, width, height, direction = np.array([0, 0, 1])):
        self.width = width
        self.height = height
        self.direction = direction # normal vector
        right = np.cross(direction, [0, 1, 0])
        up = np.cross(right, direction)
        right = right / (np.linalg.norm(right)*max(width, height))
        up = up / (np.linalg.norm(up)*max(width, height))
        self.grid = [[self.direction+(x-width/2)*right+(y-height/2)*up for x in range(width)] for y in range(height)]


class ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction

    def intersect(self): 
        return self.intersect_sphere(np.array([0, 0, 4]), 1)

    def intersect_sphere(self, Os, r):
        v = self.origin - Os
        a = np.sum(self.direction*self.direction)
        b = 2*np.sum(v*self.direction)
        c = np.sum(v*v)-r*r
        return b**2-4*a*c>=0


def main():
    cam = camera(20, 20)
    # print(cam.grid)
    for row in cam.grid:
        for point in row:
            r = ray(np.array([0, 0, 0]), point/np.linalg.norm(point))
            print('#' if r.intersect() else '.', end="")
        print()






if __name__ == "__main__":
    main()

