from hash_and_update_instrs import gen_hash_and_update_instrs_generic
from load_instrs import gen_load_instrs_round_0_with_valu, gen_load_instrs_round_0, gen_load_instrs_round_1, gen_load_instrs_round_2, gen_load_instrs_generic, gen_load_instrs
from walker_group import gen_write_out_instrs, gen_read_in_instrs
from group_partition import GROUPS, GROUP_VECS, NUM_GROUPS

from enum import Enum


OFFSET_1 = 5
OFFSET_2 = 5
OFFSET_3 = 4


class Work(Enum):
    LOAD = 0
    HASH = 1
    READ_IN = 2
    WRITE_OUT = 3
    NONE = 4

def gen_work_schedule(rounds):

    a_offset = 0
    b_offset = a_offset+1
    c_offset = OFFSET_1
    d_offset = c_offset+1
    e_offset = OFFSET_1+OFFSET_2
    f_offset = e_offset+1
    g_offset = OFFSET_1+OFFSET_2+OFFSET_3
    h_offset = g_offset+1

    work_schedule = []

    for i in range(h_offset+2*rounds+2):
        work_schedule.append([(Work.NONE, -1), 
                              (Work.NONE, -1), 
                              (Work.NONE, -1), 
                              (Work.NONE, -1), 
                              (Work.NONE, -1), 
                              (Work.NONE, -1), 
                              (Work.NONE, -1), 
                              (Work.NONE, -1)])

    offsets = [a_offset, b_offset, c_offset, d_offset,
               e_offset, f_offset, g_offset, h_offset]

    for i in range(len(offsets)):

        work_schedule[offsets[i]+0][i] = (Work.READ_IN, -1)
        work_schedule[offsets[i]+2*rounds+1][i] = (Work.WRITE_OUT, -1)

        for r in range(rounds):
            work_schedule[offsets[i]+2*r+1][i] = (Work.LOAD, r)
            work_schedule[offsets[i]+2*r+2][i] = (Work.HASH, r)

    return work_schedule


def gen_iter(round, work_schedule, walker_idx_idx, rounds, forest_height, forest_values, const_operands, tmps, consts):

    instrs = []

    for i in range(NUM_GROUPS):

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

