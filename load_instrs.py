from problem import VLEN


def gen_load_instrs(load_round, load_phase, global_round, group_size, consts, tmps):

    if global_round == 0:
        return gen_load_instrs_round_0_with_valu(load_phase, group_size, consts, tmps)
    elif load_round == 0 or load_round == 11:
        return gen_load_instrs_round_0(load_phase, group_size, consts, tmps)
    elif load_round == 1 or load_round == 12:
        return gen_load_instrs_round_1(load_phase, load_round, group_size, consts, tmps)
    elif load_round == 2 or load_round == 13:
        return gen_load_instrs_round_2(load_phase, group_size, consts, tmps)
    elif load_round == 3 or load_round == 14:
        return gen_load_instrs_round_3(load_phase, group_size, consts, tmps)
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


def gen_load_instrs_round_1(phase, load_round, group_size, consts, tmps):

    instrs = []

    if load_round == 1 and phase in [0, 1]:
        # select which node val (preloaded in setup) based on val parity
        for i in range(group_size//VLEN):
            instrs.append(("valu", ("multiply_add", tmps["node_vals"][phase][i], tmps["b0s"][phase][i], consts["v3_minus_v2"], consts["v2"])))
    else:
        for i in range(group_size//VLEN):
            instrs.append(("flow", ("vselect", tmps["node_vals"][phase][i], tmps["b0s"][phase][i], consts["v3"], consts["v2"])))


    return instrs


def gen_load_instrs_round_2(phase, group_size, consts, tmps):

    instrs = []

    for i in range(group_size//VLEN):
        instrs.append(("flow", ("vselect", tmps["3s"][0], tmps["b0s"][phase][i], consts["v6"], consts["v4"])))
        instrs.append(("flow", ("vselect", tmps["3s"][1], tmps["b0s"][phase][i], consts["v7"], consts["v5"])))
        instrs.append(("flow", ("vselect", tmps["node_vals"][phase][i], tmps["b1s"][phase][i], tmps["3s"][1], tmps["3s"][0])))

    return instrs


def gen_load_instrs_round_3(phase, group_size, consts, tmps):

    instrs = []

    for i in range(group_size//VLEN):
        instrs.append(("flow", ("vselect", tmps["3s"][2], tmps["b0s"][phase][i], consts["v12"], consts["v8"])))
        instrs.append(("flow", ("vselect", tmps["3s"][3], tmps["b0s"][phase][i], consts["v13"], consts["v9"])))
        instrs.append(("flow", ("vselect", tmps["3s"][4], tmps["b0s"][phase][i], consts["v14"], consts["v10"])))
        instrs.append(("flow", ("vselect", tmps["3s"][5], tmps["b0s"][phase][i], consts["v15"], consts["v11"])))
        instrs.append(("flow", ("vselect", tmps["3s"][6], tmps["b1s"][phase][i], tmps["3s"][4], tmps["3s"][2])))
        instrs.append(("flow", ("vselect", tmps["3s"][7], tmps["b1s"][phase][i], tmps["3s"][5], tmps["3s"][3])))
        instrs.append(("flow", ("vselect", tmps["node_vals"][phase][i], tmps["val_paritys"][phase][i], tmps["3s"][7], tmps["3s"][6])))

    return instrs

