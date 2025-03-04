import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from mips_tester import (
    configure,
    MipsState,
    test_assemble,
    test_run,
    test_final_state,
    TestResult,
)


class TestRunnerIntegration(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        # !  <---  MAY NEED TO MODIFY THIS LINE TO REFLECT YOUR mars.jar LOCATION  --->
        mars_jar_path = Path("./mars.jar")
        if not mars_jar_path.exists():
            self.skipTest(
                "mars.jar not found.  Place mars.jar in the same directory as this test."
            )

        configure(
            mars_path=str(mars_jar_path),
            max_steps=100,
            output_harness="test_harness.asm",
        )

        # Create dummy MIPS files for testing
        self.valid_asm = self.temp_path / "valid.asm"
        valid_asm_content = """
        .text
        .globl main
        main:
        addi $t0, $0, 5
        xor $t1, $t0, $s2
        li $v0, 10
        syscall
        """
        self.valid_asm.write_text(valid_asm_content)

        self.valid_asm_harness = self.temp_path / "valid_harness.asm"
        valid_asm_harness = """
        .text
        subi $t0, $0, 5
        li $v0, 69
        j main
        """
        self.valid_asm_harness.write_text(valid_asm_harness)

        self.invalid_asm = self.temp_path / "invalid.asm"
        self.invalid_asm.write_text("invalid instruction")

        self.invalid_asm_harness = self.temp_path / "invalid_harness.asm"
        invalid_asm_harness = """
        hi this is 
        invalid
        """
        self.invalid_asm_harness.write_text(invalid_asm_harness)

        self.valid_asm_runtime_exception = (
            self.temp_path / "valid_runtime_execution.asm"
        )
        valid_asm_runtime_exception_content = """
        .text
        .globl main
        main:
        la $t0, 0x00000000
        sw $t1, ($t0)
        """
        self.valid_asm_runtime_exception.write_text(valid_asm_runtime_exception_content)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_assemble_success(self):
        result = test_assemble(str(self.valid_asm))
        self.assertTrue(
            result.success, msg=f"Assembly of valid program failed: {result.messages}"
        )

    def test_assemble_success_harness(self):
        result = test_assemble(
            str(self.valid_asm), harness_name=str(self.valid_asm_harness)
        )
        self.assertTrue(
            result.success,
            msg=f"Assembly of valid program with valid harness failed: {result.messages}",
        )

    def test_assemble_failure(self):
        result = test_assemble(str(self.invalid_asm))
        self.assertFalse(result.success, msg=f"Assembly unexpectedly succeeded.")

    def test_assemble_failure_invalid_harness(self):
        result = test_assemble(
            str(self.valid_asm), harness_name=str(self.invalid_asm_harness)
        )
        self.assertFalse(
            result.success,
            msg=f"Assembly of valid program with invalid harness unexpectedly succeeded: {result.messages}",
        )

    def test_assemble_failure_valid_harness(self):
        result = test_assemble(
            str(self.invalid_asm), harness_name=str(self.valid_asm_harness)
        )
        self.assertFalse(
            result.success,
            msg=f"Assembly of invalid program with valid harness unexpectedly succeeded: {result.messages}",
        )

    def test_run_success(self):
        result = test_run(str(self.valid_asm))
        self.assertTrue(
            result.success, msg=f"Run of valid program failed: {result.messages}"
        )

    def test_run_success_harness(self):
        result = test_run(str(self.valid_asm), harness_name=str(self.valid_asm_harness))
        self.assertTrue(
            result.success,
            msg=f"Run of valid program with valid harness failed: {result.messages}",
        )

    def test_run_failure(self):
        result = test_run(str(self.invalid_asm))
        self.assertFalse(
            result.success, msg=f"Run of invalid program unexpectedly succeeded."
        )

    def test_run_failure_invalid_harness(self):
        result = test_run(
            str(self.valid_asm), harness_name=str(self.invalid_asm_harness)
        )
        self.assertFalse(
            result.success,
            msg=f"Run of valid program with invalid harness unexpectedly succeeded: {result.messages}",
        )

    def test_run_failure_valid_harness(self):
        result = test_run(
            str(self.invalid_asm), harness_name=str(self.valid_asm_harness)
        )
        self.assertFalse(
            result.success,
            msg=f"Run of invalid program with valid harness unexpectedly succeeded: {result.messages}",
        )

    def test_run_runtime_execution(self):
        result = test_run(str(self.valid_asm_runtime_exception))
        self.assertFalse(
            result.success,
            msg=f"Run of program with runtime execution unexpectedly succeeded: {result.messages}",
        )

    def test_final_state_register_success(self):
        expected_state = MipsState(registers={"t0": "0x5"}, memory={})
        result = test_final_state(
            expected_state, str(self.valid_asm_harness), str(self.valid_asm)
        )
        self.assertTrue(
            result.success, msg=f"Final state check failed: {result.messages}"
        )
        self.assertAlmostEqual(result.score, 1.0)

    def test_final_state_register_failure(self):
        expected_state = MipsState(registers={"t0": "0x10"}, memory={})
        result = test_final_state(
            expected_state, str(self.valid_asm_harness), str(self.valid_asm)
        )
        self.assertTrue(
            result.success, msg=f"Final state check failed: {result.messages}."
        )
        self.assertLess(result.score, 1.0)

    def test_final_state_memory_failure(self):
        expected_state = MipsState(registers={}, memory={"0x10010000": "0x10"})
        result = test_final_state(
            expected_state, str(self.valid_asm_harness), str(self.valid_asm)
        )
        self.assertTrue(
            result.success, msg=f"Final state check failed: {result.messages}."
        )
        self.assertLess(result.score, 1.0)

    def test_final_state_partial_success(self):
        # Test with both correct and incorrect values to check partial success
        expected_state = MipsState(
            registers={"t0": "0x5", "t1": "0x10"}, memory={}
        )  # t0 correct, t1 incorrect
        result = test_final_state(
            expected_state, str(self.valid_asm_harness), str(self.valid_asm)
        )
        self.assertTrue(
            result.success, msg=f"Final state check failed: {result.messages}"
        )
        self.assertGreater(result.score, 0.0)
        self.assertLess(result.score, 1.0)
        self.assertAlmostEqual(result.score, 0.5)

    def test_final_state_assembly_failure(self):
        expected_state = MipsState(registers={"t0": "0x5"}, memory={})
        result = test_final_state(
            expected_state, str(self.valid_asm_harness), str(self.invalid_asm)
        )
        self.assertFalse(result.success)
        self.assertEqual(result.score, 0.0)
        self.assertIn("did not assemble correctly", result.messages[0])

    def test_final_state_run_failure(self):
        expected_state = MipsState(registers={"t0": "0x5"}, memory={})
        result = test_final_state(
            expected_state,
            str(self.valid_asm_harness),
            str(self.valid_asm_runtime_exception),
        )
        self.assertFalse(result.success)
        self.assertEqual(result.score, 0.0)
        self.assertIn("did not run correctly", result.messages[0])

    def test_final_state_empty_expected_state(self):
        # Test with empty expected state.  Should pass with a score of 1.0
        expected_state = MipsState(registers={}, memory={})
        result = test_final_state(
            expected_state, str(self.valid_asm_harness), str(self.valid_asm)
        )
        self.assertTrue(
            result.success, msg=f"Final state check failed: {result.messages}"
        )
        self.assertAlmostEqual(result.score, 1.0)


if __name__ == "__main__":
    unittest.main()
