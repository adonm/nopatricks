#!/usr/bin/env python3

from abc import ABC, abstractmethod
from math import ceil

# Note Area doesn't define the type of coordinates; it happily works with Coord or tuples
class Area:
    def __init__(self, id, coord):
        self.id = id # 1-based
        self.points = set()
        self.points.add(coord)
        self.min = list(coord)
        self.max = list(coord)

    def grow(self, coord):
        self.points.add(coord)
        for i in range(len(coord)):
            self.min[i] = min(self.min[i], coord[i])
            self.max[i] = max(self.max[i], coord[i])

# grounded_fn returns true for a given plane coord if it is fillable while staying grounded
def scan(plane, grounded_fn):
    areas = []
    for k in plane:
        if plane[k].is_model() and grounded_fn(k) and not any([k in a.points for a in areas]):
            area = Area(len(areas) + 1, k)
            areas.append(area)
            flood_fill(plane, areas, area, k)
    return areas

def flood_fill(plane, areas, area, start):
    stack = [start]
    while len(stack) > 0:
        k = stack.pop()
        for n in plane.adjacent(k):
            if plane[n].is_model() and not any([n in a.points for a in areas]) and n not in stack:
                area.grow(n)
                stack.append(n)




# Partitioner is supposed to break large Areas up into smaller Areas suitable for one bot
# Might be useful later but I realised it's probably simpler to prevent scan/fill from creating
# large areas in the first place.
class Partitioner(ABC):
    @abstractmethod
    def partition_area(plane, area, subdivisions):
        pass


class PartitionSquares(Partitioner):
    def __init__(self, R):
        # arbitrary hueristic
        self.target_pts_per_bot = (R * R) / 20.0 / 2.0

    def partition(plane, areas):
        jobs = []
        total_pts = sum([len(a.points) for a in areas])
        split = min(int(total_pts / self.target_pts_per_bot), 20)
        pts_per_job = total_pts / split
        for area in areas:
            if len(area.points) / float(pts_per_job) < 1.25:
                # small area; queue it up and disregard
                jobs.add(area)
                split -= 1
                total_pts -= len(area.points)
                pts_per_job = total_pts / split

        for area in areas:
            if area not in jobs:
                sub_areas = partition_area(plane, area, ceil(len(area.points) / pts_per_job))
                jobs.extend(sub_areas)

        return jobs
