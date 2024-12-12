import numpy as np
from PIL import Image

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

    def render(self, objects):
        img = Image.new('RGB', (self.width, self.height))
        pixels = img.load()
        for y in range(self.height):
            for x in range(self.width):
                point = self.grid[y][x]
                r = ray(np.array([0, 0, 0]), point/np.linalg.norm(point))
                result = r.intersect(objects)
                pixels[self.width-x-1,self.height-y-1] = (0, 0, 0) if result is None else result.color

        img.save('render.png')
        

class object:
    def __init__(self, type, params, color = (255, 255, 255), reflectivity = 0):
        self.type = type
        self.color = color
        self.reflectivity = reflectivity
        if type == "sphere":
            self.center = params[0]
            self.radius = params[1]
        elif type == "plane":
            self.point = params[0]
            self.normal = params[1]
            self.distance = np.dot(self.point, self.normal)
        # elif type == "triangle":
        #     self.vertices = params
        else:
            raise Exception("Object does not exist")


class ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction

    def intersect(self, objects): 
        min_dist = np.inf
        result = None
        for object in objects:
            if object.type == "sphere":
                dist = self.intersect_sphere(object.center, object.radius)
            elif object.type == "plane":
                dist = self.intersect_plane(object.point, object.normal, object.distance)
            if dist < 0: continue
            if dist < min_dist:
                min_dist = dist
                result = object

        return result

    def intersect_sphere(self, Os, r):
        v = self.origin - Os
        a = np.sum(self.direction*self.direction)
        b = 2*np.sum(v*self.direction)
        c = np.sum(v*v)-r*r
        if b**2-4*a*c<0: return -1
        t1 = (-b-np.sqrt(b**2-4*a*c))/(2*a)
        t2 = (-b+np.sqrt(b**2-4*a*c))/(2*a)
        return t2 if t1 < 0 else t1
    
    def intersect_plane(self, Op, N, distance):
        if np.dot(self.direction, N) == 0: return -1
        return (distance-np.dot(self.origin, N))/np.dot(self.direction, N)
    

def main():
    width, height = 192, 108
    cam = camera(width, height)
    objects = [
        object("sphere", [np.array([0, 0, 4]), 1], (255, 0, 0), 0), 
        object("sphere", [np.array([1.1, 0, 4.5]), .5], (50, 0, 200), 0), 
        object("plane", [np.array([0, -1, 0]), np.array([0, 1, 0])], (0, 255, 0), 0)
    ]
    cam.render(objects)



if __name__ == "__main__":
    main()

