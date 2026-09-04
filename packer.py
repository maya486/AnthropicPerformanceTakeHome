from problem import SLOT_LIMITS, Engine, VLEN


def process_instr(e_name, e_slots, curr_write_operands, curr_read_operands):
    for s in e_slots:
        if e_name == "alu":
            curr_write_operands |= set([s[1]])
            curr_read_operands |= set(s[2:])
        elif e_name == "valu":
            if s[0] == "vbroadcast":
                curr_read_operands |= set([s[2]])
                for j in range(VLEN):
                    curr_write_operands |= set([s[1]+j])
            elif s[0] == "multiply_add":
                for j in range(VLEN):
                    curr_write_operands |= set([s[1]+j])
                    for reg in s[2:]:
                        curr_read_operands |= set([reg+j])
            else: # * + - ^ etc
                for j in range(VLEN):
                    curr_write_operands |= set([s[1]+j])
                    for reg in s[2:]:
                        curr_read_operands |= set([reg+j])
        elif e_name == "load":
            if s[0] == "load":
                curr_write_operands |= set([s[1]])
                curr_read_operands |= set([s[2]])
            elif s[0] == "vload":
                curr_read_operands |= set([s[2]])
                for j in range(VLEN):
                    curr_write_operands |= set([s[1]+j])
            elif s[0] == "const":
                curr_write_operands |= set([s[1]])
        elif e_name == "store":
            if s[0] == "store":
                curr_read_operands |= set([s[1], s[2]])
            elif s[0] == "vstore":
                curr_read_operands |= set([s[1]])
                for j in range(VLEN):
                    curr_read_operands |= set([s[2]+j])
        elif e_name == "flow":
            if s[0] == "vselect":
                for j in range(VLEN):
                    curr_write_operands |= set([s[1]+j])
                    for reg in s[2:]:
                        curr_read_operands |= set([reg+j])
            elif s[0] == "add_imm":
                curr_write_operands |= set([s[1]])
                curr_read_operands |= set([s[2]])


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

            # data dependency issue stops backward iteration
            if operand_intersection:
                break

            # lack of slot space skips this slot but allows
            # further backward iteration 
            if not has_slot_space:
                continue

            earliest_insertion_idx = i

        insert_slot(slot, engine, earliest_insertion_idx, instrs)

    return instrs
