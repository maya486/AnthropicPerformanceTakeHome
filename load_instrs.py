from problem import VLEN


def gen_load_instrs(load_round, load_phase, global_round, group_size, consts, tmps):

    if global_round == 0:
        return gen_load_instrs_round_0_with_valu(load_phase, group_size, consts, tmps)
    elif load_round == 0 or load_round == 11:
        return gen_load_instrs_round_0(load_phase, group_size, consts, tmps)
    elif load_round == 1 or load_round == 12:
        return gen_load_instrs_round_1(load_phase, group_size, consts, tmps)
    elif load_round == 2 or load_round == 13:
        return gen_load_instrs_round_2(load_phase, group_size, consts, tmps)
    else:
        return gen_load_instrs_generic(load_phase, group_size, tmps)
        

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

    # pseudo broadcast by just doing node_val = root_val*1
    for i in range(group_size//VLEN):
        for lane in range(VLEN):
            instrs.append(("alu", ("*", tmps["node_vals"][phase][i]+lane, tmps["3s"][0], consts["1"])))

    return instrs


def gen_load_instrs_round_1(phase, group_size, consts, tmps):

    instrs = []

    # select which node val (preloaded in setup) based on val parity
    for i in range(group_size//VLEN):
        instrs.append(("flow", ("vselect", tmps["node_vals"][phase][i], tmps["b0s"][phase][i], consts["v3"], consts["v2"])))

    return instrs


def gen_load_instrs_round_2(phase, group_size, consts, tmps):

    instrs = []

    # select which node val (preloaded in setup) through decision tree structure based on val parity of 1st and 2nd iter
    for i in range(group_size//VLEN):
        instrs.append(("flow", ("vselect", tmps["3s"][0], tmps["b0s"][phase][i], consts["v6"], consts["v4"])))
        instrs.append(("flow", ("vselect", tmps["3s"][8], tmps["b0s"][phase][i], consts["v7"], consts["v5"])))
        instrs.append(("flow", ("vselect", tmps["node_vals"][phase][i], tmps["val_paritys"][phase][i], tmps["3s"][8], tmps["3s"][0])))

    return instrs

