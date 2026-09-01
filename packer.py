from problem import SLOT_LIMITS, Engine, VLEN


def update_rw_operands_with_slot_vector(s, curr_write_operands, curr_read_operands):
    # vector operations have registers updated that aren't
    # explicity listed in the slot operands. Only the register
    # corresponding to lane 0 is listed, lanes 1-7 must be 
    # accounted for too, though, to not break data dependencies
    for j in range(VLEN):
        curr_write_operands |= set([s[1]+j])
        for reg in s[2:]:
            curr_read_operands |= set([reg+j])


def update_rw_operands_with_slot(s, curr_write_operands, curr_read_operands):
    curr_write_operands |= set([s[1]])
    curr_read_operands |= set(s[2:])


def process_instr(e_name, e_slots, curr_write_operands, curr_read_operands):
    if e_name == "valu":
        for s in e_slots:
            update_rw_operands_with_slot_vector(s, curr_write_operands, curr_read_operands)
    else:
        for s in e_slots:
            if s[0] in ["vload", "vstore", "vselect"]:
                update_rw_operands_with_slot_vector(s, curr_write_operands, curr_read_operands)
            else:
                update_rw_operands_with_slot(s, curr_write_operands, curr_read_operands)


def insert_slot(slot, engine, idx, instrs):

    if len(instrs) == 0:
        curr_instr = {
            "alu": [],
            "valu": [],
            "load": [],
            "store": [],
            "flow": []
        }
        curr_instr[engine].append(slot)
        instrs.append(curr_instr)
    elif idx == len(instrs):
        curr_instr = {
            "alu": [],
            "valu": [],
            "load": [],
            "store": [],
            "flow": []
        }
        curr_instr[engine].append(slot)
        instrs.append(curr_instr)
    else:
        instrs[idx][engine].append(slot)


def pack(slots: list[tuple[Engine, tuple]]):
    # packs slots by inserting each slot into the earliest instruction that doesn't violate data dependencies
    # slots of different engines may be reordered, but slots of the same
    # engine aren't

    instrs = []

    for engine, slot in slots:
        earliest_insertion_idx = len(instrs)

        # iterate backward through instr list to find earliest place for slot
        for i in range(len(instrs)-1, -1, -1):

            # determine whether slot has any data dependency conflicts with current instruction
            curr_write_operands = set()
            curr_read_operands = set()
            for e_name, e_slots in instrs[i].items():
                process_instr(e_name, e_slots, curr_write_operands, curr_read_operands)

            new_write_operands = set()
            new_read_operands = set()
            process_instr(engine, [slot], new_write_operands, new_read_operands)

            operand_intersection = (new_write_operands & curr_write_operands) | (new_write_operands & curr_read_operands) | (new_read_operands & curr_write_operands)

            # determine whether instruction has room for slot
            slot_counts = len(instrs[i][engine])
            has_slot_space = slot_counts < SLOT_LIMITS[engine]

            if operand_intersection:
                break

            if not has_slot_space:
                continue

            earliest_insertion_idx = i

        insert_slot(slot, engine, earliest_insertion_idx, instrs)

    return instrs
