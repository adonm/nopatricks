import commands, coord, state
from coord import Coord
from scan import Area, scan
from dataclasses import dataclass
import sys

from algorithm import shortest_path, next_move #sneaky sneaky

def move(bot, diff):
    return move_to(bot, bot.pos + diff)

def move_to(bot, dest):
    next_move(bot.state, bot, shortest_path(bot.state, bot, dest))


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
            ground_fn =  lambda k: brain.state.matrix.would_be_grounded(self.area.plane.keygen(k))
            self.targ = self.area.closest(self.targ, ground_fn)
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
        if bot.pos == Coord(0, 0, 0):
            return False
        move_to(bot, Coord(0, 0, 0))
        return True


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
        print(f"filled {self.state.matrix.nfull} / {self.state.matrix.nmodel}")
        if self.state.matrix.nfull == self.state.matrix.nmodel:
            if self.ready_to_halt():
                self.state.bots[0].halt()
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
    def parse():
        try:
            return int(sys.argv[1])
        except:
            return 1

    prob = parse()
    st = state.State.create(problem=prob)
    brain = ScanBrain(st)
    while brain.step():
        st.step()

    print(st)
    filename = "submissionScan/LA%03d.nbt" % prob
    sys.stderr.write('{}: {}\n'.format(filename, st.score) )
    print( '{}: energy: {}, default: {}, score: {:0.3f}/{:0.3f}'.format( filename, st.energy, st.default_energy, st.score, st.score_max ) )
    with open(filename, "wb") as file:
        file.write(commands.export_nbt(st.trace))




# scores (problem time/energy)
# 1 878 / 21098000
# 2 333 / 8001940
# 3  437 / 10500892
# 4 (crash; ungrounded)
# 5 1936 / 46520988
# 6 1411 / 33903292
# 7 3087 / 74179928
