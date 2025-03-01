import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from mips_tester import create_harness, MipsState, JumpType, configure

"""
Todo: in setup, curl mars to temp dir and set that as mars path
command = ['curl', '-o', './mars.jar', 'https://dpetersanderson.github.io/Mars4_5.jar']
subprocess.run(command)
"""


class TestHarness(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        # !  <---  MAY NEED TO MODIFY THIS LINE TO REFLECT YOUR mars.jar LOCATION  --->
        configure(
            mars_path="./mars.jar",
            max_steps=1000,
            output_harness="test_harness.asm",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_create_harness_basic(self):
        initial_state = MipsState(
            registers={"a0": "10", "v0": "20"},
            memory={"1000": "30", "1004": "40"},
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
        initial_state = MipsState(
            registers={"a0": "10", "v0": "20"},
            memory={"1000": "30", "1004": "40"},
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
        initial_state = MipsState(
            registers={"a0": "10", "v0": "20"},
            memory={"1000": "30", "1004": "40"},
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


if __name__ == "__main__":
    unittest.main()
