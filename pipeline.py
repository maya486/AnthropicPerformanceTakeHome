from hash_and_update_instrs import gen_hash_and_update_instrs_generic
from load_instrs import gen_load_instrs_round_0_with_valu, gen_load_instrs_round_0, gen_load_instrs_round_1, gen_load_instrs_round_2, gen_load_instrs_generic, gen_load_instrs
from walker_group import gen_write_out_instrs, gen_read_in_instrs
from group_partition import GROUPS, GROUP_VECS, NUM_GROUPS

from enum import Enum


OFFSET_1 = 7
OFFSET_2 = 4
OFFSET_3 = 4


class Work(Enum):
    LOAD = 0
    HASH = 1
    READ_IN = 2
    WRITE_OUT = 3
    NONE = 4

def gen_work_schedule(rounds):

    # total_num_iters = rounds*2+OFFSET_1+3
    total_num_iters = 200
    work_schedule = []

    for i in range(total_num_iters):
        work_schedule.append([(Work.NONE, -1), 
                              (Work.NONE, -1), 
                              (Work.NONE, -1), 
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
        work_schedule[OFFSET_1][2] = (Work.READ_IN, -1)
        work_schedule[2*r+1+OFFSET_1][2] = (Work.LOAD, r)
        work_schedule[2*r+2+OFFSET_1][2] = (Work.HASH, r)
        work_schedule[2*rounds+1+OFFSET_1][2] = (Work.WRITE_OUT, -1)

        # schedule in group D
        work_schedule[1+OFFSET_1][3] = (Work.READ_IN, -1)
        work_schedule[2*r+2+OFFSET_1][3] = (Work.LOAD, r)
        work_schedule[2*r+3+OFFSET_1][3] = (Work.HASH, r)
        work_schedule[2*rounds+2+OFFSET_1][3] = (Work.WRITE_OUT, -1)

        # schedule in group E
        work_schedule[OFFSET_2+OFFSET_1][4] = (Work.READ_IN, -1)
        work_schedule[OFFSET_2+2*r+1+OFFSET_1][4] = (Work.LOAD, r)
        work_schedule[OFFSET_2+2*r+2+OFFSET_1][4] = (Work.HASH, r)
        work_schedule[OFFSET_2+2*rounds+1+OFFSET_1][4] = (Work.WRITE_OUT, -1)

        # schedule in group F
        work_schedule[OFFSET_2+1+OFFSET_1][5] = (Work.READ_IN, -1)
        work_schedule[OFFSET_2+2*r+2+OFFSET_1][5] = (Work.LOAD, r)
        work_schedule[OFFSET_2+2*r+3+OFFSET_1][5] = (Work.HASH, r)
        work_schedule[OFFSET_2+2*rounds+2+OFFSET_1][5] = (Work.WRITE_OUT, -1)

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

