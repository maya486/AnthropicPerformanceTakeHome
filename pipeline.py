from hash_and_update_instrs import gen_hash_and_update_instrs_generic
from load_instrs import gen_load_instrs_round_0_with_valu, gen_load_instrs_round_0, gen_load_instrs_round_1, gen_load_instrs_round_2, gen_load_instrs_generic


def gen_pipeline_iter(round, forest_height, forest_values, group_size, const_operands, tmps, consts):

    hash_round = (round-1)//2
    hash_phase = (round-1)%2
    index_load_round = round//2
    index_load_phase = round%2

    # shortcut when at level 0 of tree (root)
    if index_load_round == 0 or index_load_round == 11:
        
        packed_load_instrs = gen_load_instrs_round_0(index_load_phase, group_size, consts, tmps)
        packed_hash_and_update_instrs = gen_hash_and_update_instrs_generic(hash_round, hash_phase, forest_height, group_size, tmps, consts)

        return packed_load_instrs+packed_hash_and_update_instrs

    # shortcut when at level 1 of tree (2 nodes)
    elif index_load_round == 1 or index_load_round == 12:

        packed_load_instrs = gen_load_instrs_round_1(index_load_phase, group_size, consts, tmps)
        packed_hash_and_update_instrs = gen_hash_and_update_instrs_generic(hash_round, hash_phase, forest_height, group_size, tmps, consts)

        return packed_load_instrs+packed_hash_and_update_instrs

    # shortcut when at level 2 of tree (4 nodes)
    elif index_load_round == 2 or index_load_round == 13:

        packed_load_instrs = gen_load_instrs_round_2(index_load_phase, group_size, consts, tmps)
        packed_hash_and_update_instrs = gen_hash_and_update_instrs_generic(hash_round, hash_phase, forest_height, group_size, tmps, consts)

        return packed_load_instrs+packed_hash_and_update_instrs

    # generic fallback with no shortcuts
    else:
        return gen_pipeline_iter_generic(hash_round, hash_phase, index_load_phase, forest_height, forest_values, group_size, const_operands, tmps, consts)


def gen_pipeline_iter_generic(hash_round, hash_phase, index_load_phase, forest_height, forest_values, group_size, const_operands, tmps, consts):

    hash_and_update_instrs = gen_hash_and_update_instrs_generic(hash_round, hash_phase, forest_height, group_size, tmps, consts)
    load_instrs = gen_load_instrs_generic(index_load_phase, group_size, tmps)

    return load_instrs+hash_and_update_instrs


def gen_pipeline_ramp_up(group_size, consts, tmps):
    return gen_load_instrs_round_0_with_valu(0, group_size, consts, tmps)


def gen_pipeline_ramp_down(rounds, forest_height, group_size, consts, tmps):
    return gen_hash_and_update_instrs_generic(31, 1, forest_height, group_size, tmps, consts)

