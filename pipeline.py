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

    next_group_offset = 5 + 2*rounds+2

    group_offsets = [0, next_group_offset]

    work_schedule = []

    for i in range(2*(h_offset+2*rounds+2)):
        work_schedule.append([(Work.NONE, -1, -1), 
                              (Work.NONE, -1, -1), 
                              (Work.NONE, -1, -1), 
                              (Work.NONE, -1, -1), 
                              (Work.NONE, -1, -1), 
                              (Work.NONE, -1, -1), 
                              (Work.NONE, -1, -1), 
                              (Work.NONE, -1, -1)])

    offsets = [a_offset, b_offset, c_offset, d_offset,
               e_offset, f_offset, g_offset, h_offset]

    for j in range(len(group_offsets)):
        for i in range(len(offsets)):

            offset = group_offsets[j]+offsets[i]

            work_schedule[offset+0][i] = (Work.READ_IN, -1, j)
            work_schedule[offset+2*rounds+1][i] = (Work.WRITE_OUT, -1, j)

            for r in range(rounds):
                work_schedule[offset+2*r+1][i] = (Work.LOAD, r, -1)
                work_schedule[offset+2*r+2][i] = (Work.HASH, r, -1)

    return work_schedule


def gen_iter(round, work_schedule, rounds, forest_height, forest_values, tmps, consts):

    instrs = []

    for i in range(NUM_GROUPS):

        work, work_round, group = work_schedule[round][i]
        if work == Work.LOAD:
            instrs += gen_load_instrs(work_round, i, round, GROUPS[i], consts, tmps)
        elif work == Work.HASH:
            instrs += gen_hash_and_update_instrs_generic(work_round, i, forest_height, GROUPS[i], tmps, consts)
        elif work == Work.READ_IN:
            instrs += gen_read_in_instrs(group, i, GROUPS[i], tmps, consts)
        elif work == Work.WRITE_OUT:
            instrs += gen_write_out_instrs(group, i, GROUPS[i], tmps, consts)

    return instrs

