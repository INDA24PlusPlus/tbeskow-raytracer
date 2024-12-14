import numpy as np
from PIL import Image
from multiprocessing import Pool, cpu_count
from functools import partial
import time

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

    def processPixel(self, coord, objects):
        x, y = coord
        point = self.grid[y][x]
        result = np.array([0, 0, 0], dtype=float)
        amount = 30
        for _ in range(amount):
            r = ray(np.array([0, 0, 0]), point/np.linalg.norm(point))
            result += r.trace(objects)
        return self.width-x-1, self.height-y-1, tuple((result/amount*255).astype(int)) 

    def render(self, objects, amountProcesses = cpu_count()):

        coords = [[x, y] for x in range(self.width) for y in range(self.height)]
        pixelFunc = partial(self.processPixel, objects=objects)
            
        print(f"Processes: {amountProcesses}")
        with Pool(processes=amountProcesses) as pool:
            res = pool.map(pixelFunc, coords)

        img = Image.new('RGB', (self.width, self.height))
        pixels = img.load()
        for x, y, color in res: pixels[x, y] = color

        img.save('render.png')
        

class object:
    def __init__(self, type, params, color = (1, 1, 1), emittedColor = (1, 1, 1), luminance = 0):
        self.type = type
        self.color = np.array(color, dtype=float)
        self.emittedColor = np.array(emittedColor, dtype=float)
        self.luminance = luminance
        if type == "sphere": # ensidig
            self.center = np.array(params[0], dtype=float)
            self.radius = np.array(params[1], dtype=float)
        elif type == "plane": # ensidig
            # self.point = np.array(params[0], dtype=float)
            self.normal = np.array(params[1], dtype=float)
            self.distance = np.dot(params[0], self.normal)
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
        for _ in range(depth):
            result, distance = self.intersect(objects)
            if result == None: break
            self.origin+=self.direction*distance
            self.direction = self.randomDirection(self.findNormal(result))

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
                dist = self.intersect_plane(object.normal, object.distance)
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
        toRoot = b**2-4*a*c
        if toRoot < 0: return -1
        return (-b-np.sqrt(toRoot))/(2*a)
    
    def intersect_plane(self, N, distance):
        scalar = np.dot(self.direction, N)
        if scalar == 0: return -1
        return (distance-np.dot(self.origin, N))/scalar
    

def main():
    width, height = 192, 108
    # width, height = 50, 40
    cam = camera(width, height)
    objects = [
        object("sphere", [np.array([0, 0, 4]), 1], (1, 0, 0), 0), 
        object("sphere", [np.array([1.1, 0, 4.5]), .5], (.3, 0, 1), 0), 
        object("sphere", [np.array([-9, 25, 14]), 20], luminance=1), 
        object("plane", [np.array([0, -1, 0]), np.array([0, 1, 0])], (0, 1, 0), 0)
    ]
    cam.render(objects, amountProcesses=8)


if __name__ == "__main__":
    starttime = time.time()
    main()
    print(f"Render time: {time.time()-starttime:.2f}s")
    

