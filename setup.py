from problem import VLEN
from group_partition import GROUPS, GROUP_VECS, NUM_GROUPS, CHUNK_SIZE, GROUPS_PREFIX_SUM

def setup_scratch(alloc_scratch, scratch_const, num_walkers):

    setup = []

    tmp1s = []
    b0s = []
    b1s = []
    tmp2s = []
    # for p in range(num_phases):
    for p in range(NUM_GROUPS):
        tmp1s.append([])
        tmp2s.append([])
        b0s.append([])
        b1s.append([])
        # for walker_group_idx in range(group_size//VLEN):
        for walker_group_idx in range(GROUP_VECS[p]):
            tmp1s[p].append(alloc_scratch(None, VLEN))
            tmp2s[p].append(alloc_scratch(None, VLEN))
            b0s[p].append(alloc_scratch(None, VLEN))
            b1s[p].append(alloc_scratch(None, VLEN))

    tmp3s = []
    for i in range(16):
        tmp3s.append(alloc_scratch(None, VLEN))


    # memory layout
    # 0: "rounds",
    # 1: "n_nodes",
    # 2: "num_walkers",
    # 3: "forest_height",
    # 4: "forest_values_p",
    # 5: "inp_indices_p",
    # 6: "inp_values_p",

    # Scratch space addresses
    init_vars = [
        "forest_values_p",
        "inp_indices_p",
        "inp_values_p",
    ]
    init_vars_scratch = []
    for v in init_vars:
        init_vars_scratch.append(alloc_scratch(v, 1))
    for i, v in enumerate(init_vars):
        setup.append(("load", ("const", tmp1s[0][0], i+4))) # +4 bc forest_values_p starts at memory location 4
        setup.append(("load", ("load", init_vars_scratch[i], tmp1s[0][0])))

    tmp_scalar_const_zero = scratch_const(setup, 0)


    forest_values = alloc_scratch(init_vars_scratch[0], VLEN)
    setup.append(("valu", ("vbroadcast", forest_values, init_vars_scratch[0])))

    # tmp_scalar_const_8 = scratch_const(setup, 8)
    tmp_scalar_const_8 = alloc_scratch()
    setup.append(("flow", ("add_imm", tmp_scalar_const_8, tmp_scalar_const_zero, 8)))

    const_v2 = alloc_scratch("v2", VLEN)
    const_v3 = alloc_scratch("v3", VLEN)
    const_v4 = alloc_scratch("v4", VLEN)
    const_v5 = alloc_scratch("v5", VLEN)
    const_v6 = alloc_scratch("v6", VLEN)
    const_v7 = alloc_scratch("v7", VLEN)
    const_v8 = alloc_scratch("v8", VLEN)
    const_v9 = alloc_scratch("v9", VLEN)
    const_v10 = alloc_scratch("v10", VLEN)
    const_v11 = alloc_scratch("v11", VLEN)
    const_v12 = alloc_scratch("v12", VLEN)
    const_v13 = alloc_scratch("v13", VLEN)
    const_v14 = alloc_scratch("v14", VLEN)
    const_v15 = alloc_scratch("v15", VLEN)

    setup.append(("load", ("vload", tmp1s[0][0], forest_values)))
    setup.append(("alu", ("+", tmp1s[0][1], init_vars_scratch[0], tmp_scalar_const_8)))
    setup.append(("load", ("vload", tmp1s[0][1], tmp1s[0][1])))
    setup.append(("valu", ("vbroadcast", const_v2, tmp1s[0][0]+1)))
    setup.append(("valu", ("vbroadcast", const_v3, tmp1s[0][0]+2)))
    setup.append(("valu", ("vbroadcast", const_v4, tmp1s[0][0]+3)))
    setup.append(("valu", ("vbroadcast", const_v5, tmp1s[0][0]+4)))
    setup.append(("valu", ("vbroadcast", const_v6, tmp1s[0][0]+5)))
    setup.append(("valu", ("vbroadcast", const_v7, tmp1s[0][0]+6)))
    setup.append(("valu", ("vbroadcast", const_v8, tmp1s[0][0]+7)))
    setup.append(("valu", ("vbroadcast", const_v9, tmp1s[0][1]+0)))
    setup.append(("valu", ("vbroadcast", const_v10, tmp1s[0][1]+1)))
    setup.append(("valu", ("vbroadcast", const_v11, tmp1s[0][1]+2)))
    setup.append(("valu", ("vbroadcast", const_v12, tmp1s[0][1]+3)))
    setup.append(("valu", ("vbroadcast", const_v13, tmp1s[0][1]+4)))
    setup.append(("valu", ("vbroadcast", const_v14, tmp1s[0][1]+5)))
    setup.append(("valu", ("vbroadcast", const_v15, tmp1s[0][1]+6)))



    walker_idxs = []
    for walker_idx in range(0, num_walkers, CHUNK_SIZE):
        walker_idx_idx = (int)(walker_idx/(CHUNK_SIZE))
        walker_idxs.append([])
        for p in range(NUM_GROUPS):
            walker_idxs[walker_idx_idx].append([])
            for i in range(GROUP_VECS[p]):
                walker_idxs[walker_idx_idx][p].append(alloc_scratch(None, 1))

                tmp = scratch_const(setup, GROUPS_PREFIX_SUM[p]+walker_idx+VLEN*i)

                # tmp = alloc_scratch()

                # setup.append(("flow", ("add_imm", tmp, tmp_scalar_const_zero, GROUPS_PREFIX_SUM[p]+walker_idx+VLEN*i)))

                # values
                setup.append(("alu", ("+", walker_idxs[walker_idx_idx][p][i], init_vars_scratch[2], tmp)))




    const_one = alloc_scratch(1, VLEN)
    const_two = alloc_scratch(2, VLEN)
    # const_three = alloc_scratch(3, VLEN)
    const_four = alloc_scratch(4, VLEN)
    # const_five = alloc_scratch(5, VLEN)
    const_seven = alloc_scratch(5, VLEN)
    const_nine = alloc_scratch(9, VLEN)
    const_eleven = alloc_scratch(11, VLEN)
    # const_twelve = alloc_scratch(12, VLEN)
    const_thirteen = alloc_scratch(13, VLEN)
    const_sixteen = alloc_scratch(16, VLEN)
    const_nineteen = alloc_scratch(19, VLEN)
    const_4096 = alloc_scratch(4096, VLEN)
    const_32 = alloc_scratch(32, VLEN)
    const_8 = alloc_scratch(8, VLEN)
    const_1_minus_fvo = alloc_scratch("1_minus_fvo", VLEN) # fvo = forest_value_offset
    const_root_addr_plus_7 = alloc_scratch("root_addr_plus_7", VLEN) # fvo = forest_value_offset
    const_inp_indices_minus_inp_values = alloc_scratch("inp_indices_minus_inp_values", VLEN) # fvo = forest_value_offset
    const_v3_minus_v2 = alloc_scratch("v3_minus_v2", VLEN) # fvo = forest_value_offset


    # tmp_scalar_const_one = scratch_const(setup, 1)
    tmp_scalar_const_one = alloc_scratch()
    setup.append(("flow", ("add_imm", tmp_scalar_const_one, tmp_scalar_const_zero, 1)))

    # tmp_scalar_const_two = scratch_const(setup, 2)
    tmp_scalar_const_two = alloc_scratch()
    setup.append(("flow", ("add_imm", tmp_scalar_const_two, tmp_scalar_const_zero, 2)))
    # tmp_scalar_const_three = scratch_const(setup, 3)
    # tmp_scalar_const_four = scratch_const(setup, 4)
    tmp_scalar_const_four = alloc_scratch()
    setup.append(("flow", ("add_imm", tmp_scalar_const_four, tmp_scalar_const_zero, 4)))
    # tmp_scalar_const_five = scratch_const(setup, 5)
    # tmp_scalar_const_seven = scratch_const(setup, 7)
    tmp_scalar_const_seven = alloc_scratch()
    setup.append(("flow", ("add_imm", tmp_scalar_const_seven, tmp_scalar_const_zero, 7)))
    # tmp_scalar_const_nine = scratch_const(setup, 9)
    tmp_scalar_const_nine = alloc_scratch()
    setup.append(("flow", ("add_imm", tmp_scalar_const_nine, tmp_scalar_const_zero, 9)))
    # tmp_scalar_const_eleven = scratch_const(setup, 11)
    tmp_scalar_const_eleven = alloc_scratch()
    setup.append(("flow", ("add_imm", tmp_scalar_const_eleven, tmp_scalar_const_zero, 11)))
    # tmp_scalar_const_twelve = scratch_const(setup, 12)
    # tmp_scalar_const_thirteen = scratch_const(setup, 13)
    tmp_scalar_const_thirteen = alloc_scratch()
    setup.append(("flow", ("add_imm", tmp_scalar_const_thirteen, tmp_scalar_const_zero, 13)))
    # tmp_scalar_const_sixteen = scratch_const(setup, 16)
    tmp_scalar_const_sixteen = alloc_scratch()
    setup.append(("flow", ("add_imm", tmp_scalar_const_sixteen, tmp_scalar_const_zero, 16)))
    # tmp_scalar_const_nineteen = scratch_const(setup, 19)
    tmp_scalar_const_nineteen = alloc_scratch()
    setup.append(("flow", ("add_imm", tmp_scalar_const_nineteen, tmp_scalar_const_zero, 19)))
    # tmp_scalar_const_4096 = scratch_const(setup, 4096)
    tmp_scalar_const_4096 = alloc_scratch()
    setup.append(("flow", ("add_imm", tmp_scalar_const_4096, tmp_scalar_const_zero, 4096)))
    # tmp_scalar_const_32 = scratch_const(setup, 32)
    tmp_scalar_const_32 = alloc_scratch()
    setup.append(("flow", ("add_imm", tmp_scalar_const_32, tmp_scalar_const_zero, 32)))



    setup.append(("valu", ("vbroadcast", const_one, tmp_scalar_const_one)))
    setup.append(("valu", ("vbroadcast", const_two, tmp_scalar_const_two)))
    # setup.append(("valu", ("vbroadcast", const_three, tmp_scalar_const_three)))
    setup.append(("valu", ("vbroadcast", const_four, tmp_scalar_const_four)))
    # setup.append(("valu", ("vbroadcast", const_five, tmp_scalar_const_five)))
    setup.append(("valu", ("vbroadcast", const_seven, tmp_scalar_const_seven)))
    setup.append(("valu", ("vbroadcast", const_nine, tmp_scalar_const_nine)))
    setup.append(("valu", ("vbroadcast", const_eleven, tmp_scalar_const_eleven)))
    # setup.append(("valu", ("vbroadcast", const_twelve, tmp_scalar_const_twelve)))
    setup.append(("valu", ("vbroadcast", const_thirteen, tmp_scalar_const_thirteen)))
    setup.append(("valu", ("vbroadcast", const_sixteen, tmp_scalar_const_sixteen)))
    setup.append(("valu", ("vbroadcast", const_nineteen, tmp_scalar_const_nineteen)))
    setup.append(("valu", ("vbroadcast", const_4096, tmp_scalar_const_4096)))
    setup.append(("valu", ("vbroadcast", const_32, tmp_scalar_const_32)))
    setup.append(("valu", ("vbroadcast", const_8, tmp_scalar_const_8)))



    tmp_vals = []
    tmp_node_vals = []
    tmp_addrs = []
    tmp_val_paritys = []
    # for p in range(num_phases):
    for p in range(NUM_GROUPS):
        tmp_vals.append([])
        tmp_node_vals.append([])
        tmp_addrs.append([])
        tmp_val_paritys.append([])
        # for walker_group_idx in range(group_size//VLEN):
        for walker_group_idx in range(GROUP_VECS[p]):
            tmp_vals[p].append(alloc_scratch(None, VLEN))
            tmp_node_vals[p].append(alloc_scratch(None, VLEN))
            tmp_addrs[p].append(alloc_scratch(None, VLEN))
            tmp_val_paritys[p].append(alloc_scratch(None, VLEN))

    tmp_0x7ED55D16 = alloc_scratch("tmp_0x7ED55D16", VLEN)
    tmp_0xC761C23C = alloc_scratch("tmp_0xC761C23C", VLEN)
    tmp_0x165667B1 = alloc_scratch("tmp_0x165667B1", VLEN)
    tmp_0xD3A2646C = alloc_scratch("tmp_0xD3A2646C", VLEN)
    tmp_0xFD7046C5 = alloc_scratch("tmp_0xFD7046C5", VLEN)
    tmp_0xB55A4F09 = alloc_scratch("tmp_0xB55A4F09", VLEN)

    # const_0x7ED55D16 = scratch_const(setup, 0x7ED55D16)
    const_0x7ED55D16 = alloc_scratch()
    setup.append(("flow", ("add_imm", const_0x7ED55D16, tmp_scalar_const_zero, 0x7ED55D16)))
    # const_0xC761C23C = scratch_const(setup, 0xC761C23C)
    const_0xC761C23C = alloc_scratch()
    setup.append(("flow", ("add_imm", const_0xC761C23C, tmp_scalar_const_zero, 0xC761C23C)))
    # const_0x165667B1 = scratch_const(setup, 0x165667B1)
    const_0x165667B1 = alloc_scratch()
    setup.append(("flow", ("add_imm", const_0x165667B1, tmp_scalar_const_zero, 0x165667B1)))
    # const_0xD3A2646C = scratch_const(setup, 0xD3A2646C)
    const_0xD3A2646C = alloc_scratch()
    setup.append(("flow", ("add_imm", const_0xD3A2646C, tmp_scalar_const_zero, 0xD3A2646C)))
    # const_0xFD7046C5 = scratch_const(setup, 0xFD7046C5)
    const_0xFD7046C5 = alloc_scratch()
    setup.append(("flow", ("add_imm", const_0xFD7046C5, tmp_scalar_const_zero, 0xFD7046C5)))
    # const_0xB55A4F09 = scratch_const(setup, 0xB55A4F09)
    const_0xB55A4F09 = alloc_scratch()
    setup.append(("flow", ("add_imm", const_0xB55A4F09, tmp_scalar_const_zero, 0xB55A4F09)))

    setup.append(("valu", ("vbroadcast", tmp_0x7ED55D16, const_0x7ED55D16)))
    setup.append(("valu", ("vbroadcast", tmp_0xC761C23C, const_0xC761C23C)))
    setup.append(("valu", ("vbroadcast", tmp_0x165667B1, const_0x165667B1)))
    setup.append(("valu", ("vbroadcast", tmp_0xD3A2646C, const_0xD3A2646C)))
    setup.append(("valu", ("vbroadcast", tmp_0xFD7046C5, const_0xFD7046C5)))
    setup.append(("valu", ("vbroadcast", tmp_0xB55A4F09, const_0xB55A4F09)))



    setup.append(("valu", ("-", const_1_minus_fvo, const_one, forest_values)))
    setup.append(("valu", ("+", const_root_addr_plus_7, const_seven, forest_values)))
    setup.append(("alu", ("-", const_inp_indices_minus_inp_values, init_vars_scratch[1], init_vars_scratch[2])))
    setup.append(("valu", ("-", const_v3_minus_v2, const_v3, const_v2)))


    consts = {
        "1": const_one,
        "2": const_two,
        "4": const_four,
        # "7": const_seven,
        "8": const_8,
        "9": const_nine,
        "11": const_eleven,
        "13": const_thirteen,
        "16": const_sixteen,
        "19": const_nineteen,
        "32": const_32,
        "4096": const_4096,
        "0x7ED55D16": tmp_0x7ED55D16,
        "0xC761C23C": tmp_0xC761C23C,
        "0x165667B1": tmp_0x165667B1,
        "0xD3A2646C": tmp_0xD3A2646C,
        "0xFD7046C5": tmp_0xFD7046C5,
        "0xB55A4F09": tmp_0xB55A4F09,
        "forest_values": forest_values,
        "inp_indices_p": init_vars_scratch[1],
        "inp_values_p": init_vars_scratch[2],
        "v2": const_v2, 
        "v3": const_v3, 
        "v4": const_v4, 
        "v5": const_v5, 
        "v6": const_v6, 
        "v7": const_v7, 
        "v8": const_v8, 
        "v9": const_v9, 
        "v10": const_v10, 
        "v11": const_v11, 
        "v12": const_v12, 
        "v13": const_v13, 
        "v14": const_v14, 
        "v15": const_v15, 
        "1_minus_fvo": const_1_minus_fvo, 
        "root_addr_plus_7": const_root_addr_plus_7,
        "inp_indices_minus_inp_values": const_inp_indices_minus_inp_values,
        "v3_minus_v2": const_v3_minus_v2,
        "walker_idxs": walker_idxs,
    }


    tmps = {
        "vals": tmp_vals,
        "node_vals": tmp_node_vals,
        "val_paritys": tmp_val_paritys,
        "addrs": tmp_addrs,
        "1s": tmp1s,
        "2s": tmp2s,
        "3s": tmp3s,
        "b0s": b0s,
        "b1s": b1s,
    }


    return setup, consts, tmps


