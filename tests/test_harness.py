import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from mips_tester import create_harness, MipsState, JumpType, configure, MemorySize

"""
Todo: in setup, download mars if specified path does not exist
"""


class TestHarness(unittest.TestCase):
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
            mars_path=mars_jar_path,
            max_steps=1000,
            output_harness="test_harness.asm",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_create_harness_basic(self):
        initial_state = MipsState.from_dict(
            {
                "registers": {"a0": "10", "v0": "20"},
                "memory": {"1000": "30", "1004": "40"},
            }
        )
        harness_path = create_harness(
            initial_state,
            output_harness_name=self.temp_path / "test_harness.asm",
        )
        self.assertTrue(harness_path.exists())
        with open(harness_path, "r") as f:
            content = f.read()
            self.assertIn("li $a0, 10", content)
            self.assertIn("li $v0, 20", content)
            self.assertIn("li $t0, 30", content)
            self.assertIn("sw $t0, ($t1)", content)
            self.assertIn("j main", content)

    def test_create_harness_file_with_dict(self):
        initial_state = {
            "registers": {"a0": "10", "v0": "20"},
            "memory": {"1000": "30", "1004": "40"},
        }
        harness_path = create_harness(
            initial_state,
            output_harness_name=self.temp_path / "test_harness.asm",
        )
        self.assertTrue(harness_path.exists())
        with open(harness_path, "r") as f:
            content = f.read()
            self.assertIn("li $a0, 10", content)
            self.assertIn("li $v0, 20", content)
            self.assertIn("li $t0, 30", content)
            self.assertIn("sw $t0, ($t1)", content)
            self.assertIn("j main", content)

    def test_create_harness_with_custom_label(self):
        initial_state = MipsState.from_dict(
            {
                "registers": {"a0": "10", "v0": "20"},
                "memory": {"1000": "30", "1004": "40"},
            }
        )
        harness_path = create_harness(
            initial_state,
            label="start",
            output_harness_name=self.temp_path / "test_harness.asm",
        )
        self.assertTrue(harness_path.exists())
        with open(harness_path, "r") as f:
            content = f.read()
            self.assertIn("li $a0, 10", content)
            self.assertIn("li $v0, 20", content)
            self.assertIn("li $t0, 30", content)
            self.assertIn("sw $t0, ($t1)", content)
            self.assertIn("j start", content)

    def test_create_harness_jal(self):
        initial_state = MipsState.from_dict(
            {
                "registers": {"a0": "10", "v0": "20"},
                "memory": {"1000": "30", "1004": "40"},
            }
        )
        # test 1 with default label:
        harness_path = create_harness(
            initial_state,
            output_harness_name=self.temp_path / "test_harness.asm",
            jump_type=JumpType.JUMP_AND_LINK,
        )
        self.assertTrue(harness_path.exists())
        with open(harness_path, "r") as f:
            content = f.read()
            self.assertIn("li $a0, 10", content)
            self.assertIn("li $v0, 20", content)
            self.assertIn("li $t0, 30", content)
            self.assertIn("sw $t0, ($t1)", content)
            self.assertIn("jal main", content)

        # test 2 with custom label:
        harness_path = create_harness(
            initial_state,
            label="start",
            output_harness_name=self.temp_path / "test_harness.asm",
            jump_type=JumpType.JUMP_AND_LINK,
        )
        self.assertTrue(harness_path.exists())
        with open(harness_path, "r") as f:
            content = f.read()
            self.assertIn("li $a0, 10", content)
            self.assertIn("li $v0, 20", content)
            self.assertIn("li $t0, 30", content)
            self.assertIn("sw $t0, ($t1)", content)
            self.assertIn("jal start", content)

    def test_create_harness_empty_state(self):
        initial_state = MipsState()
        # test 1 with default label:
        harness_path = create_harness(
            initial_state,
            output_harness_name=self.temp_path / "test_harness.asm",
        )
        self.assertTrue(harness_path.exists())
        with open(harness_path, "r") as f:
            content = f.read()
            self.assertIn("j main", content)

        # test 2 with custom label:
        harness_path = create_harness(
            initial_state,
            label="start",
            output_harness_name=self.temp_path / "test_harness.asm",
        )
        self.assertTrue(harness_path.exists())
        with open(harness_path, "r") as f:
            content = f.read()
            self.assertIn("j start", content)

    def test_create_harness_hex_values(self):
        initial_state = MipsState.from_dict(
            {
                "registers": {"a0": "0x10", "v0": "0x20"},
                "memory": {"0x1000": "0x30", "0x1004": "0x40"},
            }
        )
        # test 1: default label
        harness_path = create_harness(
            initial_state,
            output_harness_name=self.temp_path / "test_harness.asm",
        )
        self.assertTrue(harness_path.exists())
        with open(harness_path, "r") as f:
            content = f.read()
            self.assertIn("li $a0, 0x10", content)
            self.assertIn("li $v0, 0x20", content)
            self.assertIn("li $t0, 0x30", content)
            self.assertIn("sw $t0, ($t1)", content)
            self.assertIn("j main", content)

        # test 2: custom label
        harness_path = create_harness(
            initial_state,
            label="start",
            output_harness_name=self.temp_path / "test_harness.asm",
        )
        self.assertTrue(harness_path.exists())
        with open(harness_path, "r") as f:
            content = f.read()
            self.assertIn("li $a0, 0x10", content)
            self.assertIn("li $v0, 0x20", content)
            self.assertIn("li $t0, 0x30", content)
            self.assertIn("sw $t0, ($t1)", content)
            self.assertIn("j start", content)

    def test_create_harness_invalid_label(self):
        # test with a label that contains spaces
        initial_state = MipsState(registers={"a0": "10"})
        with self.assertRaises(ValueError):
            create_harness(
                initial_state,
                label="invalid label",
                output_harness_name=self.temp_path / "test_harness.asm",
            )

    def test_create_harness_with_byte_memory(self):
        """Test creating a harness with byte memory access."""
        initial_state = MipsState(
            memory={"0x10010000": {"value": "0xAB", "size": MemorySize.BYTE}}
        )
        harness_path = create_harness(
            initial_state,
            output_harness_name=self.temp_path / "byte_harness.asm",
        )

        # Verify harness content
        with open(harness_path, "r") as f:
            content = f.read()
            self.assertIn("li $t0, 0xAB", content)
            self.assertIn("la $t1, 0x10010000", content)
            self.assertIn("sb $t0, ($t1)", content)

    def test_create_harness_with_halfword_memory(self):
        """Test creating a harness with halfword memory access."""
        initial_state = MipsState(
            memory={"0x10010002": {"value": "0xABCD", "size": MemorySize.HALFWORD}}
        )
        harness_path = create_harness(
            initial_state,
            output_harness_name=self.temp_path / "halfword_harness.asm",
        )

        # Verify harness content
        with open(harness_path, "r") as f:
            content = f.read()
            self.assertIn("li $t0, 0xABCD", content)
            self.assertIn("la $t1, 0x10010002", content)
            self.assertIn("sh $t0, ($t1)", content)

    def test_create_harness_with_word_memory(self):
        """Test creating a harness with word memory access."""
        initial_state = MipsState(
            memory={"0x10010004": {"value": "0xABCD1234", "size": MemorySize.WORD}}
        )
        harness_path = create_harness(
            initial_state,
            output_harness_name=self.temp_path / "word_harness.asm",
        )

        # Verify harness content
        with open(harness_path, "r") as f:
            content = f.read()
            self.assertIn("li $t0, 0xABCD1234", content)
            self.assertIn("la $t1, 0x10010004", content)
            self.assertIn("sw $t0, ($t1)", content)

    def test_mixed_memory_types_harness(self):
        """Test creating a harness with mixed memory type accesses."""
        initial_state = MipsState(
            memory={
                "0x10010000": {"value": "0xAB", "size": MemorySize.BYTE},
                "0x10010002": {"value": "0xCDEF", "size": MemorySize.HALFWORD},
                "0x10010004": {"value": "0x12345678", "size": MemorySize.WORD},
            }
        )
        harness_path = create_harness(
            initial_state,
            output_harness_name=self.temp_path / "mixed_harness.asm",
        )

        # Verify harness content
        with open(harness_path, "r") as f:
            content = f.read()
            # Check byte
            self.assertIn("li $t0, 0xAB", content)
            self.assertIn("la $t1, 0x10010000", content)
            self.assertIn("sb $t0, ($t1)", content)

            # Check halfword
            self.assertIn("li $t0, 0xCDEF", content)
            self.assertIn("la $t1, 0x10010002", content)
            self.assertIn("sh $t0, ($t1)", content)

            # Check word
            self.assertIn("li $t0, 0x12345678", content)
            self.assertIn("la $t1, 0x10010004", content)
            self.assertIn("sw $t0, ($t1)", content)

    def test_memory_alignment_validation_halfword(self):
        """Test validation of halfword memory alignment."""
        # Misaligned halfword address should raise ValueError
        with self.assertRaises(ValueError):
            MipsState(
                memory={"0x10010001": {"value": "0xABCD", "size": MemorySize.HALFWORD}}
            )

    def test_memory_alignment_validation_word(self):
        """Test validation of word memory alignment."""
        # Misaligned word address should raise ValueError
        with self.assertRaises(ValueError):
            MipsState(
                memory={"0x10010001": {"value": "0xABCD1234", "size": MemorySize.WORD}},
            )

        with self.assertRaises(ValueError):
            MipsState(
                registers={},
                memory={"0x10010002": {"value": "0xABCD1234", "size": MemorySize.WORD}},
            )


if __name__ == "__main__":
    unittest.main()
