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

from pipeline import gen_pipeline_iter, gen_pipeline_ramp_up, gen_pipeline_ramp_down, gen_work_schedule, gen_iter
from walker_group import gen_read_in_walker_group_instrs, gen_write_out_walker_group_instrs
from packer import pack
from setup import setup_scratch


class KernelBuilder:
    def __init__(self):
        self.instrs = []
        self.scratch = {}
        self.scratch_debug = {}
        self.scratch_ptr = 0
        self.const_map = {}

    def debug_info(self):
        return DebugInfo(scratch_map=self.scratch_debug)


    def add(self, instr_list, engine, slot):
        instr_list.append({engine: [slot]})

    def alloc_scratch(self, name=None, length=1):
        addr = self.scratch_ptr
        if name is not None:
            self.scratch[name] = addr
            self.scratch_debug[addr] = (name, length)
        self.scratch_ptr += length
        assert self.scratch_ptr <= SCRATCH_SIZE, "Out of scratch space"
        return addr

    def scratch_const(self, instr_list, val, name=None):
        if val not in self.const_map:
            addr = self.alloc_scratch(name)
            instr_list.append(("load", ("const", addr, val)))
            self.const_map[val] = addr
        return self.const_map[val]


    def build_kernel(
        self, forest_height: int, n_nodes: int, num_walkers: int, rounds: int
    ):
        """
        Like reference_kernel2 but building actual instructions.
        Scalar implementation using only scalar ALU and load/store.
        """

        instrs = []

        # number of walker processed at a time
        group_size = 32
        num_phases = 4
        pipeline_offset = 10

        setup, const_operands, consts, tmps = setup_scratch(self.alloc_scratch, self.scratch_const, num_walkers, group_size, num_phases)
        instrs.extend(setup)


        # fully process groups of walkers at a time
        # for walker_idx in range(0, num_walkers, 2*group_size):
        for walker_idx in range(0, num_walkers, num_phases*group_size):

            walker_idx_idx = (int)(walker_idx/(num_phases*group_size))

            # read in all walker group vals and idxs
            # instrs.extend(gen_read_in_walker_group_instrs(walker_idx_idx, num_phases, group_size, tmps, consts))


            # DO WORK
            work_schedule = gen_work_schedule(rounds, pipeline_offset)
            for round in range(len(work_schedule)):
                instrs.extend(gen_iter(round, work_schedule, walker_idx_idx, rounds, forest_height, consts["forest_values"], group_size, const_operands, tmps, consts))

            # # start pipeline
            # instrs.extend(gen_pipeline_ramp_up(group_size, consts, tmps))

            # # main body of pipeline
            # for round in range(1, 2*rounds):

                 # instrs.extend(gen_pipeline_iter(round, forest_height, consts["forest_values"], group_size, const_operands, tmps, consts))

            # # finish pipeline
            # instrs.extend(gen_pipeline_ramp_down(rounds, forest_height, group_size, consts, tmps))

            # write out all walker group vals and idxs
            # instrs.extend(gen_write_out_walker_group_instrs(walker_idx_idx, num_phases, group_size, tmps, consts))


        packed_instrs = pack(instrs, const_operands)

        # required to match with yields in reference_kernel2
        packed_instrs = [{"flow": [("pause",)]}] + packed_instrs + [{"flow": [("pause",)]}]

        self.instrs.extend(packed_instrs)

        # print(len(self.instrs))


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
