from problem import VLEN

def gen_index_calculation_instrs_generic(phase, group_size, consts, tmps):
    # addr = forest_values_p + idx
    instrs = []
    for i in range(group_size//VLEN):
        instrs.append(("valu", ("+", tmps["addrs"][phase][i], consts["forest_values"], tmps["idxs"][phase][i])))
    return instrs 

def gen_index_calculation_instrs_round_0(phase, group_size, consts, tmps):
    instrs = []
    instrs.append(("alu", ("+", tmps["addrs"][phase][0], consts["forest_values"], consts["0"])))
    instrs.append(("load", ("load", tmps["addrs"][phase][0], tmps["addrs"][phase][0])))
    for i in range(group_size//VLEN):
        for lane in range(VLEN):
            instrs.append(("alu", ("+", tmps["node_vals"][phase][i]+lane, tmps["addrs"][phase][0], consts["0"])))

    return instrs
