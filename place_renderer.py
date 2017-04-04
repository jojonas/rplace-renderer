import argparse
import os
import struct

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


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
        for i in range(N):
            buffer = self.file.read(self.format.size)
            if len(buffer) < self.format.size:
                break
            data = self.format.unpack_from(buffer)
            timestamp, x, y, color = data
            if not self.t0:
                self.t0 = timestamp
            self.state[y][x] = color
            self.step += 1

        #print("Read %d steps until T = %d sec." % (N, timestamp-self.t0))

    def plot(self):
        plt.imshow(self.state, cmap=self.cmap)
        plt.axis("off")
        plt.gca().get_xaxis().set_visible(False)
        plt.gca().get_yaxis().set_visible(False)
        plt.xlim(0,self.width)
        plt.ylim(self.height,0)

    def total_steps(self):
        stat = os.stat(self.filename)
        size = stat.st_size
        steps = int(size / self.format.size)
        return steps

    def __del__(self):
        self.file.close()
        self.file = None


def render_timeline(filename="diffs.bin", batch=100e3):
    place = Place(filename)

    total = place.total_steps()
    for i in range(0, total, int(batch)):
        print("Progress: %d / %d" % (i,total))
        place.run(batch)
        place.plot()
        plt.savefig("place_%05dk.png" % (int(i/1000)), bbox_inches="tight", pad_inches=0)

if __name__=="__main__":
    parser = argparse.ArgumentParser("/r/place renderer")
    parser.add_argument("filename")
    parser.add_argument("--batch-size", type=int, default=100e3)
    args = parser.parse_args()

    render_timeline(args.filename, batch=args.batch_size)
