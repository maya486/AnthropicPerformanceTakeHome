from index_calculation_instrs import gen_index_calculation_instrs_generic
from load_instrs import gen_load_instrs_generic, gen_load_instrs_round_0
from hash_and_update_instrs import gen_hash_and_update_instrs_generic
from packer import pack, merge_independent_instr_streams

def gen_hot_loop_generic(round, forest_height, forest_values, group_size, const_operands, tmps, consts):
    hash_and_update_instrs = gen_hash_and_update_instrs_generic((round-1)//2, (round-1)%2, forest_height, group_size, tmps, consts)
    index_instrs = gen_index_calculation_instrs_generic(round%2, group_size, consts, tmps)
    packed_valu_instrs = pack(index_instrs + hash_and_update_instrs, const_operands)

    packed_load_instrs = pack(gen_load_instrs_generic(round%2, group_size, tmps), const_operands)

    # the empty instr added before the loads is to make sure the first cycle executes some
    # index calculations and only after do the loads dependent on them start
    return merge_independent_instr_streams(packed_valu_instrs, [{"alu": [], "valu": [], "store": [], "load": []}] + packed_load_instrs)


def gen_hot_loop_prologue(group_size, consts, tmps):
    return gen_load_instrs_round_0(0, group_size, consts, tmps)


"""
Original Implementation:
    (valu) index: calculate all group_size index locations with idx+forest_values_p
    (load) load: load all group_size addrs with mem[addr]
    (valu) hash: for each of the group_size loaded vals do hash and move idx to next tree level

Original Packing:
    valu: index_i + hash_i+1
    load: [nop] + load_i

Original Packing Strategy:
    Pack index and hash together on the valu and then merge in loads with
    a prepended nop.

Round 0 Shortcut:
    (alu) index: calculate index location for single root
    (load+alu) load: load single root val
        AND add with zero to sudo vbroadcast to whole group_size
    (valu) hash: for each of the group_size loaded vals do hash and move idx to next tree level

New Packing:
    if valu hash:
        do original packing
    else:
        alu: index_i + load_i
        valu: hash_i+1
        load: [wait] + load_i

New Packing Strategy:
    if valu hash:
        do original packing
    else:
        pack index and load together then merge in hash



Notes:
    add [wait] count as return value from index (generic has this as 1)
"""
