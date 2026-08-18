from problem import VLEN

def gen_hash_and_update_instrs_generic(round, phase, forest_height, group_size, tmps, hash_consts):
    instrs = []

    # val = myhash(val ^ node_val)

    for i in range(group_size//VLEN):
        instrs.append(("valu", ("^", tmps["vals"][phase][i], tmps["vals"][phase][i], tmps["node_vals"][phase][i])))

    # stage 1
    for i in range(group_size//VLEN):
        instrs.append(("valu", ("+", tmps["1s"][phase][i], tmps["vals"][phase][i], hash_consts["0x7ED55D16"])))
    for i in range(group_size//VLEN):
        instrs.append(("valu", ("multiply_add", tmps["vals"][phase][i], tmps["vals"][phase][i], hash_consts["4096"], tmps["1s"][phase][i])))

    # stage 2
    for i in range(group_size//VLEN):
        instrs.append(("valu", ("^", tmps["1s"][phase][i], tmps["vals"][phase][i], hash_consts["0xC761C23C"])))
    for i in range(group_size//VLEN):
        instrs.append(("valu", (">>", tmps["2s"][phase][i], tmps["vals"][phase][i], hash_consts["19"])))
    for i in range(group_size//VLEN):
        instrs.append(("valu", ("^", tmps["vals"][phase][i], tmps["1s"][phase][i], tmps["2s"][phase][i])))

    # stage 3
    for i in range(group_size//VLEN):
        instrs.append(("valu", ("+", tmps["1s"][phase][i], tmps["vals"][phase][i], hash_consts["0x165667B1"])))
    for i in range(group_size//VLEN):
        instrs.append(("valu", ("multiply_add", tmps["vals"][phase][i], tmps["vals"][phase][i], hash_consts["32"], tmps["1s"][phase][i])))

    # stage 4
    for i in range(group_size//VLEN):
        instrs.append(("valu", ("+", tmps["1s"][phase][i], tmps["vals"][phase][i], hash_consts["0xD3A2646C"])))
    for i in range(group_size//VLEN):
        instrs.append(("valu", ("<<", tmps["2s"][phase][i], tmps["vals"][phase][i], hash_consts["9"])))
    for i in range(group_size//VLEN):
        instrs.append(("valu", ("^", tmps["vals"][phase][i], tmps["1s"][phase][i], tmps["2s"][phase][i])))

    # stage 5
    for i in range(group_size//VLEN):
        instrs.append(("valu", ("+", tmps["1s"][phase][i], tmps["vals"][phase][i], hash_consts["0xFD7046C5"])))
    for i in range(group_size//VLEN):
        instrs.append(("valu", ("multiply_add", tmps["vals"][phase][i], tmps["vals"][phase][i], hash_consts["8"], tmps["1s"][phase][i])))

        # stage 6
    for i in range(group_size//VLEN):
        instrs.append(("valu", ("^", tmps["1s"][phase][i], tmps["vals"][phase][i], hash_consts["0xB55A4F09"])))
    for i in range(group_size//VLEN):
        instrs.append(("valu", (">>", tmps["2s"][phase][i], tmps["vals"][phase][i], hash_consts["16"])))
    for i in range(group_size//VLEN):
        instrs.append(("valu", ("^", tmps["vals"][phase][i], tmps["1s"][phase][i], tmps["2s"][phase][i])))

    # update index to next tree level or loop back up
    if round == forest_height:
        # idx = 0
        for i in range(group_size//VLEN):
            instrs.append(("valu", ("&", tmps["idxs"][phase][i], tmps["idxs"][phase][i], hash_consts["0"])));
    else:

        # idx = 2*idx + 1 + val&1

        # if at root need to record the parity into b0 for later level 2 optimization (see gen_load_instrs_round_2)
        if round == 0 or round == 11:

            for i in range(group_size//VLEN):
                instrs.append(("valu", ("&", tmps["b0s"][phase][i], tmps["vals"][phase][i], hash_consts["1"])));
            for i in range(group_size//VLEN):
                instrs.append(("valu", ("multiply_add", tmps["idxs"][phase][i], tmps["idxs"][phase][i], hash_consts["2"], hash_consts["1"])))
            for i in range(group_size//VLEN):
                instrs.append(("valu", ("+", tmps["idxs"][phase][i], tmps["idxs"][phase][i], tmps["b0s"][phase][i])))

        else:

            for i in range(group_size//VLEN):
                instrs.append(("valu", ("&", tmps["val_paritys"][phase][i], tmps["vals"][phase][i], hash_consts["1"])));
            for i in range(group_size//VLEN):
                instrs.append(("valu", ("multiply_add", tmps["idxs"][phase][i], tmps["idxs"][phase][i], hash_consts["2"], hash_consts["1"])))
            for i in range(group_size//VLEN):
                instrs.append(("valu", ("+", tmps["idxs"][phase][i], tmps["idxs"][phase][i], tmps["val_paritys"][phase][i])))

    return instrs 

