"""
# Anthropic's Original Performance Engineering Take-home (Release version)

Copyright Anthropic PBC 2026. Permission is granted to modify and use, but not
to publish or redistribute your solutions so it's hard to find spoilers.

# Task

- Optimize the kernel (in KernelBuilder.build_kernel) as much as possible in the
  available time, as measured by test_kernel_cycles on a frozen separate copy
  of the simulator.

Validate your results using `python tests/submission_tests.py` without modifying
anything in the tests/ folder.

We recommend you look through problem.py next.
"""

from collections import defaultdict
import random
import unittest

from problem import (
    Engine,
    DebugInfo,
    SLOT_LIMITS,
    VLEN,
    N_CORES,
    SCRATCH_SIZE,
    Machine,
    Tree,
    Input,
    HASH_STAGES,
    reference_kernel,
    build_mem_image,
    reference_kernel2,
)


class KernelBuilder:
    def __init__(self):
        self.instrs = []
        self.scratch = {}
        self.scratch_debug = {}
        self.scratch_ptr = 0
        self.const_map = {}

    def debug_info(self):
        return DebugInfo(scratch_map=self.scratch_debug)

    def build(self, slots: list[tuple[Engine, tuple]], vliw: bool = False):
        # Simple slot packing that just uses one slot per instruction bundle
        instrs = []
        for engine, slot in slots:
            instrs.append({engine: [slot]})
        return instrs

    def add(self, engine, slot):
        self.instrs.append({engine: [slot]})

    def alloc_scratch(self, name=None, length=1):
        addr = self.scratch_ptr
        if name is not None:
            self.scratch[name] = addr
            self.scratch_debug[addr] = (name, length)
        self.scratch_ptr += length
        assert self.scratch_ptr <= SCRATCH_SIZE, "Out of scratch space"
        return addr

    def scratch_const(self, val, name=None):
        if val not in self.const_map:
            addr = self.alloc_scratch(name)
            self.add("load", ("const", addr, val))
            self.const_map[val] = addr
        return self.const_map[val]

    def build_hash(self, val_hash_addr, tmp1, tmp2, round, i):
        slots = []

# HASH_STAGES = [
    # ("+", 0x7ED55D16, "+", "<<", 12),
    # ("^", 0xC761C23C, "^", ">>", 19),
    # ("+", 0x165667B1, "+", "<<", 5),
    # ("+", 0xD3A2646C, "^", "<<", 9),
    # ("+", 0xFD7046C5, "+", "<<", 3),
    # ("^", 0xB55A4F09, "^", ">>", 16),
# ]
        # for hi, (op1, val1, op2, op3, val3) in enumerate(HASH_STAGES):
            # slots.append(("alu", (op1, tmp1, val_hash_addr, self.scratch_const(val1))))
            # slots.append(("alu", (op3, tmp2, val_hash_addr, self.scratch_const(val3))))
            # slots.append(("alu", (op2, val_hash_addr, tmp1, tmp2)))
        slots.append(("alu", ("+", tmp1, val_hash_addr, tmp_0x7ED55D16)))
        slots.append(("alu", ("<<", tmp2, val_hash_addr, twelve_const)))
        slots.append(("alu", ("+", val_hash_addr, tmp1, tmp2)))

        slots.append(("alu", ("^", tmp1, val_hash_addr, tmp_0xC761C23C)))
        slots.append(("alu", (">>", tmp2, val_hash_addr, nineteen_const)))
        slots.append(("alu", ("^", val_hash_addr, tmp1, tmp2)))

        slots.append(("alu", ("+", tmp1, val_hash_addr, tmp_0x165667B1)))
        slots.append(("alu", ("<<", tmp2, val_hash_addr, five_const)))
        slots.append(("alu", ("+", val_hash_addr, tmp1, tmp2)))

        slots.append(("alu", ("+", tmp1, val_hash_addr, tmp_0xD3A2646C)))
        slots.append(("alu", ("<<", tmp2, val_hash_addr, nine_const)))
        slots.append(("alu", ("^", val_hash_addr, tmp1, tmp2)))

        slots.append(("alu", ("+", tmp1, val_hash_addr, tmp_0xFD7046C5)))
        slots.append(("alu", ("<<", tmp2, val_hash_addr, three_const)))
        slots.append(("alu", ("+", val_hash_addr, tmp1, tmp2)))

        slots.append(("alu", ("^", tmp1, val_hash_addr, tmp_0xB55A4F09)))
        slots.append(("alu", (">>", tmp2, val_hash_addr, sixteen_const)))
        slots.append(("alu", ("^", val_hash_addr, tmp1, tmp2)))

        return slots

    def build_kernel(
        self, forest_height: int, n_nodes: int, num_walkers: int, rounds: int
    ):
        """
        Like reference_kernel2 but building actual instructions.
        Scalar implementation using only scalar ALU and load/store.
        """


        # Pause instructions are matched up with yield statements in the reference
        # kernel to let you debug at intermediate steps. The testing harness in this
        # file requires these match up to the reference kernel's yields, but the
        # submission harness ignores them.
        self.add("flow", ("pause",))
        # Any debug engine instruction is ignored by the submission simulator

        body = []  # array of slots

        # Scalar scratch registers
        # tmp_idx = self.alloc_scratch("tmp_idx")
        # tmp_val = self.alloc_scratch("tmp_val")
        # tmp_node_val = self.alloc_scratch("tmp_node_val")
        # tmp_addr = self.alloc_scratch("tmp_addr")
        # tmp_val_parity = self.alloc_scratch("tmp_val_parity")

        # number of walker processed at a time
        group_size = 64

        tmp1s = []
        tmp2s = []
        tmp3s = []
        for walker_group_idx in range(group_size//VLEN):
            tmp1s.append(self.alloc_scratch(None, VLEN))
            tmp2s.append(self.alloc_scratch(None, VLEN))
            tmp3s.append(self.alloc_scratch(None, VLEN))

        # Scratch space addresses
        init_vars = [
            "rounds",
            "n_nodes",
            "num_walkers",
            "forest_height",
            "forest_values_p",
            "inp_indices_p",
            "inp_values_p",
        ]
        for v in init_vars:
            self.alloc_scratch(v, 1)
        for i, v in enumerate(init_vars):
            self.add("load", ("const", tmp1s[0], i))
            self.add("load", ("load", self.scratch[v], tmp1s[0]))

        const_zero = self.alloc_scratch(0, VLEN)
        const_one = self.alloc_scratch(1, VLEN)
        const_two = self.alloc_scratch(2, VLEN)
        const_three = self.alloc_scratch(3, VLEN)
        const_five = self.alloc_scratch(5, VLEN)
        const_nine = self.alloc_scratch(9, VLEN)
        const_twelve = self.alloc_scratch(12, VLEN)
        const_sixteen = self.alloc_scratch(16, VLEN)
        const_nineteen = self.alloc_scratch(19, VLEN)

        forest_values = self.alloc_scratch(self.scratch["forest_values_p"], VLEN)

        body.append(("valu", ("vbroadcast", const_zero, self.scratch_const(0))))
        body.append(("valu", ("vbroadcast", const_one, self.scratch_const(1))))
        body.append(("valu", ("vbroadcast", const_two, self.scratch_const(2))))
        body.append(("valu", ("vbroadcast", const_three, self.scratch_const(3))))
        body.append(("valu", ("vbroadcast", const_five, self.scratch_const(5))))
        body.append(("valu", ("vbroadcast", const_nine, self.scratch_const(9))))
        body.append(("valu", ("vbroadcast", const_twelve, self.scratch_const(12))))
        body.append(("valu", ("vbroadcast", const_sixteen, self.scratch_const(16))))
        body.append(("valu", ("vbroadcast", const_nineteen, self.scratch_const(19))))
        body.append(("valu", ("vbroadcast", forest_values, self.scratch["forest_values_p"])))

        tmp_idxs = []
        tmp_vals = []
        tmp_node_vals = []
        tmp_addrs = []
        tmp_val_paritys = []
        for walker_group_idx in range(group_size//VLEN):
            tmp_idxs.append(self.alloc_scratch(None, VLEN))
            tmp_vals.append(self.alloc_scratch(None, VLEN))
            tmp_node_vals.append(self.alloc_scratch(None, VLEN))
            tmp_addrs.append(self.alloc_scratch(None, VLEN))
            tmp_val_paritys.append(self.alloc_scratch(None, VLEN))

        tmp_0x7ED55D16 = self.alloc_scratch("tmp_0x7ED55D16", VLEN)
        tmp_0xC761C23C = self.alloc_scratch("tmp_0xC761C23C", VLEN)
        tmp_0x165667B1 = self.alloc_scratch("tmp_0x165667B1", VLEN)
        tmp_0xD3A2646C = self.alloc_scratch("tmp_0xD3A2646C", VLEN)
        tmp_0xFD7046C5 = self.alloc_scratch("tmp_0xFD7046C5", VLEN)
        tmp_0xB55A4F09 = self.alloc_scratch("tmp_0xB55A4F09", VLEN)

        const_0x7ED55D16 = self.scratch_const(0x7ED55D16)
        const_0xC761C23C = self.scratch_const(0xC761C23C)
        const_0x165667B1 = self.scratch_const(0x165667B1)
        const_0xD3A2646C = self.scratch_const(0xD3A2646C)
        const_0xFD7046C5 = self.scratch_const(0xFD7046C5)
        const_0xB55A4F09 = self.scratch_const(0xB55A4F09)

        body.append(("valu", ("vbroadcast", tmp_0x7ED55D16, const_0x7ED55D16)))
        body.append(("valu", ("vbroadcast", tmp_0xC761C23C, const_0xC761C23C)))
        body.append(("valu", ("vbroadcast", tmp_0x165667B1, const_0x165667B1)))
        body.append(("valu", ("vbroadcast", tmp_0xD3A2646C, const_0xD3A2646C)))
        body.append(("valu", ("vbroadcast", tmp_0xFD7046C5, const_0xFD7046C5)))
        body.append(("valu", ("vbroadcast", tmp_0xB55A4F09, const_0xB55A4F09)))

        for walker_idx in range(0, num_walkers, group_size):

            # load index for every walker in group_size
            # for i in range(walker_idx, walker_idx+group_size, VLEN):
            for i in range(group_size//VLEN):
                walker = self.scratch_const(walker_idx+VLEN*i)

                # idx = mem[inp_indices_p + i]
                body.append(("alu", ("+", tmp_addrs[i], self.scratch["inp_indices_p"], walker)))
                body.append(("load", ("vload", tmp_idxs[i], tmp_addrs[i])))
                # val = mem[inp_values_p + i]
                body.append(("alu", ("+", tmp_addrs[i], self.scratch["inp_values_p"], walker)))
                body.append(("load", ("vload", tmp_vals[i], tmp_addrs[i])))

            for round in range(rounds):
                for i in range(group_size//VLEN):
                # for i in range(walker_idx, walker_idx+group_size, VLEN):
                    # node_val = mem[forest_values_p + idx]
                    body.append(("valu", ("+", tmp_addrs[i], forest_values, tmp_idxs[i])))
                    for lane in range(VLEN):
                        body.append(("load", ("load", tmp_node_vals[i]+lane, tmp_addrs[i]+lane)))

                    # val = myhash(val ^ node_val)
                    body.append(("valu", ("^", tmp_vals[i], tmp_vals[i], tmp_node_vals[i])))

                    body.append(("valu", ("+", tmp1s[i], tmp_vals[i], tmp_0x7ED55D16)))
                    body.append(("valu", ("<<", tmp2s[i], tmp_vals[i], const_twelve)))
                    body.append(("valu", ("+", tmp_vals[i], tmp1s[i], tmp2s[i])))

                    body.append(("valu", ("^", tmp1s[i], tmp_vals[i], tmp_0xC761C23C)))
                    body.append(("valu", (">>", tmp2s[i], tmp_vals[i], const_nineteen)))
                    body.append(("valu", ("^", tmp_vals[i], tmp1s[i], tmp2s[i])))

                    body.append(("valu", ("+", tmp1s[i], tmp_vals[i], tmp_0x165667B1)))
                    body.append(("valu", ("<<", tmp2s[i], tmp_vals[i], const_five)))
                    body.append(("valu", ("+", tmp_vals[i], tmp1s[i], tmp2s[i])))

                    body.append(("valu", ("+", tmp1s[i], tmp_vals[i], tmp_0xD3A2646C)))
                    body.append(("valu", ("<<", tmp2s[i], tmp_vals[i], const_nine)))
                    body.append(("valu", ("^", tmp_vals[i], tmp1s[i], tmp2s[i])))

                    body.append(("valu", ("+", tmp1s[i], tmp_vals[i], tmp_0xFD7046C5)))
                    body.append(("valu", ("<<", tmp2s[i], tmp_vals[i], const_three)))
                    body.append(("valu", ("+", tmp_vals[i], tmp1s[i], tmp2s[i])))

                    body.append(("valu", ("^", tmp1s[i], tmp_vals[i], tmp_0xB55A4F09)))
                    body.append(("valu", (">>", tmp2s[i], tmp_vals[i], const_sixteen)))
                    body.append(("valu", ("^", tmp_vals[i], tmp1s[i], tmp2s[i])))

                    # update index to next tree level or loop back up
                    if round == forest_height:
                        # idx = 0
                        body.append(("valu", ("&", tmp_idxs[i], tmp_idxs[i], const_zero)));
                    else:
                        # idx = 2*idx + 1 + val&1
                        body.append(("valu", ("&", tmp_val_paritys[i], tmp_vals[i], const_one)));
                        body.append(("valu", ("*", tmp_idxs[i], tmp_idxs[i], const_two)))
                        body.append(("valu", ("+", tmp_idxs[i], tmp_idxs[i], const_one)))
                        body.append(("valu", ("+", tmp_idxs[i], tmp_idxs[i], tmp_val_paritys[i])))



            # for i in range(walker_idx, walker_idx+group_size, VLEN):
            for i in range(group_size//VLEN):
                walker = self.scratch_const(walker_idx+VLEN*i)

                # mem[inp_indices_p + i] = idx
                body.append(("alu", ("+", tmp_addrs[i], self.scratch["inp_indices_p"], walker)))
                body.append(("store", ("vstore", tmp_addrs[i], tmp_idxs[i])))
                # mem[inp_values_p + i] = val
                body.append(("alu", ("+", tmp_addrs[i], self.scratch["inp_values_p"], walker)))
                body.append(("store", ("vstore", tmp_addrs[i], tmp_vals[i])))

        body_instrs = self.build(body)
        self.instrs.extend(body_instrs)
        # Required to match with the yield in reference_kernel2
        self.instrs.append({"flow": [("pause",)]})

BASELINE = 147734

def do_kernel_test(
    forest_height: int,
    rounds: int,
    num_walkers: int,
    seed: int = 123,
    trace: bool = False,
    prints: bool = False,
):
    print(f"{forest_height=}, {rounds=}, {num_walkers=}")
    random.seed(seed)
    forest = Tree.generate(forest_height)
    inp = Input.generate(forest, num_walkers, rounds)
    mem = build_mem_image(forest, inp)

    kb = KernelBuilder()
    kb.build_kernel(forest.height, len(forest.values), len(inp.indices), rounds)
    # print(kb.instrs)

    value_trace = {}
    machine = Machine(
        mem,
        kb.instrs,
        kb.debug_info(),
        n_cores=N_CORES,
        value_trace=value_trace,
        trace=trace,
    )
    machine.prints = prints
    for i, ref_mem in enumerate(reference_kernel2(mem, value_trace)):
        machine.run()
        inp_values_p = ref_mem[6]
        if prints:
            print(machine.mem[inp_values_p : inp_values_p + len(inp.values)])
            print(ref_mem[inp_values_p : inp_values_p + len(inp.values)])
        assert (
            machine.mem[inp_values_p : inp_values_p + len(inp.values)]
            == ref_mem[inp_values_p : inp_values_p + len(inp.values)]
        ), f"Incorrect result on round {i}"
        inp_indices_p = ref_mem[5]
        if prints:
            print(machine.mem[inp_indices_p : inp_indices_p + len(inp.indices)])
            print(ref_mem[inp_indices_p : inp_indices_p + len(inp.indices)])
        # Updating these in memory isn't required, but you can enable this check for debugging
        # assert machine.mem[inp_indices_p:inp_indices_p+len(inp.indices)] == ref_mem[inp_indices_p:inp_indices_p+len(inp.indices)]

    print("CYCLES: ", machine.cycle)
    print("Speedup over baseline: ", BASELINE / machine.cycle)
    return machine.cycle


class Tests(unittest.TestCase):
    def test_ref_kernels(self):
        """
        Test the reference kernels against each other
        """
        random.seed(123)
        for i in range(10):
            f = Tree.generate(4)
            inp = Input.generate(f, 10, 6)
            mem = build_mem_image(f, inp)
            reference_kernel(f, inp)
            for _ in reference_kernel2(mem, {}):
                pass
            assert inp.indices == mem[mem[5] : mem[5] + len(inp.indices)]
            assert inp.values == mem[mem[6] : mem[6] + len(inp.values)]

    def test_kernel_trace(self):
        # Full-scale example for performance testing
        do_kernel_test(10, 16, 256, trace=True, prints=False)

    # Passing this test is not required for submission, see submission_tests.py for the actual correctness test
    # You can uncomment this if you think it might help you debug
    # def test_kernel_correctness(self):
    #     for batch in range(1, 3):
    #         for forest_height in range(3):
    #             do_kernel_test(
    #                 forest_height + 2, forest_height + 4, batch * 16 * VLEN * N_CORES
    #             )

    def test_kernel_cycles(self):
        do_kernel_test(10, 16, 256)


# To run all the tests:
#    python perf_takehome.py
# To run a specific test:
#    python perf_takehome.py Tests.test_kernel_cycles
# To view a hot-reloading trace of all the instructions:  **Recommended debug loop**
# NOTE: The trace hot-reloading only works in Chrome. In the worst case if things aren't working, drag trace.json onto https://ui.perfetto.dev/
#    python perf_takehome.py Tests.test_kernel_trace
# Then run `python watch_trace.py` in another tab, it'll open a browser tab, then click "Open Perfetto"
# You can then keep that open and re-run the test to see a new trace.

# To run the proper checks to see which thresholds you pass:
#    python tests/submission_tests.py

if __name__ == "__main__":
    unittest.main()
