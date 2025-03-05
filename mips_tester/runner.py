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
        command.append(f"{harness_name}")

    command.extend(
        [f"{filename}", "nc", "a"]
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
        return TestResult(
            success=False, score=0.0, messages=["Program did not compile correctly"]
        )


def test_run(
    filename: Path | str,
    harness_name: Path | str | None = None,
    verbose: bool = False,
    max_steps: int | None = None,
) -> TestResult:

    # revert to defaults if max_steps not specified:
    if max_steps is None:
        max_steps = config.default_max_steps

    command = ["java", "-jar", str(config.mars_path)]

    # include harness if specified
    if harness_name is not None:
        command.append(f"{str(harness_name)}")

    command.extend([f"{filename}", str(max_steps), "nc", "se1", "ae1"])

    # run program:
    # print(" ".join(command))
    result = subprocess.getstatusoutput(" ".join(command))
    # with open(filename, "r") as f:
    #     print(f.read())
    # print(result)

    if result[0] == 0:
        if verbose:
            print(
                f"Program {' '.join([harness_name, filename] if harness_name else [filename])} did not have runtime errors!"
            )
        return TestResult(success=True, score=1.0)
    else:
        if verbose:
            print(
                f"Program {' '.join([harness_name, filename] if harness_name else [filename])} had runtime error(s)!"
            )
        return TestResult(
            success=False,
            score=0.0,
            messages=["Program execution resulted in runtime errors"],
        )


def test_final_state(
    expected_state: MipsState | dict,
    harness_name: Path | str,
    filename: Path | str,
    verbose: bool = False,
    max_steps: int | None = None,
) -> TestResult:

    # convert expected_state to MipsState if not already:
    if isinstance(expected_state, dict):
        expected_state = MipsState(**expected_state)

    # revert to defaults if max_steps not specified:
    if max_steps is None:
        max_steps = config.default_max_steps

    # check the program assembles first:
    assembly_test = test_assemble(filename, harness_name, False)
    if not assembly_test.success:
        return TestResult(
            success=False,
            score=0.0,
            messages=[f"{filename} did not assemble correctly"],
        )

    # check the program runs:
    run_test = test_run(filename, harness_name, False, max_steps)
    if not run_test.success:
        return TestResult(
            success=False,
            score=0.0,
            messages=[f"{filename} did not run correctly"],
        )

    # prepare command to check both memory and registers
    check_targets = []

    # add memory locations:
    for addr in expected_state.memory:
        check_targets.append(f"{addr}-{addr}")

    # add register names:
    for reg, expected_value in expected_state.registers.model_dump().items():
        if expected_value is not None:
            check_targets.append(f"{reg}")

    # construct command:
    command = [
        "java",
        "-jar",
        str(config.mars_path),
        str(harness_name),
        str(filename),
        str(max_steps),
        "se1",
        "nc",
        *check_targets,
    ]

    result = subprocess.getstatusoutput(" ".join(command))

    output_lines = result[1].split("\n")

    # parse the output:
    total_marks = 0
    available_marks = 0
    messages = []

    # check memory locations:
    for addr in expected_state.memory:
        available_marks += 1

        # find the line in output corresponding to this memory address:
        target_mem_line = next(
            (line for line in output_lines if f"Mem[{addr}]" in line), None
        )

        if not target_mem_line:
            # todo: possibly raise exception here?
            continue

        actual_value = target_mem_line.split()[-1]
        expected_value = expected_state.memory[addr]

        if int(actual_value, base=16) == int(expected_value, base=0):
            total_marks += 1
            if verbose:
                print(f"Correct value in {addr}")
        else:
            message = f"Incorrect value in {addr}! Expected: {expected_value} Actual: {actual_value}"
            messages.append(message)
            if verbose:
                print(message)

    # check register values
    for reg, expected_value in expected_state.registers.model_dump().items():
        if expected_value is None:
            continue
        available_marks += 1

        target_reg_line = next(
            (line for line in output_lines if f"${reg}" in line), None
        )

        if not target_reg_line:
            # todo: possibly raise exception here?
            continue
        actual_value = target_reg_line.split()[-1]

        if int(actual_value, base=16) == int(expected_value, base=0):
            total_marks += 1
            if verbose:
                print(f"Correct value in ${reg}")
        else:
            message = f"Incorrect value in ${reg}! Expected: {expected_value} Actual: {actual_value}"
            messages.append(message)
            if verbose:
                print(message)

    score = total_marks / available_marks if available_marks > 0 else 1.0
    return TestResult(success=True, score=score, messages=messages)
