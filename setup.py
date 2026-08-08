from problem import VLEN

def setup_scratch(alloc_scratch, scratch_const, num_walkers, group_size, num_phases):

    setup = []

    tmp1s = []
    tmp2s = []
    tmp3s = []
    for p in range(num_phases):
        tmp1s.append([])
        tmp2s.append([])
        tmp3s.append([])
        for walker_group_idx in range(group_size//VLEN):
            tmp1s[p].append(alloc_scratch(None, VLEN))
            tmp2s[p].append(alloc_scratch(None, VLEN))
            tmp3s[p].append(alloc_scratch(None, VLEN))

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
        setup.append(("load", ("const", tmp1s[0][i], i+4))) # +4 bc forest_values_p starts at memory location 4
    for i, v in enumerate(init_vars):
        setup.append(("load", ("load", init_vars_scratch[i], tmp1s[0][i])))

    const_zero = alloc_scratch(0, VLEN)
    const_one = alloc_scratch(1, VLEN)
    const_two = alloc_scratch(2, VLEN)
    const_three = alloc_scratch(3, VLEN)
    const_five = alloc_scratch(5, VLEN)
    const_nine = alloc_scratch(9, VLEN)
    const_twelve = alloc_scratch(12, VLEN)
    const_sixteen = alloc_scratch(16, VLEN)
    const_nineteen = alloc_scratch(19, VLEN)
    const_4096 = alloc_scratch(4096, VLEN)
    const_32 = alloc_scratch(32, VLEN)
    const_8 = alloc_scratch(8, VLEN)
    const_512 = alloc_scratch(512, VLEN)

    tmp_scalar_const_zero = scratch_const(setup, 0)
    tmp_scalar_const_one = scratch_const(setup, 1)
    tmp_scalar_const_two = scratch_const(setup, 2)
    tmp_scalar_const_three = scratch_const(setup, 3)
    tmp_scalar_const_five = scratch_const(setup, 5)
    tmp_scalar_const_nine = scratch_const(setup, 9)
    tmp_scalar_const_twelve = scratch_const(setup, 12)
    tmp_scalar_const_sixteen = scratch_const(setup, 16)
    tmp_scalar_const_nineteen = scratch_const(setup, 19)
    tmp_scalar_const_4096 = scratch_const(setup, 4096)
    tmp_scalar_const_32 = scratch_const(setup, 32)
    tmp_scalar_const_8 = scratch_const(setup, 8)
    tmp_scalar_const_512 = scratch_const(setup, 512)

    forest_values = alloc_scratch(init_vars_scratch[0], VLEN)

    setup.append(("valu", ("vbroadcast", const_zero, tmp_scalar_const_zero)))
    setup.append(("valu", ("vbroadcast", const_one, tmp_scalar_const_one)))
    setup.append(("valu", ("vbroadcast", const_two, tmp_scalar_const_two)))
    setup.append(("valu", ("vbroadcast", const_three, tmp_scalar_const_three)))
    setup.append(("valu", ("vbroadcast", const_five, tmp_scalar_const_five)))
    setup.append(("valu", ("vbroadcast", const_nine, tmp_scalar_const_nine)))
    setup.append(("valu", ("vbroadcast", const_twelve, tmp_scalar_const_twelve)))
    setup.append(("valu", ("vbroadcast", const_sixteen, tmp_scalar_const_sixteen)))
    setup.append(("valu", ("vbroadcast", const_nineteen, tmp_scalar_const_nineteen)))
    setup.append(("valu", ("vbroadcast", const_4096, tmp_scalar_const_4096)))
    setup.append(("valu", ("vbroadcast", const_32, tmp_scalar_const_32)))
    setup.append(("valu", ("vbroadcast", const_8, tmp_scalar_const_8)))
    setup.append(("valu", ("vbroadcast", const_512, tmp_scalar_const_512)))
    setup.append(("valu", ("vbroadcast", forest_values, init_vars_scratch[0])))

    tmp_idxs = []
    tmp_vals = []
    tmp_node_vals = []
    tmp_addrs = []
    tmp_val_paritys = []
    for p in range(num_phases):
        tmp_idxs.append([])
        tmp_vals.append([])
        tmp_node_vals.append([])
        tmp_addrs.append([])
        tmp_val_paritys.append([])
        for walker_group_idx in range(group_size//VLEN):
            tmp_idxs[p].append(alloc_scratch(None, VLEN))
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

    const_0x7ED55D16 = scratch_const(setup, 0x7ED55D16)
    const_0xC761C23C = scratch_const(setup, 0xC761C23C)
    const_0x165667B1 = scratch_const(setup, 0x165667B1)
    const_0xD3A2646C = scratch_const(setup, 0xD3A2646C)
    const_0xFD7046C5 = scratch_const(setup, 0xFD7046C5)
    const_0xB55A4F09 = scratch_const(setup, 0xB55A4F09)

    setup.append(("valu", ("vbroadcast", tmp_0x7ED55D16, const_0x7ED55D16)))
    setup.append(("valu", ("vbroadcast", tmp_0xC761C23C, const_0xC761C23C)))
    setup.append(("valu", ("vbroadcast", tmp_0x165667B1, const_0x165667B1)))
    setup.append(("valu", ("vbroadcast", tmp_0xD3A2646C, const_0xD3A2646C)))
    setup.append(("valu", ("vbroadcast", tmp_0xFD7046C5, const_0xFD7046C5)))
    setup.append(("valu", ("vbroadcast", tmp_0xB55A4F09, const_0xB55A4F09)))

    walker_idxs = []
    for walker_idx in range(0, num_walkers, 2*group_size):
        walker_idx_idx = (int)(walker_idx/(2*group_size))
        walker_idxs.append([])
        for phase in range(num_phases):
            walker_idxs[walker_idx_idx].append([])
            for i in range(group_size//VLEN):
                walker_idxs[walker_idx_idx][phase].append(scratch_const(setup, group_size*phase+walker_idx+VLEN*i))

    consts = {
        "0": const_zero,
        "1": const_one,
        "2": const_two,
        "8": const_8,
        "9": const_nine,
        "16": const_sixteen,
        "19": const_nineteen,
        "32": const_32,
        "512": const_512,
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
    }

    const_operands = list(consts.values())

    consts["walker_idxs"] = walker_idxs

    tmps = {
        "vals": tmp_vals,
        "node_vals": tmp_node_vals,
        "val_paritys": tmp_val_paritys,
        "addrs": tmp_addrs,
        "idxs": tmp_idxs,
        "1s": tmp1s,
        "2s": tmp2s,
    }


    return setup, const_operands, consts, tmps


