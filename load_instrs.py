from problem import VLEN

def gen_load_instrs_generic(phase, group_size, tmps):

    # node_val = mem[addr]
    instrs = []
    for i in range(group_size//VLEN):
        for lane in range(VLEN):
            instrs.append(("load", ("load", tmps["node_vals"][phase][i]+lane, tmps["addrs"][phase][i]+lane)))
    return instrs 


def gen_load_instrs_round_0(phase, group_size, consts, tmps):
    instrs = []

    # load root into tmp reg
    instrs.append(("load", ("load", tmps["3s"][0], consts["forest_values"])))

    # can vbroadcast because for round 0 this is prologue of pipeline so no concurrent hash stuff
    for i in range(group_size//VLEN):
        instrs.append(("valu", ("vbroadcast", tmps["node_vals"][phase][i], tmps["3s"][0])))

    return instrs

def gen_load_instrs_round_1(phase, group_size, consts, tmps):
    instrs = []

    # load root into tmp reg
    instrs.append(("load", ("load", tmps["3s"][0], consts["forest_values"])))

    # can vbroadcast because for round 0 this is prologue of pipeline so no concurrent hash stuff
    for i in range(group_size//VLEN):
        instrs.append(("valu", ("vbroadcast", tmps["node_vals"][phase][i], tmps["3s"][0])))

    return instrs
