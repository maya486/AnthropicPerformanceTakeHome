from problem import VLEN

def gen_index_calculation_instrs(phase, forest_values, group_size, tmps):
    # addr = forest_values_p + idx
    instrs = []
    for i in range(group_size//VLEN):
        instrs.append(("valu", ("+", tmps["addrs"][phase][i], forest_values, tmps["idxs"][phase][i])))
    return instrs 
