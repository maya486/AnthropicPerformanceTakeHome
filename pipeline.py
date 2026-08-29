from hash_and_update_instrs import gen_hash_and_update_instrs_generic
from load_instrs import gen_load_instrs_round_0_with_valu, gen_load_instrs_round_0, gen_load_instrs_round_1, gen_load_instrs_round_2, gen_load_instrs_generic, gen_load_instrs
from walker_group import gen_write_out_instrs, gen_read_in_instrs
from group_partition import GROUPS, GROUP_VECS, NUM_GROUPS

from enum import Enum


class Work(Enum):
    LOAD = 0
    HASH = 1
    READ_IN = 2
    WRITE_OUT = 3
    NONE = 4

# class Group(Enum):
    # A = 0
    # B = 1
    # C = 2
    # D = 3
    # E = 4
    # F = 5

def gen_work_schedule(rounds, pipeline_offset, pipeline_offset_2):

    # total_num_iters = rounds*2+pipeline_offset+3
    total_num_iters = 200
    work_schedule = []

    for i in range(total_num_iters):
        work_schedule.append([(Work.NONE, -1), 
                              (Work.NONE, -1), 
                              (Work.NONE, -1), 
                              (Work.NONE, -1), 
                              (Work.NONE, -1), 
                              (Work.NONE, -1)])

    for r in range(rounds):

        # schedule in group A
        work_schedule[0][0] = (Work.READ_IN, -1)
        work_schedule[2*r+1][0] = (Work.LOAD, r)
        work_schedule[2*r+2][0] = (Work.HASH, r)
        work_schedule[2*rounds+1][0] = (Work.WRITE_OUT, -1)

        # schedule in group B
        work_schedule[1][1] = (Work.READ_IN, -1)
        work_schedule[2*r+2][1] = (Work.LOAD, r)
        work_schedule[2*r+3][1] = (Work.HASH, r)
        work_schedule[2*rounds+2][1] = (Work.WRITE_OUT, -1)

        # schedule in group C
        work_schedule[pipeline_offset][2] = (Work.READ_IN, -1)
        work_schedule[2*r+1+pipeline_offset][2] = (Work.LOAD, r)
        work_schedule[2*r+2+pipeline_offset][2] = (Work.HASH, r)
        work_schedule[2*rounds+1+pipeline_offset][2] = (Work.WRITE_OUT, -1)

        # schedule in group D
        work_schedule[1+pipeline_offset][3] = (Work.READ_IN, -1)
        work_schedule[2*r+2+pipeline_offset][3] = (Work.LOAD, r)
        work_schedule[2*r+3+pipeline_offset][3] = (Work.HASH, r)
        work_schedule[2*rounds+2+pipeline_offset][3] = (Work.WRITE_OUT, -1)

        # schedule in group E
        work_schedule[pipeline_offset_2+pipeline_offset][4] = (Work.READ_IN, -1)
        work_schedule[pipeline_offset_2+2*r+1+pipeline_offset][4] = (Work.LOAD, r)
        work_schedule[pipeline_offset_2+2*r+2+pipeline_offset][4] = (Work.HASH, r)
        work_schedule[pipeline_offset_2+2*rounds+1+pipeline_offset][4] = (Work.WRITE_OUT, -1)

        # schedule in group F
        work_schedule[pipeline_offset_2+1+pipeline_offset][5] = (Work.READ_IN, -1)
        work_schedule[pipeline_offset_2+2*r+2+pipeline_offset][5] = (Work.LOAD, r)
        work_schedule[pipeline_offset_2+2*r+3+pipeline_offset][5] = (Work.HASH, r)
        work_schedule[pipeline_offset_2+2*rounds+2+pipeline_offset][5] = (Work.WRITE_OUT, -1)

    return work_schedule


def gen_iter(round, work_schedule, walker_idx_idx, rounds, forest_height, forest_values, const_operands, tmps, consts):

    instrs = []

    for i in range(6): # [A, B, C, D, E, F] aka phase

        work, work_round = work_schedule[round][i]
        if work == Work.LOAD:
            instrs += gen_load_instrs(work_round, i, round, GROUPS[i], consts, tmps)
        elif work == Work.HASH:
            instrs += gen_hash_and_update_instrs_generic(work_round, i, forest_height, GROUPS[i], tmps, consts)
        elif work == Work.READ_IN:
            instrs += gen_read_in_instrs(walker_idx_idx, i, GROUPS[i], tmps, consts)
        elif work == Work.WRITE_OUT:
            instrs += gen_write_out_instrs(walker_idx_idx, i, GROUPS[i], tmps, consts)

    return instrs

    


# def gen_pipeline_iter(round, forest_height, forest_values, group_size, const_operands, tmps, consts):

    # hash_round = (round-1)//2
    # hash_phase = (round-1)%2
    # index_load_round = round//2
    # index_load_phase = round%2

    # # shortcut when at level 0 of tree (root)
    # if index_load_round == 0 or index_load_round == 11:
        
        # packed_load_instrs = gen_load_instrs_round_0(index_load_phase, group_size, consts, tmps)
        # packed_hash_and_update_instrs = gen_hash_and_update_instrs_generic(hash_round, hash_phase, forest_height, group_size, tmps, consts)

        # return packed_load_instrs+packed_hash_and_update_instrs

    # # shortcut when at level 1 of tree (2 nodes)
    # elif index_load_round == 1 or index_load_round == 12:

        # packed_load_instrs = gen_load_instrs_round_1(index_load_phase, group_size, consts, tmps)
        # packed_hash_and_update_instrs = gen_hash_and_update_instrs_generic(hash_round, hash_phase, forest_height, group_size, tmps, consts)

        # return packed_load_instrs+packed_hash_and_update_instrs

    # # shortcut when at level 2 of tree (4 nodes)
    # elif index_load_round == 2 or index_load_round == 13:

        # packed_load_instrs = gen_load_instrs_round_2(index_load_phase, group_size, consts, tmps)
        # packed_hash_and_update_instrs = gen_hash_and_update_instrs_generic(hash_round, hash_phase, forest_height, group_size, tmps, consts)

        # return packed_load_instrs+packed_hash_and_update_instrs

    # # generic fallback with no shortcuts
    # else:
        # return gen_pipeline_iter_generic(hash_round, hash_phase, index_load_phase, forest_height, forest_values, group_size, const_operands, tmps, consts)


# def gen_pipeline_iter_generic(hash_round, hash_phase, index_load_phase, forest_height, forest_values, group_size, const_operands, tmps, consts):

    # hash_and_update_instrs = gen_hash_and_update_instrs_generic(hash_round, hash_phase, forest_height, group_size, tmps, consts)
    # load_instrs = gen_load_instrs_generic(index_load_phase, group_size, tmps)

    # return load_instrs+hash_and_update_instrs


# def gen_pipeline_ramp_up(group_size, consts, tmps):
    # return gen_load_instrs_round_0_with_valu(0, group_size, consts, tmps)


# def gen_pipeline_ramp_down(rounds, forest_height, group_size, consts, tmps):
    # return gen_hash_and_update_instrs_generic(31, 1, forest_height, group_size, tmps, consts)

