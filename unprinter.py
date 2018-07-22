import commands
from mrcrowbar import utils

def unprint(cmds):
    
    # so the real trick is keeping track of the fission and fusion commands.
    # when fissioning, the new bot is always added to the end of the buffer for each timestep
    # fusion can merge any two bots, which isn't reversible.
    # this means we have to adjust the order of the bots in the instruction buffer urgh
    # that's not too bad, we don't have to simulate the whole thing, just a wee subset

    """

1 -> 1, 2
1 wait      2 -> 2, 3
1, 2 -> 1   1, 2 -> 1   3 wait
1 wait      3 move
1, 3 -> 1   1, 3 -> 1
    
    """

    bots = [{'id': 1, 'x': 0, 'y': 0, 'z': 0}]
    bot_acc = 2
    time = 0
    changes = {}
    instructions = iter(cmds)
    end = False
    while not end:
        buffer = [next(instructions) for i in bots]
        splits = []
        merges = []
        new_bots = []
        dead_bots = []
        prims = []
        secs = []
        for i, instr in enumerate(buffer):
            klass = type(instr)
            if klass == commands.Fission:
                splits.append((bots[i]['id'], bot_acc))
                new_bots.append({'id': bot_acc, 'x': bots[i]['x']+instr.ndx, 'y': bots[i]['y']+instr.ndy, 'z': bots[i]['y']+instr.ndy})
                bot_acc += 1
            elif klass == commands.SMove:
                bots[i]['x'] += instr.lldx
                bots[i]['y'] += instr.lldy
                bots[i]['z'] += instr.lldz
            elif klass == commands.LMove:
                bots[i]['x'] += instr.sld1x+instr.sld2x
                bots[i]['y'] += instr.sld1y+instr.sld2y
                bots[i]['z'] += instr.sld1z+instr.sld2z
            elif klass == commands.FusionS:
                dead_bots.append(bots[i])
                secs.append((bots[i]['id'], (bots[i]['x']+instr.ndx, bots[i]['y']+instr.ndy, bots[i]['z']+instr.ndy)))
            elif klass == commands.FusionP:
                prims.append((bots[i]['id'], (bots[i]['x']+instr.ndx, bots[i]['y']+instr.ndy, bots[i]['z']+instr.ndy)))
            elif klass == commands.Halt:
                end = True

        for prim_id, sec_pos in prims:
            for sec_id, prim_pos in secs:
                primbot = next(b for b in bots if b['id'] == prim_id)
                secbot = next(b for b in bots if b['id'] == sec_id)
                if prim_pos == (primbot['x'], primbot['y'], primbot['z']) and sec_pos == (secbot['x'], secbot['y'], secbot['z']):
                    merges.append((prim_id, sec_id))

        bots.extend(new_bots)
        for b in dead_bots:
            bots.remove(b)
        if splits or merges:
            changes[time] = {'splits': splits, 'merges': merges}
        time += 1

    print(changes)

    map_acc = 2
    mapping = {1: 1}
    times = [t for t in changes.keys()]
    times.sort(key=lambda x: -x)
    for ts in times:
        for prim, sec in changes[ts]['merges']:
            if prim not in mapping:
                mapping[prim] = map_acc
                map_acc += 1
            if sec not in mapping:
                mapping[sec] = map_acc
                map_acc += 1

    print(mapping)

    return changes, mapping

    bots = [{'id': 1, 'x': 0, 'y': 0, 'z': 0}]
    bot_acc = 2
    time = 0
    result = []
    instructions = iter(cmds)
    while True:
        buffer = [(mapping[b['id']], next(instructions)) for b in bots]
        # replace merges with splits and vice versa
        if time in changes:
            for prim, sec in changes[time]['splits']:
                primbot = next(b for b in bots if b['id'] == prim) 
                secbot = next(b for b in bots if b['id'] == sec) 
                
                fus_inst = buffer.pop(buffer.index(key=lambda x: x[0]==mapping[prim]))
                
                buffer.append((mapping[prim], command.FusionP().set_nd() ))
                buffer.append((mapping[sec], command.FusionS().set_nd() ))
            for prim, sec in changes[time]['merges']:
                buffer.pop(buffer.index(key=lambda x: x[0]==mapping[sec]))
        buffer.sort(key=lambda x: x[0])
        
        new_bots = []
        dead_bots = []

        for bot_id, instr in buffer:
            klass = type(instr)
            # most instructions we can pass through
            if klass in (commands.Halt, commands.Wait, commands.Flip):
                result.append(instr)
            # reverse move instructions
            elif klass == commands.SMove:
                bot = next(b for b in bots if b['id'] == bot_id)
                bot['x'] += instr.lldx
                bot['y'] += instr.lldy
                bot['z'] += instr.lldz
                mod = commands.SMove().set_lld( -instr.lldx, -instr.lldy, -instr.lldz )
                result.append(mod)
            elif klass == commands.LMove:
                bot = next(b for b in bots if b['id'] == bot_id)
                bot['x'] += instr.sld1x+instr.sld2x
                bot['y'] += instr.sld1y+instr.sld2y
                bot['z'] += instr.sld1z+instr.sld2z
                mod = commands.LMove().set_sld1( -instr.sld2x, -instr.sld2y, -instr.sld2z ).set_sld2( -instr.sld1x, -instr.sld1y, -instr.sld1z )
                result.append(mod)
            # invert fill/void. offset is relative to bot pos, so remains the same
            elif klass == commands.Fill:
                mod = commands.Void().set_nd( instr.ndx, instr.ndy, instr.ndz )
                result.append(mod)
            elif klass == commands.Void:
                mod = commands.Fill().set_nd( instr.ndx, instr.ndy, instr.ndz )
                result.append(mod)
            #elif klass == commands.GFill:
            #    mod = commands.GVoid().
            #elif klass == commands.GVoid:
            #    mod = commands.GFill().
            
            elif klass in (commands.Fission, commands.FusionP, commands.FusionS):
                # we've intercepted and modified these in advance
                result.append(instr)
        
        time += 1

    """
    return
    
    

def test():
    f = open('submission/FA001.nbt', 'rb').read()
    cmds = commands.read_nbt(f)
    unprint(cmds)
