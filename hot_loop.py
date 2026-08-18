from index_calculation_instrs import gen_index_calculation_instrs_generic
from load_instrs import gen_load_instrs_generic, gen_load_instrs_round_0, gen_load_instrs_round_0_with_valu, gen_load_instrs_round_1
from hash_and_update_instrs import gen_hash_and_update_instrs_generic
from packer import pack, merge_independent_instr_streams, squish

printed_once = False

def gen_hot_loop(round, forest_height, forest_values, group_size, const_operands, tmps, consts):

    hash_round = (round-1)//2
    hash_phase = (round-1)%2
    index_load_round = round//2
    index_load_phase = round%2

    # at root
    if index_load_round == 0 or index_load_round == 11:
        # packed_load_instrs = pack(gen_load_instrs_round_0(index_load_phase, group_size, consts, tmps), const_operands)
        # packed_hash_and_update_instrs = pack(gen_hash_and_update_instrs_generic(hash_round, hash_phase, forest_height, group_size, tmps, consts), const_operands)
        packed_load_instrs = gen_load_instrs_round_0(index_load_phase, group_size, consts, tmps)
        packed_hash_and_update_instrs = gen_hash_and_update_instrs_generic(hash_round, hash_phase, forest_height, group_size, tmps, consts)
        return squish(packed_load_instrs+packed_hash_and_update_instrs, const_operands)

        # return merge_independent_instr_streams(packed_load_instrs, packed_hash_and_update_instrs)

    # at level below root, only 2 nodes
    elif index_load_round == 1 or index_load_round == 12:

        # packed_load_instrs = pack(gen_load_instrs_round_1(index_load_phase, group_size, consts, tmps), const_operands)
        # packed_hash_and_update_instrs = pack(gen_hash_and_update_instrs_generic(hash_round, hash_phase, forest_height, group_size, tmps, consts), const_operands)
        packed_load_instrs = gen_load_instrs_round_1(index_load_phase, group_size, consts, tmps)
        packed_hash_and_update_instrs = gen_hash_and_update_instrs_generic(hash_round, hash_phase, forest_height, group_size, tmps, consts)

        return squish(packed_load_instrs+packed_hash_and_update_instrs, const_operands)

        # return merge_independent_instr_streams(packed_load_instrs, packed_hash_and_update_instrs)


    else:
        return gen_hot_loop_generic(hash_round, hash_phase, index_load_phase, forest_height, forest_values, group_size, const_operands, tmps, consts)


def gen_hot_loop_generic(hash_round, hash_phase, index_load_phase, forest_height, forest_values, group_size, const_operands, tmps, consts):
    global printed_once

    # if hash_round == 15 and not printed_once:
    if True:
        hash_and_update_instrs = gen_hash_and_update_instrs_generic(hash_round, hash_phase, forest_height, group_size, tmps, consts)
        index_instrs = gen_index_calculation_instrs_generic(index_load_phase, group_size, consts, tmps)
        # packed_valu_instrs = index_instrs + hash_and_update_instrs, const_operands)

        load_instrs = gen_load_instrs_generic(index_load_phase, group_size, tmps)
        # printed_once = True
        return squish(index_instrs+load_instrs+hash_and_update_instrs, const_operands)

    # if hash_round < 15:
    # else:
        # hash_and_update_instrs = gen_hash_and_update_instrs_generic(hash_round, hash_phase, forest_height, group_size, tmps, consts)
        # index_instrs = gen_index_calculation_instrs_generic(index_load_phase, group_size, consts, tmps)
        # packed_valu_instrs = pack(index_instrs + hash_and_update_instrs, const_operands)

        # packed_load_instrs = pack(gen_load_instrs_generic(index_load_phase, group_size, tmps), const_operands)
        # # the empty instr added before the loads is to make sure the first cycle executes some
        # # index calculations and only after do the loads dependent on them start
        # return merge_independent_instr_streams(packed_valu_instrs, [{"alu": [], "valu": [], "store": [], "load": [], "flow": []}] + packed_load_instrs)



def gen_hot_loop_prologue(group_size, consts, tmps):
    return gen_load_instrs_round_0_with_valu(0, group_size, consts, tmps)

def gen_hot_loop_epilogue(rounds, forest_height, group_size, consts, tmps):
    return gen_hash_and_update_instrs_generic(31, 1, forest_height, group_size, tmps, consts)


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

Round 1 Shortcut:
    (alu) index: calculate index location for 2 nodes
    (load+alu) load: load 2 nodes into tmp1s[1] and [2]
        AND create a walker_node_idx = walker_idx+tmp1s[0]
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
