from problem import SLOT_LIMITS, Engine, VLEN


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

def squish(slots: list[tuple[Engine, tuple]], const_operands, verbose: bool = False):
    # simple slot packing that packs consecutive instructions together (no reordering)

    instrs = []
    # curr_instr = {
        # "alu": [],
        # "valu": [],
        # "load": [],
        # "store": [],
        # "flow": []
    # }
    # slot_counts = {
        # "alu": 0,
        # "valu": 0,
        # "load": 0,
        # "store": 0,
        # "flow": 0,
    # }
    # curr_read_operands = set()
    # curr_write_operands = set()

    for engine, slot in slots:
        placed_slot = False
        # last_valid_index =
        for i in range(len(instrs)-1, -1, -1):
            curr_read_operands = set()
            curr_write_operands = set()
            for e_name, e_slots in instrs[i].items():
                # print(e)

                # valu have to add 7 other implicit regs
                if e_name == "valu":
                    for s in e_slots:
                        # possible issue with valu ops not having lanes correctly handled in dependence tree analysis
                        curr_write_operands |= set([s[1]])
                        curr_read_operands |= set(s[2:])
                        for j in range(VLEN):
                            curr_write_operands |= set([s[1]+j])
                            for reg in s[2:]:
                                curr_read_operands |= set([reg+j])
                else:
                    for s in e_slots:
                        # possible issue with valu ops not having lanes correctly handled in dependence tree analysis
                        curr_write_operands |= set([s[1]])
                        curr_read_operands |= set(s[2:])

                            


            slot_counts = len(instrs[i][engine])
            # print("slot counts", slot_counts)
            # has_slot_space = slot_counts[engine] < SLOT_LIMITS[engine]
            has_slot_space = slot_counts < SLOT_LIMITS[engine]
            new_operands = set(slot[1:])
            new_write_operands = set([slot[1]])
            new_read_operands = set(slot[2:])

            operand_intersection = (new_write_operands & curr_write_operands) | (new_write_operands & curr_read_operands) | (new_read_operands & curr_write_operands)
            has_invalid_dependence = operand_intersection - set(const_operands)

            if not has_slot_space or has_invalid_dependence:
                # print(instrs)
                # print("adding", slot, "at index", i+1)
                # print("with slot_counts", slot_counts, "and limit", SLOT_LIMITS[engine])
                # instrs.append(curr_instr)
                # instrs.insert(i+1, curr_instr)
                if i == len(instrs)-1:
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
                    instrs[i+1][engine].append(slot)

                # curr_instr = {
                    # "alu": [],
                    # "valu": [],
                    # "load": [],
                    # "store": [],
                    # "flow": []
                # }
                # slot_counts["alu"] = 0
                # slot_counts["valu"] = 0
                # slot_counts["load"] = 0
                # slot_counts["store"] = 0
                # slot_counts["flow"] = 0
                curr_read_operands = set()
                curr_write_operands = set()


                placed_slot = True
                break


            # slot_counts[engine]+=1
            # curr_instr[engine].append(slot)
            # curr_read_operands.update(new_read_operands)
            # curr_write_operands.update(new_write_operands)
        # instrs.insert(0, curr_instr)
        # instrs[0][engine].append(slot)
        if not placed_slot:
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
            else:
                instrs[0][engine].append(slot)



    # if curr_instr["alu"] or curr_instr["valu"] or curr_instr["load"] or curr_instr["store"] or curr_instr["flow"]:
        # instrs.append(curr_instr)

    # if verbose:
        # # print(instrs)
        # for i in instrs:
            # print(i)
        
    return instrs
