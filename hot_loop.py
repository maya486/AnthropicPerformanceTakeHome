from index_calculation_instrs import gen_index_calculation_instrs_generic
from load_instrs import gen_load_instrs_generic
from hash_and_update_instrs import gen_hash_and_update_instrs_generic
from packer import pack, merge_independent_instr_streams

def gen_hot_loop_generic(round, phase, forest_height, forest_values, group_size, const_operands, tmps, consts):
    hash_and_update_instrs = gen_hash_and_update_instrs_generic((round-1)//2, (round-1)%2, forest_height, group_size, tmps, consts)
    index_instrs = gen_index_calculation_instrs_generic(round%2, group_size, consts, tmps)
    packed_valu_instrs = pack(index_instrs + hash_and_update_instrs, const_operands)

    packed_load_instrs = pack(gen_load_instrs_generic(round%2, group_size, tmps), const_operands)

    # the empty instr added before the loads is to make sure the first cycle executes some
    # index calculations and only after do the loads dependent on them start
    return merge_independent_instr_streams(packed_valu_instrs, [{"alu": [], "valu": [], "store": [], "load": []}] + packed_load_instrs)


