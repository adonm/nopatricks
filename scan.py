#!/usr/bin/env python3

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
        plane[k].set_area_id(area.id)
        for n in plane.adjacent(k):
            if plane[n].is_model() and not any([n in a.points for a in areas]) and n not in stack:
                area.grow(n)
                stack.append(n)

