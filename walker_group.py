from problem import VLEN


def gen_write_out_walker_group_instrs(walker_idx_idx, num_phases, group_size, tmps, consts):
    walker_group_epilogue = []

    # mem[inp_indices_p + i] = idx
    # mem[inp_values_p + i] = val
    for phase in range(num_phases):
        for i in range(group_size//VLEN):
            walker_group_epilogue.append(("alu", ("+", tmps["addrs"][phase][i], consts["inp_indices_p"], consts["walker_idxs"][walker_idx_idx][phase][i])))

    for phase in range(num_phases):
        for i in range(group_size//VLEN):
            walker_group_epilogue.append(("store", ("vstore", tmps["addrs"][phase][i], tmps["idxs"][phase][i])))

    for phase in range(num_phases):
        for i in range(group_size//VLEN):
            walker_group_epilogue.append(("alu", ("+", tmps["addrs"][phase][i], consts["inp_values_p"], consts["walker_idxs"][walker_idx_idx][phase][i])))

    for phase in range(num_phases):
        for i in range(group_size//VLEN):
            walker_group_epilogue.append(("store", ("vstore", tmps["addrs"][phase][i], tmps["vals"][phase][i])))

    return walker_group_epilogue


def gen_read_in_walker_group_instrs(walker_idx_idx, num_phases, group_size, tmps, consts):
    walker_group_prologue = []

    # idx = mem[inp_indices_p + i]
    # val = mem[inp_values_p + i]
    for phase in range(num_phases):
        for i in range(group_size//VLEN):
            walker_group_prologue.append(("alu", ("+", tmps["addrs"][phase][i], consts["inp_indices_p"], consts["walker_idxs"][walker_idx_idx][phase][i])))

    for phase in range(num_phases):
        for i in range(group_size//VLEN):
            walker_group_prologue.append(("load", ("vload", tmps["idxs"][phase][i], tmps["addrs"][phase][i])))

    for phase in range(num_phases):
        for i in range(group_size//VLEN):
            walker_group_prologue.append(("alu", ("+", tmps["addrs"][phase][i], consts["inp_values_p"], consts["walker_idxs"][walker_idx_idx][phase][i])))

    for phase in range(num_phases):
        for i in range(group_size//VLEN):
            walker_group_prologue.append(("load", ("vload", tmps["vals"][phase][i], tmps["addrs"][phase][i])))


    return walker_group_prologue

