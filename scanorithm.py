import commands, coord, state
from coord import Coord
from scan import Area, scan
from dataclasses import dataclass


def move(bot, diff):
    if diff.dy != 0:
        return bot.smove(coord.LongDiff(0, max(-15, min(diff.dy, 15)), 0))
    elif diff.dx != 0:
        return bot.smove(coord.LongDiff(max(-15, min(diff.dx, 15)), 0, 0))
    else:
        return bot.smove(coord.LongDiff(0, 0, max(-15, min(diff.dz, 15))))


class FillArea:
    def __init__(self, area):
        self.area = area
        self.targ = area.anchor #TODO find nearest groundable square

    def step(self, brain, bot):
        if self.targ is None:
            #move to next layer
            bot.smove(coord.LongDiff(0, brain.dir, 0))
            return False
        diff = self.area.plane.keygen(self.targ) - bot.pos
        if isinstance(diff, coord.NearDiff):
            #print(f"fill {self.targ}")
            self.area.points.remove(self.targ)
            self.targ = self.area.closest(self.targ)
            bot.fill(diff)
        else:
            # try to move to the spot above our target
            move(bot, (self.area.plane.keygen(self.targ) + coord.LongDiff(0, brain.dir, 0)) - bot.pos)
        return True


@dataclass
class SpawnBot:
    towards: Coord
    retainSeeds: float # fraction


@dataclass
class HeadHome:
    def step(self, brain, bot):
        return False


class ScanBrain:
    def __init__(self, state):
        self.state = state
        self.y = 0
        self.dir = 1
        self.prev_ground = lambda x : True

        self.active = {}
        self.pending = []


    def num_jobs(self):
        return len(self.active) + len(self.pending)


    def plan(self):
        assert self.num_jobs() == 0
        pts_limit = 999999 #self.state.R * self.state.R / 20.0 / 2.0
        plane = self.state.matrix.yplane(self.y)
        areas = scan(plane, self.prev_ground, pts_limit)
        print(f"Found {len(areas)} area(s) @ y={self.y}\n" + "\n".join(map(repr, areas)))
        if len(areas) == 0 and sum([int(v.is_model()) for v in plane.values()]) == 0:
            self.dir = -self.dir
        #if len(areas) > 20:
        #    raise Exception("TODO merge areas together")
        #TODO fission if more bots required
        id = 1
        while len(self.active) < 20 and len(areas) > 0:
            # TODO assign jobs to nearest bots instead of sequentially
            self.active[id] = FillArea(areas.pop())
            id += 1
        self.pending = list(map(FillArea, areas))


    def step(self):
        if self.num_jobs() == 0:
            self.plan()

        if any([self.step_bot(bot) for bot in self.state.bots]) or self.num_jobs() != 0:
            return True

        # no bots are busy; what's next?
        print(f"filled {self.state.matrix.nfull} / {self.state.matrix.num_modelled}")
        if self.state.matrix.nfull == self.state.matrix.nmodel:
            if self.ready_to_halt():
                return False
            for i in range(1, 21):
                self.active[i] = HeadHome()
        else:
            prevy = self.y
            self.y += self.dir
            if not self.state.matrix.in_range(self.y):
                self.dir = -self.dir
                self.y = prevy + self.dir
            print(f"move to y={self.y}")
            self.prev_ground = lambda k: self.state.matrix.yplane(prevy)[k].is_grounded()
            print(f"{self.state.matrix.yplane(prevy)}")
        return True


    def ready_to_halt(self):
        return len(self.state.bots) == 1 and self.state.bots[0].pos == Coord(0, 0, 0) \
                and self.state.harmonics == False


    def step_bot(self, bot):
        # Each bot is responsible for jobs assigned to it or its seeds
        for id in [bot.bid] + bot.seeds:
            if id in self.active:
                more_work = self.active[id].step(self, bot)
                if not more_work:
                    del self.active[id]
                return more_work
        bot.wait()
        return False


if __name__ == '__main__':
    prob = 1
    try:
        prob = int(sys.argv[0])
    except:
        pass
    st = state.State.create(problem=prob)
    brain = ScanBrain(st)
    i = 1500
    while brain.step():
        st.step()
        i -= 1
        if i == 0:
            break

    print(st)

    with open("test%03d.nbt" % prob, "wb") as file:
        file.write(commands.export_nbt(st.trace))
