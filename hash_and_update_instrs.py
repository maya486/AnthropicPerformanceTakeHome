from problem import VLEN

def gen_hash_and_update_instrs_generic(round, phase, forest_height, group_size, tmps, hash_consts):
    instrs = []

    # one group uses the alu instead of the valu
    # num_valu_groups = (group_size//VLEN) - 1
    num_valu_groups = (group_size//VLEN)
    alu_group = num_valu_groups - 1

    # val = val ^ node_val

    for i in range(num_valu_groups-1):
        instrs.append(("valu", ("^", tmps["vals"][phase][i], tmps["vals"][phase][i], tmps["node_vals"][phase][i])))
    for lane in range(VLEN):
        instrs.append(("alu", ("^", tmps["vals"][phase][alu_group]+lane, tmps["vals"][phase][alu_group]+lane, tmps["node_vals"][phase][alu_group]+lane)))

    # the hash function has 6 stages

    # stage 1
    for i in range(num_valu_groups-1):
        instrs.append(("valu", ("+", tmps["1s"][phase][i], tmps["vals"][phase][i], hash_consts["0x7ED55D16"])))
    for lane in range(VLEN):
        instrs.append(("alu", ("+", tmps["1s"][phase][alu_group]+lane, tmps["vals"][phase][alu_group]+lane, hash_consts["0x7ED55D16"])))

    for i in range(num_valu_groups-1):
        instrs.append(("valu", ("multiply_add", tmps["vals"][phase][i], tmps["vals"][phase][i], hash_consts["4096"], tmps["1s"][phase][i])))
    for lane in range(VLEN):
        instrs.append(("alu", ("*", tmps["vals"][phase][alu_group]+lane, tmps["vals"][phase][alu_group]+lane, hash_consts["4096"])))
        instrs.append(("alu", ("+", tmps["vals"][phase][alu_group]+lane, tmps["vals"][phase][alu_group]+lane, tmps["1s"][phase][alu_group]+lane)))

    # stage 2
    for i in range(num_valu_groups-1):
        instrs.append(("valu", ("^", tmps["1s"][phase][i], tmps["vals"][phase][i], hash_consts["0xC761C23C"])))
    for lane in range(VLEN):
        instrs.append(("alu", ("^", tmps["1s"][phase][alu_group]+lane, tmps["vals"][phase][alu_group]+lane, hash_consts["0xC761C23C"])))

    for i in range(num_valu_groups-1):
        instrs.append(("valu", (">>", tmps["2s"][phase][i], tmps["vals"][phase][i], hash_consts["19"])))
    for lane in range(VLEN):
        instrs.append(("alu", (">>", tmps["2s"][phase][alu_group]+lane, tmps["vals"][phase][alu_group]+lane, hash_consts["19"])))

    for i in range(num_valu_groups-1):
        instrs.append(("valu", ("^", tmps["vals"][phase][i], tmps["1s"][phase][i], tmps["2s"][phase][i])))
    for lane in range(VLEN):
        instrs.append(("alu", ("^", tmps["vals"][phase][alu_group]+lane, tmps["1s"][phase][alu_group]+lane, tmps["2s"][phase][alu_group]+lane)))

    # stage 3
    for i in range(num_valu_groups-1):
        instrs.append(("valu", ("+", tmps["1s"][phase][i], tmps["vals"][phase][i], hash_consts["0x165667B1"])))
    for lane in range(VLEN):
        instrs.append(("alu", ("+", tmps["1s"][phase][alu_group]+lane, tmps["vals"][phase][alu_group]+lane, hash_consts["0x165667B1"])))

    for i in range(num_valu_groups):
        instrs.append(("valu", ("multiply_add", tmps["vals"][phase][i], tmps["vals"][phase][i], hash_consts["32"], tmps["1s"][phase][i])))
    # for lane in range(VLEN):
        # instrs.append(("alu", ("*", tmps["vals"][phase][alu_group]+lane, tmps["vals"][phase][alu_group]+lane, hash_consts["32"])))
        # instrs.append(("alu", ("+", tmps["vals"][phase][alu_group]+lane, tmps["vals"][phase][alu_group]+lane, tmps["1s"][phase][alu_group]+lane)))

    # stage 4
    for i in range(num_valu_groups):
        instrs.append(("valu", ("+", tmps["1s"][phase][i], tmps["vals"][phase][i], hash_consts["0xD3A2646C"])))
    # for lane in range(VLEN):
        # instrs.append(("alu", ("+", tmps["1s"][phase][alu_group]+lane, tmps["vals"][phase][alu_group]+lane, hash_consts["0xD3A2646C"])))

    for i in range(num_valu_groups):
        instrs.append(("valu", ("<<", tmps["2s"][phase][i], tmps["vals"][phase][i], hash_consts["9"])))
    # for lane in range(VLEN):
        # instrs.append(("alu", ("<<", tmps["2s"][phase][alu_group]+lane, tmps["vals"][phase][alu_group]+lane, hash_consts["9"])))

    for i in range(num_valu_groups):
        instrs.append(("valu", ("^", tmps["vals"][phase][i], tmps["1s"][phase][i], tmps["2s"][phase][i])))
    # for lane in range(VLEN):
        # instrs.append(("alu", ("^", tmps["vals"][phase][alu_group]+lane, tmps["1s"][phase][alu_group]+lane, tmps["2s"][phase][alu_group]+lane)))

    # stage 5
    for i in range(num_valu_groups):
        instrs.append(("valu", ("+", tmps["1s"][phase][i], tmps["vals"][phase][i], hash_consts["0xFD7046C5"])))
    # for lane in range(VLEN):
        # instrs.append(("alu", ("+", tmps["1s"][phase][alu_group]+lane, tmps["vals"][phase][alu_group]+lane, hash_consts["0xFD7046C5"])))

    for i in range(num_valu_groups):
        instrs.append(("valu", ("multiply_add", tmps["vals"][phase][i], tmps["vals"][phase][i], hash_consts["8"], tmps["1s"][phase][i])))
    # for lane in range(VLEN):
        # instrs.append(("alu", ("*", tmps["vals"][phase][alu_group]+lane, tmps["vals"][phase][alu_group]+lane, hash_consts["8"])))
        # instrs.append(("alu", ("+", tmps["vals"][phase][alu_group]+lane, tmps["vals"][phase][alu_group]+lane, tmps["1s"][phase][alu_group]+lane)))

        # stage 6
    for i in range(num_valu_groups):
        instrs.append(("valu", ("^", tmps["1s"][phase][i], tmps["vals"][phase][i], hash_consts["0xB55A4F09"])))
    # for lane in range(VLEN):
        # instrs.append(("alu", ("^", tmps["1s"][phase][alu_group]+lane, tmps["vals"][phase][alu_group]+lane, hash_consts["0xB55A4F09"])))

    for i in range(num_valu_groups):
        instrs.append(("valu", (">>", tmps["2s"][phase][i], tmps["vals"][phase][i], hash_consts["16"])))
    # for lane in range(VLEN):
        # instrs.append(("alu", (">>", tmps["2s"][phase][alu_group]+lane, tmps["vals"][phase][alu_group]+lane, hash_consts["16"])))

    for i in range(num_valu_groups):
        instrs.append(("valu", ("^", tmps["vals"][phase][i], tmps["1s"][phase][i], tmps["2s"][phase][i])))
    # for lane in range(VLEN):
        # instrs.append(("alu", ("^", tmps["vals"][phase][alu_group]+lane, tmps["1s"][phase][alu_group]+lane, tmps["2s"][phase][alu_group]+lane)))

    # update index to next tree level or loop back up
    if round == forest_height:
        # idx = 0
        for i in range(num_valu_groups):
            instrs.append(("valu", ("*", tmps["addrs"][phase][i], hash_consts["forest_values"], hash_consts["1"])));
        # for lane in range(VLEN):
            # instrs.append(("alu", ("*", tmps["addrs"][phase][alu_group]+lane, hash_consts["forest_values"], hash_consts["1"])));
    else:

        # update idx to next level of tree going left or right based on parity
        # idx = 2*idx + 1 + val&1

        # if at root need to record the parity into b0 instead of val_paritys for later level 2 optimization (see gen_load_instrs_round_2)
        if round == 0 or round == 11:

            # b0 (parity) = val & 1
            for i in range(num_valu_groups):
                instrs.append(("valu", ("&", tmps["b0s"][phase][i], tmps["vals"][phase][i], hash_consts["1"])));
            # for lane in range(VLEN):
                # instrs.append(("alu", ("&", tmps["b0s"][phase][alu_group]+lane, tmps["vals"][phase][alu_group]+lane, hash_consts["1"])));

            # addr = addr*2 + 1 - forest_values_offset
            for i in range(num_valu_groups):
                instrs.append(("valu", ("multiply_add", tmps["addrs"][phase][i], tmps["addrs"][phase][i], hash_consts["2"], hash_consts["1_minus_fvo"])))
            # for lane in range(VLEN):
                # instrs.append(("alu", ("*", tmps["addrs"][phase][alu_group]+lane, tmps["addrs"][phase][alu_group]+lane, hash_consts["2"])))
                # instrs.append(("alu", ("+", tmps["addrs"][phase][alu_group]+lane, tmps["addrs"][phase][alu_group]+lane, hash_consts["1_minus_fvo"])))

            # addr += parity
            for i in range(num_valu_groups):
                instrs.append(("valu", ("+", tmps["addrs"][phase][i], tmps["addrs"][phase][i], tmps["b0s"][phase][i])))
            # for lane in range(VLEN):
                # instrs.append(("alu", ("+", tmps["addrs"][phase][alu_group]+lane, tmps["addrs"][phase][alu_group]+lane, tmps["b0s"][phase][alu_group]+lane)))

        else:

            # val_parity = vals & 1
            for i in range(num_valu_groups):
                instrs.append(("valu", ("&", tmps["val_paritys"][phase][i], tmps["vals"][phase][i], hash_consts["1"])));
            # for lane in range(VLEN):
                # instrs.append(("alu", ("&", tmps["val_paritys"][phase][alu_group]+lane, tmps["vals"][phase][alu_group]+lane, hash_consts["1"])));
                
            # addr = addr*2 + 1 - forest_value_offset
            for i in range(num_valu_groups):
                instrs.append(("valu", ("multiply_add", tmps["addrs"][phase][i], tmps["addrs"][phase][i], hash_consts["2"], hash_consts["1_minus_fvo"])))
            # for lane in range(VLEN):
                # instrs.append(("alu", ("*", tmps["addrs"][phase][alu_group]+lane, tmps["addrs"][phase][alu_group]+lane, hash_consts["2"])))
                # instrs.append(("alu", ("+", tmps["addrs"][phase][alu_group]+lane, tmps["addrs"][phase][alu_group]+lane, hash_consts["1_minus_fvo"])))

            # addr += val_parity
            for i in range(num_valu_groups):
                instrs.append(("valu", ("+", tmps["addrs"][phase][i], tmps["addrs"][phase][i], tmps["val_paritys"][phase][i])))
            # for lane in range(VLEN):
                # instrs.append(("alu", ("+", tmps["addrs"][phase][alu_group]+lane, tmps["addrs"][phase][alu_group]+lane, tmps["val_paritys"][phase][alu_group]+lane)))

    return instrs 

