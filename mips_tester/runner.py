"""
Functions to assemble, run and check final state of MIPS programs
"""

import subprocess
from pathlib import Path

from .models import MipsState, TestResult
from .core import config
from .harness import create_harness


def test_assemble(
    filename: Path | str, harness_name: Path | str | None = None, verbose: bool = False
) -> TestResult:
    """Checks if a MIPS program (and it's harness) assembles successfully.

    Args:
        filename (Path | str): The MIPS program to test
        harness_name (Path | str | None, optional): Optional test harness to setup/register memory values. Defaults to None.
        verbose (bool, optional): Flag to print informative feedback. Defaults to False.

    Returns:
        TestResult: Contains success status proportion of passed tests, and corresponding messages.
    """
    command = ["java", "-jar", str(config.mars_path)]

    if harness_name is not None:
        command.append(f'"{harness_name}"')

    command.extend(
        [f'"{filename}"', "nc", "a"]
    )  # a -> assemble only, nc -> no copyright message

    result = subprocess.getstatusoutput(
        " ".join(command)
    )  # todo: replace with subprocess.run

    if result[1] == "":
        if verbose:
            print(
                f"Program {' '.join([harness_name, filename] if harness_name else [filename])} assembled correctly!"
            )
        return TestResult(success=True, score=1.0)
    else:
        if verbose:
            print(
                f"Program {' '.join([harness_name, filename] if harness_name else [filename])} did not assemble correctly!"
            )
        return TestResult(success=False, score=0.0, messages=["Program did not compile correctly"])


def test_run(
    filename: Path | str,
    harness_name: Path | str | None = None,
    verbose: bool = False,
    max_steps: int | None = None,
) -> TestResult:

    pass


def test_final_state(
    expected_state: MipsState | dict,
    harness_name: Path | str,
    filename: Path | str,
    verbose: bool = False,
    max_steps: int | None = None,
) -> TestResult:

    pass
