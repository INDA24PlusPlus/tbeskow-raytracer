import numpy as np
from PIL import Image

class camera:
    def __init__(self, width, height, direction = np.array([0, 0, 1])):
        self.width = width
        self.height = height
        self.direction = direction 
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
                pixels[self.width-x-1,self.height-y-1] = tuple((r.trace(objects)*255).astype(int)) 

        img.save('render.png')
        

class object:
    def __init__(self, type, params, color = (1, 1, 1), emittedColor = (1, 1, 1), luminance = 0):
        self.type = type
        self.color = color
        self.emittedColor = emittedColor
        self.luminance = luminance
        if type == "sphere":
            self.center = params[0]
            self.radius = params[1]
        elif type == "plane": # ensidig
            self.point = params[0]
            self.normal = params[1]
            self.distance = np.dot(self.point, self.normal)
        # elif type == "triangle":
        #     self.vertices = params
        else:
            raise Exception("Object does not exist")


class ray:
    def __init__(self, origin, direction):
        self.origin = np.array(origin, dtype=float)
        self.direction = np.array(direction, dtype=float)

    def trace(self, objects, depth = 10):
        incomingColor = np.array([0, 0, 0], dtype=float)
        rayColor = np.array([1, 1, 1], dtype=float)
        # print("start")
        for i in range(depth):
            result, distance = self.intersect(objects)
            if result == None: break
            self.origin+=self.direction*distance
            self.direction = self.randomDirection(self.findNormal(result))
            # print(rayColor, incomingColor, result.luminance)
            incomingColor+=result.emittedColor*result.luminance*rayColor
            rayColor *= result.color


        return incomingColor
    
    def randomDirection(self, normal):
        while True:
            direction = np.random.uniform(-1, 1, 3)
            if np.linalg.norm(direction) > 1: continue
            if np.dot(direction, normal) < 0: continue
            return direction/np.linalg.norm(direction)
    
    def findNormal(self, object):
        if object.type == "sphere":
            return (self.origin-object.center)/object.radius
        elif object.type == "plane":
            return object.normal
        else:
            raise Exception("gg")

    def intersect(self, objects): 
        min_dist = np.inf
        result = None
        for object in objects:
            if object.type == "sphere":
                dist = self.intersect_sphere(object.center, object.radius)
            elif object.type == "plane":
                dist = self.intersect_plane(object.point, object.normal, object.distance)
            if dist <= 1e-8: continue
            if dist < min_dist:
                min_dist = dist
                result = object
        return result, min_dist

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
    # width, height = 50, 40
    cam = camera(width, height)
    objects = [
        object("sphere", [np.array([0, 0, 4]), 1], (1, 0, 0), 0), 
        object("sphere", [np.array([1.1, 0, 4.5]), .5], (.3, 0, 1), 0), 
        object("sphere", [np.array([-3, 25, 8]), 20], luminance=1), 
        object("plane", [np.array([0, -1, 0]), np.array([0, 1, 0])], (0, 1, 0), 0)
    ]
    cam.render(objects)



if __name__ == "__main__":
    main()

