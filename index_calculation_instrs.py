from problem import VLEN

def gen_index_calculation_instrs_generic(phase, group_size, consts, tmps):
    # addr = forest_values_p + idx
    instrs = []
    # for i in range(group_size//VLEN):
        # instrs.append(("valu", ("+", tmps["addrs"][phase][i], consts["forest_values"], tmps["idxs"][phase][i])))
    return instrs 

