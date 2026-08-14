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

def gen_load_instrs_round_11(phase, group_size, consts, tmps):
    instrs = []

    # load root into tmp reg
    instrs.append(("load", ("load", tmps["3s"][0], consts["forest_values"])))

    for i in range(group_size//VLEN):
        for lane in range(VLEN):
            instrs.append(("alu", ("+", tmps["node_vals"][phase][i]+lane, tmps["3s"][0], consts["0"])))

    return instrs

def gen_load_instrs_round_1(phase, group_size, consts, tmps):
    instrs = []

    # index instrs for 2 nodes
    instrs.append(("alu", ("+", tmps["3s"][0], consts["forest_values"], consts["1"])))
    instrs.append(("alu", ("+", tmps["3s"][1], consts["forest_values"], consts["2"])))

    # load 2 nodes
    instrs.append(("load", ("load", tmps["3s"][2], tmps["3s"][0])))
    instrs.append(("load", ("load", tmps["3s"][3], tmps["3s"][1])))

    for i in range(group_size//VLEN):
        for lane in range(VLEN):
            instrs.append(("alu", ("-", tmps["4s"][phase][i]+lane, tmps["idxs"][phase][i]+lane, consts["1"])))

    for i in range(group_size//VLEN):
        instrs.append(("flow", ("vselect", tmps["node_vals"][phase][i], tmps["4s"][phase][i], tmps["3s"][3], tmps["3s"][2])))


    return instrs

