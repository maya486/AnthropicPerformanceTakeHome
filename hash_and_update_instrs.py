from problem import VLEN

def gen_hash_and_update_instrs_generic(round, phase, forest_height, group_size, tmps, hash_consts):
    instrs = []

    num_valu_groups = (group_size//VLEN)

    # vary to easily push one group from valu to alu though
    # sometimes split is more finegrained than that to 
    # achieve perfect balance between alu and valu
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

    for i in range(num_valu_groups):
        instrs.append(("valu", ("multiply_add", tmps["vals"][phase][i], tmps["vals"][phase][i], hash_consts["4096"], tmps["1s"][phase][i])))

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

    # stage 4
    for i in range(num_valu_groups-1):
        instrs.append(("valu", ("+", tmps["1s"][phase][i], tmps["vals"][phase][i], hash_consts["0xD3A2646C"])))
    for lane in range(VLEN):
        instrs.append(("alu", ("+", tmps["1s"][phase][alu_group]+lane, tmps["vals"][phase][alu_group]+lane, hash_consts["0xD3A2646C"])))


    # finegrained tuning of alu valu balance
    if (round in [6]) or (round == 5 and phase in [0, 1, 2, 3, 4, 5, 6]):
        for i in range(num_valu_groups-1):
            instrs.append(("valu", ("<<", tmps["2s"][phase][i], tmps["vals"][phase][i], hash_consts["9"])))
        for lane in range(VLEN):
            instrs.append(("alu", ("<<", tmps["2s"][phase][alu_group]+lane, tmps["vals"][phase][alu_group]+lane, hash_consts["9"])))
    else:
        for i in range(num_valu_groups):
            instrs.append(("valu", ("<<", tmps["2s"][phase][i], tmps["vals"][phase][i], hash_consts["9"])))

    for i in range(num_valu_groups):
        instrs.append(("valu", ("^", tmps["vals"][phase][i], tmps["1s"][phase][i], tmps["2s"][phase][i])))

    # stage 5
    for i in range(num_valu_groups):
        if phase == 0 and round in [6]:
            for lane in range(VLEN):
                instrs.append(("flow", ("add_imm", tmps["1s"][phase][i]+lane, tmps["vals"][phase][i]+lane, 0xFD7046C5)))
        else:
            instrs.append(("valu", ("+", tmps["1s"][phase][i], tmps["vals"][phase][i], hash_consts["0xFD7046C5"])))

    for i in range(num_valu_groups):
        instrs.append(("valu", ("multiply_add", tmps["vals"][phase][i], tmps["vals"][phase][i], hash_consts["8"], tmps["1s"][phase][i])))

    # stage 6
    for i in range(num_valu_groups):
        instrs.append(("valu", ("^", tmps["1s"][phase][i], tmps["vals"][phase][i], hash_consts["0xB55A4F09"])))

    for i in range(num_valu_groups):
        instrs.append(("valu", (">>", tmps["2s"][phase][i], tmps["vals"][phase][i], hash_consts["16"])))

    for i in range(num_valu_groups):
        instrs.append(("valu", ("^", tmps["vals"][phase][i], tmps["1s"][phase][i], tmps["2s"][phase][i])))

    # update index to next tree level or loop back up to root

    # loop back up to root
    if round == forest_height:
        for i in range(num_valu_groups):
            instrs.append(("valu", ("*", tmps["addrs"][phase][i], hash_consts["forest_values"], hash_consts["1"])));

    # update idx to next level of tree going left or right 
    # based on parity based on idx = 2*idx + 1 + val&1
    # for top tree levels where addr isn't used due to load
    # opts, don't have to update, only track parity
    # sometimes track parity in b0s or b1s instead of 
    # val_paritys for load opts

    elif round == 0 or round == 11:

        # b0 (parity) = val & 1
        for i in range(num_valu_groups):
            instrs.append(("valu", ("&", tmps["b0s"][phase][i], tmps["vals"][phase][i], hash_consts["1"])));

    elif round == 1 or round == 12:

        # b1 (parity) = val & 1
        for i in range(num_valu_groups):
            instrs.append(("valu", ("&", tmps["b1s"][phase][i], tmps["vals"][phase][i], hash_consts["1"])));

    elif round == 2 or round == 13:
        
        # val_parity = vals & 1
        for i in range(num_valu_groups):
            instrs.append(("valu", ("&", tmps["val_paritys"][phase][i], tmps["vals"][phase][i], hash_consts["1"])));

        # addr = root_addr + 7 + val_parity
        for i in range(num_valu_groups):
            instrs.append(("valu", ("+", tmps["addrs"][phase][i], hash_consts["root_addr_plus_7"], tmps["val_paritys"][phase][i])))

        # addr += b1*2
        for i in range(num_valu_groups):
            instrs.append(("valu", ("multiply_add", tmps["addrs"][phase][i], tmps["b1s"][phase][i], hash_consts["2"], tmps["addrs"][phase][i])))

        # addr += b0*4
        for i in range(num_valu_groups):
            instrs.append(("valu", ("multiply_add", tmps["addrs"][phase][i], tmps["b0s"][phase][i], hash_consts["4"], tmps["addrs"][phase][i])))

    else:

        # val_parity = vals & 1
        for i in range(num_valu_groups):
            instrs.append(("valu", ("&", tmps["val_paritys"][phase][i], tmps["vals"][phase][i], hash_consts["1"])));
            
        # addr = addr*2 + 1 - forest_value_offset
        for i in range(num_valu_groups):
            instrs.append(("valu", ("multiply_add", tmps["addrs"][phase][i], tmps["addrs"][phase][i], hash_consts["2"], hash_consts["1_minus_fvo"])))

        # addr += val_parity
        for i in range(num_valu_groups):
            instrs.append(("valu", ("+", tmps["addrs"][phase][i], tmps["addrs"][phase][i], tmps["val_paritys"][phase][i])))

    return instrs 

