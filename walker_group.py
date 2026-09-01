from problem import VLEN


def gen_write_out_instrs(walker_idx_idx, phase, group_size, tmps, consts):
    walker_group_epilogue = []

    # mem[inp_indices_p + i] = idx

    # tmp_addr = inp_indices_p + i
    for i in range(group_size//VLEN):
        walker_group_epilogue.append(("alu", ("+", tmps["1s"][phase][i], consts["inp_indices_p"], consts["walker_idxs"][walker_idx_idx][phase][i])))

    # addrs -> idxs (-= root addr offset)
    for i in range(group_size//VLEN):
        walker_group_epilogue.append(("valu", ("-", tmps["addrs"][phase][i], tmps["addrs"][phase][i], consts["forest_values"])))

    # mem[tmp_addr] = idxs
    for i in range(group_size//VLEN):
        walker_group_epilogue.append(("store", ("vstore", tmps["1s"][phase][i], tmps["addrs"][phase][i])))

    # mem[inp_values_p + i] = val

    # tmp_addr = inp_values_p + i
    for i in range(group_size//VLEN):
        walker_group_epilogue.append(("alu", ("+", tmps["1s"][phase][i], consts["inp_values_p"], consts["walker_idxs"][walker_idx_idx][phase][i])))

    # mem[tmp_addr] = val
    for i in range(group_size//VLEN):
        walker_group_epilogue.append(("store", ("vstore", tmps["1s"][phase][i], tmps["vals"][phase][i])))

    return walker_group_epilogue


def gen_read_in_instrs(walker_idx_idx, phase, group_size, tmps, consts):
    walker_group_prologue = []

    # val = mem[inp_values_p + i]

    # tmp_addr = inp_values_p + i
    for i in range(group_size//VLEN):
        walker_group_prologue.append(("alu", ("+", tmps["addrs"][phase][i], consts["inp_values_p"], consts["walker_idxs"][walker_idx_idx][phase][i])))

    # val = mem[tmp_addr]
    for i in range(group_size//VLEN):
        walker_group_prologue.append(("load", ("vload", tmps["vals"][phase][i], tmps["addrs"][phase][i])))

    # setup addr to be addr of root
    for i in range(group_size//VLEN):
        walker_group_prologue.append(("valu", ("vbroadcast", tmps["addrs"][phase][i], consts["forest_values"])))

    return walker_group_prologue

