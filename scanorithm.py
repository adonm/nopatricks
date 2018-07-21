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


@dataclass
class FillArea:
    area: Area
    targ: Coord=None  # TODO find nearest groundable square on construction

    def step(self, brain, bot):
        if self.targ is None:
            self.targ = self.area.plane.keygen(self.area.anchor)
        diff = self.targ - bot.pos
        if isinstance(diff, coord.NearDiff):
            # self.targ = TODO neighbour of current targ
            self.area.points.remove(self.targ)
            bot.fill(diff)
        else:
            move(bot, (self.targ + coord.UP) - bot.pos)
        return True


@dataclass
class SpawnBot:
    towards: Coord
    retainSeeds: float # fraction


@dataclass
class HeadHome:
    pass


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
        pts_limit = self.state.R * self.state.R / 20.0 / 2.0
        areas = scan(self.state.matrix.yplane(self.y), self.prev_ground, pts_limit)
        print(f"Found {len(areas)} area(s)\n" + "\n".join(map(repr, areas)))
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

        if any([self.step_bot(bot) for bot in self.state.bots]):
            return True

        # no bots are busy; what's next?
        if self.state.matrix.num_full == self.state.matrix.num_modelled:
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
            self.prev_ground = lambda k: self.state.matrix.yplane(prevy)[k].is_grounded()
        return True


    def ready_to_halt():
        return len(self.state.bots) == 1 and self.state.bots[0].pos == Coord(0, 0, 0) \
                and self.state.harmonics == False


    def step_bot(self, bot):
        # Each bot is responsible for jobs assigned to it or its seeds
        for id in [bot.bid] + bot.seeds:
            if id in self.active:
                more_work = self.active[id].step(self, bot)
                if not more_work:
                    del self.active[id]
                return True
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
    while brain.step():
        pass

    with open("test%03d.nbt" % prob, "wb") as file:
        file.write(commands.export_nbt(st.trace))
