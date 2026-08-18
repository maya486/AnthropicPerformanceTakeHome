from problem import VLEN

def gen_load_instrs_generic(phase, group_size, tmps):

    # node_val = mem[addr]
    instrs = []
    for i in range(group_size//VLEN):
        for lane in range(VLEN):
            instrs.append(("load", ("load", tmps["node_vals"][phase][i]+lane, tmps["addrs"][phase][i]+lane)))
    return instrs 


def gen_load_instrs_round_0_with_valu(phase, group_size, consts, tmps):
    instrs = []

    # load root into tmp reg
    instrs.append(("load", ("load", tmps["3s"][0], consts["forest_values"])))

    # can vbroadcast because for round 0 this is prologue of pipeline so no concurrent hash stuff
    for i in range(group_size//VLEN):
        instrs.append(("valu", ("vbroadcast", tmps["node_vals"][phase][i], tmps["3s"][0])))

    return instrs

def gen_load_instrs_round_0(phase, group_size, consts, tmps):
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
    instrs.append(("load", ("load", tmps["3s"][8], tmps["3s"][0])))
    instrs.append(("load", ("load", tmps["3s"][16], tmps["3s"][1])))
    for lane in range(1, VLEN):
        instrs.append(("alu", ("+", tmps["3s"][8]+lane, tmps["3s"][8], consts["0"])))
        instrs.append(("alu", ("+", tmps["3s"][16]+lane, tmps["3s"][16], consts["0"])))


    for i in range(group_size//VLEN):
        for lane in range(VLEN):
            instrs.append(("alu", ("-", tmps["1s"][phase][i]+lane, tmps["idxs"][phase][i]+lane, consts["1"])))

    for i in range(group_size//VLEN):
        instrs.append(("flow", ("vselect", tmps["node_vals"][phase][i], tmps["1s"][phase][i], tmps["3s"][16], tmps["3s"][8])))


    return instrs


def gen_load_instrs_round_2(phase, group_size, consts, tmps):

    instrs = []

    for i in range(group_size//VLEN):
        instrs.append(("flow", ("vselect", tmps["3s"][0], tmps["b0s"][phase][i], consts["v6"], consts["v4"])))
        instrs.append(("flow", ("vselect", tmps["3s"][8], tmps["b0s"][phase][i], consts["v7"], consts["v5"])))
        instrs.append(("flow", ("vselect", tmps["node_vals"][phase][i], tmps["val_paritys"][phase][i], tmps["3s"][8], tmps["3s"][0])))

    return instrs

