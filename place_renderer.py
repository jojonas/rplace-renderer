import argparse
import os, os.path
import struct

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from PIL import Image

class Place:
    width = 1000
    height = 1000
    format = struct.Struct("<IIII")
    cmap = ListedColormap([
        "#FFFFFF",
        "#E4E4E4",
        "#888888",
        "#222222",
        "#FFA7D1",
        "#E50000",
        "#E59500",
        "#A06A42",
        "#E5D900",
        "#94E044",
        "#02BE01",
        "#00D3DD",
        "#0083C7",
        "#0000EA",
        "#CF6EE4",
        "#820080"])

    def __init__(self, filename):
        self.file = open(filename, 'rb')
        self.filename = filename
        self.state = np.zeros((self.height, self.width), dtype=np.int8)
        self.step = 0
        self.t0 = 0

    def run(self, N=1):
        for i in range(int(N)):
            buffer = self.file.read(self.format.size)
            if len(buffer) < self.format.size:
                break
            data = self.format.unpack_from(buffer)
            timestamp, x, y, color = data
            if not self.t0:
                self.t0 = timestamp
            self.state[y][x] = color
            self.step += 1

            # print("Read %d steps until T = %d sec." % (N, timestamp-self.t0))

    def plot(self):
        """ Plot using matplotlib. Call plt.show() to show. """
        plt.imshow(self.state, cmap=self.cmap)
        plt.xlim(0, self.width)
        plt.ylim(self.height, 0)

    def image(self):
        """ Generate PIL-Image from current state. """
        colored_data = self.cmap(self.state)
        image = Image.fromarray(np.uint8(colored_data*255))
        return image

    def total_steps(self):
        stat = os.stat(self.filename)
        size = stat.st_size
        steps = int(size / self.format.size)
        return steps

    def __del__(self):
        self.file.close()
        self.file = None


def render_timeline(filename="diffs.bin", batch=100e3, out="."):
    if not os.path.exists(out):
        os.makedirs(out)

    place = Place(filename)
    total = place.total_steps()

    for i in range(0, int(total/batch)):
        print("Progress: %d / %d = %.1f %%" % (i*batch, total, 100.*i*batch/total))

        place.run(batch)
        image = place.image()

        image.save(os.path.join(out, "place_%03d.png" % i))

if __name__ == "__main__":
    parser = argparse.ArgumentParser("/r/place renderer")
    parser.add_argument("filename")
    parser.add_argument("--batch-size", type=int, default=100e3)
    parser.add_argument("--outdir", default=".")
    args = parser.parse_args()

    render_timeline(args.filename, batch=args.batch_size, out=args.outdir)
