import numpy as np
from PIL import Image
import pyopencl as cl
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

        self.platform = cl.get_platforms()[0]
        self.device = self.platform.get_devices()[0]
        self.context = cl.Context([self.device])
        self.queue = cl.CommandQueue(self.context)

        with open("kernel_code.cl", "r") as f:
            self.program = cl.Program(self.context, f.read()).build()


    def render(self, preObjects):

        rays = np.array([(np.array([0., 0., 0., 0.]), np.concatenate([point/np.linalg.norm(point), [0.]]))
                         for row in self.grid for point in row],
                         dtype=[
                            ("origin", "f4", 4),
                            ("direction", "f4", 4),
                         ])
        
        objects = np.array([(
            np.int32(0 if obj.type == "sphere" else 1),
            np.float32(obj.luminance),
            np.float32(obj.radius if obj.type == "sphere" else 0),
            np.float32(obj.distance if obj.type == "plane" else 0),
            np.concatenate([obj.color, [0.0]]).astype(np.float32),
            np.concatenate([obj.emittedColor, [0.0]]).astype(np.float32),
            np.concatenate([obj.center, [0.0]]).astype(np.float32) if obj.type == "sphere" else np.zeros(4, dtype=np.float32),
            np.concatenate([obj.normal, [0.0]]).astype(np.float32) if obj.type == "plane" else np.zeros(4, dtype=np.float32),
        ) for obj in preObjects],
        dtype=np.dtype([
            ("type", "i4"),
            ("luminance", "f4"),
            ("radius", "f4"),
            ("distance", "f4"),
            ("color", "f4", 4),
            ("emittedColor", "f4", 4),
            ("center", "f4", 4),
            ("normal", "f4", 4),
        ], align=True))


        results = np.zeros(len(rays), dtype=np.dtype("f4, f4, f4, f4"))
        
        mf = cl.mem_flags
        rays_buf = cl.Buffer(self.context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=rays)
        objects_buf = cl.Buffer(self.context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=objects)
        results_buf = cl.Buffer(self.context, mf.WRITE_ONLY, results.nbytes)


        self.program.intersect(self.queue, (len(rays),), None, rays_buf, objects_buf, np.int32(len(objects)), results_buf)

        cl.enqueue_copy(self.queue, results, results_buf)

        img = Image.new('RGB', (self.width, self.height))
        pixels = img.load()

        for i, (r, g, b, _) in enumerate(results):
            x, y = i % self.width, i // self.width
            # print(x, y)
            # print(r, g, b)
            pixels[self.width-x-1, self.height-y-1] = tuple((int(r*255), int(g*255), int(b*255)))

        img.save('render.png')


class object:
    def __init__(self, type, params, color = (1, 1, 1), emittedColor = (1, 1, 1), luminance = 0):
        self.type = type
        self.color = np.array(color, dtype=np.float32)
        self.emittedColor = np.array(emittedColor, dtype=np.float32)
        self.luminance = luminance
        if type == "sphere": # ensidig
            self.center = np.array(params[0], dtype=np.float32)
            self.radius = params[1]
        elif type == "plane": # ensidig
            # self.point = np.array(params[0], dtype=float)
            self.normal = np.array(params[1], dtype=np.float32)
            self.distance = np.dot(params[0], self.normal)
        # elif type == "triangle":
        #     self.vertices = params
        else:
            raise Exception("Object does not exist")
        

def main():
    width, height = 192*2, 108*2
    # width, height = 50, 40
    cam = camera(width, height)
    objects = [
        object("sphere", [np.array([0, 0, 4]), 1.], (1, 0, 0)), 
        object("sphere", [np.array([1.1, 0, 4.5]), .5], (.3, 0, 1)), 
        object("sphere", [np.array([-9, 25, 14]), 20.], luminance=1), 
        object("plane", [np.array([0, -1, 0]), np.array([0, 1, 0])], (0, 1, 0))
    ]
    cam.render(objects)


if __name__ == "__main__":
    starttime = time.time()
    main()
    print(f"Render time: {time.time()-starttime:.2f}s")
    

