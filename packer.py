from problem import SLOT_LIMITS, Engine


def merge_independent_instr_streams(list_a, list_b):
    instrs = []
    for i in range(min(len(list_a), len(list_b))):
        curr_instr = {
            "alu": [],
            "valu": [],
            "load": [],
            "store": [],
            "flow": []
        }
        curr_instr["alu"].extend(list_a[i]["alu"])
        curr_instr["alu"].extend(list_b[i]["alu"])
        curr_instr["valu"].extend(list_a[i]["valu"])
        curr_instr["valu"].extend(list_b[i]["valu"])
        curr_instr["load"].extend(list_a[i]["load"])
        curr_instr["load"].extend(list_b[i]["load"])
        curr_instr["store"].extend(list_a[i]["store"])
        curr_instr["store"].extend(list_b[i]["store"])
        curr_instr["flow"].extend(list_a[i]["flow"])
        curr_instr["flow"].extend(list_b[i]["flow"])
        instrs.append(curr_instr)
    if len(list_a) < len(list_b):
        instrs.extend(list_b[len(list_a):])
    elif len(list_b) < len(list_a):
        instrs.extend(list_a[len(list_b):])
    return instrs


def pack(slots: list[tuple[Engine, tuple]], const_operands, vliw: bool = False):
    # simple slot packing that packs consecutive instructions together (no reordering)

    instrs = []
    curr_instr = {
        "alu": [],
        "valu": [],
        "load": [],
        "store": [],
        "flow": []
    }
    slot_counts = {
        "alu": 0,
        "valu": 0,
        "load": 0,
        "store": 0,
        "flow": 0,
    }
    curr_read_operands = set()
    curr_write_operands = set()

    for engine, slot in slots:
        has_slot_space = slot_counts[engine] < SLOT_LIMITS[engine]
        new_operands = set(slot[1:])
        new_write_operands = set([slot[1]])
        new_read_operands = set(slot[2:])

        operand_intersection = (new_write_operands & curr_write_operands) | (new_write_operands & curr_read_operands) | (new_read_operands & curr_write_operands)
        has_invalid_dependence = operand_intersection - set(const_operands)

        if not has_slot_space or has_invalid_dependence:
            instrs.append(curr_instr)

            curr_instr = {
                "alu": [],
                "valu": [],
                "load": [],
                "store": [],
                "flow": []
            }
            slot_counts["alu"] = 0
            slot_counts["valu"] = 0
            slot_counts["load"] = 0
            slot_counts["store"] = 0
            slot_counts["flow"] = 0
            curr_read_operands = set()
            curr_write_operands = set()

        slot_counts[engine]+=1
        curr_instr[engine].append(slot)
        curr_read_operands.update(new_read_operands)
        curr_write_operands.update(new_write_operands)


    if curr_instr["alu"] or curr_instr["valu"] or curr_instr["load"] or curr_instr["store"] or curr_instr["flow"]:
        instrs.append(curr_instr)

    return instrs
