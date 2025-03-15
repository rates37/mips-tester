import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from mips_tester import (
    configure,
    MipsState,
    test_assemble,
    test_run,
    test_final_state,
    MemorySize,
    create_harness,
    JumpType,
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
            self.temp_path / "valid_runtime_exception.asm"
        )
        valid_asm_runtime_exception_content = """
        .text
        .globl main
        main:
        la $t0, 0x00000000
        sw $t1, ($t0)
        """
        self.valid_asm_runtime_exception.write_text(
            valid_asm_runtime_exception_content)

        self.memory_test_asm = self.temp_path / "memory_test.asm"
        memory_test_content = """
        .text
        .globl main
        main:
        # Byte operations
        li $t0, 69
        la $t1, 0x10010000
        sb $t0, 0($t1)
        lb $t2, 0($t1)
        
        # Halfword operations
        li $t0, 420
        la $t1, 0x10010002
        sh $t0, 0($t1)
        lh $t3, 0($t1)
        
        # Word operations
        li $t0, 69420
        la $t1, 0x10010004
        sw $t0, 0($t1)
        lw $t4, 0($t1)
        """
        self.memory_test_asm.write_text(memory_test_content)

        self.byte_array_prog = self.temp_path / "byte_array_test.asm"
        byte_array_content = """
        .text
        .globl main
        main:
        la $t1, 0x10010010
        lb $s0, 0($t1)
        lb $s1, 1($t1)
        lb $s2, 2($t1)
        lb $s3, 3($t1)
        """
        self.byte_array_prog.write_text(byte_array_content)

        self.hw_array_prog = self.temp_path / "hw_array_test.asm"
        hw_array_content = """
        .text
        .globl main
        main:
        la $t1, 0x10010010
        lh $s0, 0($t1)
        lh $s1, 2($t1)
        """
        self.hw_array_prog.write_text(hw_array_content)

        self.w_array_prog = self.temp_path / "w_array_test.asm"
        w_array_content = """
        .text
        .globl main
        main:
        la $t1, 0x10010010
        lw $s0, 0($t1)
        """
        self.w_array_prog.write_text(w_array_content)

        self.return_value_asm = self.temp_path / "return_values.asm"
        return_value_content = """
        .text
        .globl main
        main:
        # Function that returns values in $v0 and $v1
        li $v0, 42
        li $v1, 84
        
        jr $ra
        """
        self.return_value_asm.write_text(return_value_content)

        self.custom_label_asm = self.temp_path / "custom_label.asm"
        self.custom_label_asm_name = "custom_entry"
        custom_label_content = f"""
        .text
        .globl {self.custom_label_asm_name}
        {self.custom_label_asm_name}:
        li $t0, 0xABCDEF
        li $t1, 0x123456
        
        li $v0, 10
        syscall
        """
        self.custom_label_asm.write_text(custom_label_content)

        # Create a MIPS program with the custom label
        self.custom_label_jal_asm_name = "my_custom_label"
        self.custom_label_jal_asm = self.temp_path / "custom_label_jal.asm"
        custom_label_jal_content = f"""
        .text
        .globl {self.custom_label_jal_asm_name}
        {self.custom_label_jal_asm_name}:
        # subroutine to add one to argument $a0 and return value in $v0
        addi $v0, $a0, 1
        jr $ra
        """
        self.custom_label_jal_asm.write_text(custom_label_jal_content)

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
        self.assertFalse(
            result.success, msg=f"Assembly unexpectedly succeeded.")

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
        result = test_run(str(self.valid_asm),
                          harness_name=str(self.valid_asm_harness))
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

    def test_run_runtime_exception(self):
        result = test_run(str(self.valid_asm_runtime_exception))
        self.assertFalse(
            result.success,
            msg=f"Run of program with runtime exception unexpectedly succeeded: {result.messages}",
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

    def test_final_state_memory_failure_legacy(self):
        expected_state = MipsState.from_dict(
            {"registers": {}, "memory": {"0x10010000": "0x10"}}
        )
        result = test_final_state(
            expected_state, str(self.valid_asm_harness), str(self.valid_asm)
        )
        self.assertTrue(
            result.success, msg=f"Final state check failed: {result.messages}."
        )
        self.assertLess(result.score, 1.0)

    def test_final_state_memory_failure(self):
        expected_state = MipsState(
            registers={}, memory={"0x10010000": {"value": "0xFF", "size": "word"}}
        )
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

    def test_final_state_memory_text_region_success_legacy(self):
        expected_state = MipsState.from_dict(
            {"registers": {}, "memory": {"0x400000": "0x0"}}
        )
        result = test_final_state(
            expected_state, str(self.valid_asm_harness), str(self.valid_asm)
        )
        self.assertTrue(
            result.success, msg=f"Final state check failed: {result.messages}."
        )
        self.assertLess(result.score, 1.0)

    def test_final_state_memory_text_region_success(self):
        expected_state = MipsState(registers={}, memory={
                                   "0x400000": {"value": "0x0"}})
        result = test_final_state(
            expected_state, str(self.valid_asm_harness), str(self.valid_asm)
        )
        self.assertTrue(
            result.success, msg=f"Final state check failed: {result.messages}."
        )
        self.assertLess(result.score, 1.0)

    def test_final_state_byte_memory(self):
        """Test checking final state with byte memory accesses."""

        initial_state = MipsState()
        harness_path = create_harness(
            initial_state,
            output_harness_name=self.temp_path / "byte_test_harness.asm",
        )

        expected_state = MipsState(
            registers={"t2": "69", "t3": "420", "t4": "69420"},
            memory={
                "0x10010000": {"value": "69", "size": MemorySize.BYTE},
                "0x10010002": {"value": "420", "size": MemorySize.HALFWORD},
                "0x10010004": {"value": "69420", "size": MemorySize.WORD}
            }
        )

        result = test_final_state(
            expected_state,
            str(harness_path),
            str(self.memory_test_asm)
        )

        self.assertTrue(result.success)
        self.assertAlmostEqual(result.score, 1.0)

    def test_memory_byte_array_extraction(self):
        """Test extracting individual bytes from a memory array."""

        initial_state = MipsState(
            memory={"0x10010010": {"value": "0x12345678", "size": MemorySize.WORD}}
        )
        harness_path = create_harness(
            initial_state,
            output_harness_name=self.temp_path / "byte_array_harness.asm",
        )

        expected_state = MipsState(
            registers={
                "s0": "0x78",
                "s1": "0x56",
                "s2": "0x34",
                "s3": "0x12",
            }
        )

        result = test_final_state(
            expected_state, str(harness_path), str(self.byte_array_prog)
        )

        self.assertTrue(result.success)
        self.assertAlmostEqual(result.score, 1.0)

    def test_memory_half_word_array_extraction(self):
        """Test extracting half words from a memory array."""

        initial_state = MipsState(
            memory={"0x10010010": {"value": "0x12345678", "size": MemorySize.WORD}}
        )
        harness_path = create_harness(
            initial_state,
            output_harness_name=self.temp_path / "hw_array_harness.asm",
        )

        expected_state = MipsState(
            registers={
                "s0": "0x5678",
                "s1": "0x1234",
            }
        )

        result = test_final_state(
            expected_state,
            str(harness_path),
            str(self.hw_array_prog),
        )

        self.assertTrue(result.success)
        self.assertAlmostEqual(result.score, 1.0)

    def test_memory_word_extraction(self):
        """Test extracting word from a memory array."""

        initial_state = MipsState(
            memory={"0x10010010": {"value": "0x12345678", "size": MemorySize.WORD}}
        )
        harness_path = create_harness(
            initial_state,
            output_harness_name=self.temp_path / "w_array_harness.asm",
        )

        expected_state = MipsState(
            registers={
                "s0": "0x12345678",
            }
        )

        result = test_final_state(
            expected_state,
            str(harness_path),
            str(self.w_array_prog),
        )

        self.assertTrue(result.success)
        self.assertAlmostEqual(result.score, 1.0)

    def test_harness_jump_types_jal(self):
        """Test harness with jump and link (jal)."""
        initial_state = MipsState(
            registers={"a0": "0x10", "a1": "0x20"}, memory={})

        harness_path = create_harness(
            initial_state,
            output_harness_name=self.temp_path / "jal_harness.asm",
            jump_type=JumpType.JUMP_AND_LINK,
        )

        expected_state = MipsState(
            registers={
                "v0": "42",
                "v1": "84",
            },
        )

        result = test_final_state(
            expected_state,
            harness_path,
            str(self.return_value_asm),
        )

        self.assertTrue(result.success)
        self.assertAlmostEqual(result.score, 1.0)

    def test_custom_label(self):
        """Test harness with custom entry label."""

        initial_state = MipsState(
            registers={"a0": "0x10", "a1": "0x20"},
            memory={}
        )

        harness_path = create_harness(
            initial_state,
            label=self.custom_label_asm_name,
            output_harness_name=self.temp_path / "custom_label_harness.asm",
        )

        expected_state = MipsState(
            registers={
                "a0": "0x10",
                "a1": "0x20",
                "t0": "0xABCDEF",
                "t1": "0x123456",
                "v0": "10"
            },
        )

        result = test_final_state(
            expected_state,
            str(harness_path),
            str(self.custom_label_asm)
        )

        self.assertTrue(result.success)
        self.assertAlmostEqual(result.score, 1.0)

    def test_jal_custom_label(self):
        """Test harness with subroutine to custom entry label."""

        initial_state = MipsState(
            registers={"a0": "0x10"}
        )

        harness_path = create_harness(
            initial_state,
            label=self.custom_label_jal_asm_name,
            output_harness_name=self.temp_path / "custom_label_harness.asm",
            jump_type=JumpType.JUMP_AND_LINK,
        )

        expected_state = MipsState(
            registers={
                "v0": "0x11"
            }
        )

        result = test_final_state(
            expected_state,
            str(harness_path),
            str(self.custom_label_jal_asm)
        )

        self.assertTrue(result.success)
        self.assertAlmostEqual(result.score, 1.0)


if __name__ == "__main__":
    unittest.main()
