"""
Functions to assemble, run and check final state of MIPS programs
"""

import subprocess
from pathlib import Path

from .models import MipsState, TestResult, MemorySize
from .core import config

def _check_exists(filename: Path | str, harness_name: Path | str = None) -> None | TestResult:
    # checks whether the file name and harness exist
    filename = Path(filename)
    if not Path.exists(filename):
        return TestResult(success=False, score=0.0, messages=[f"File {filename} was not found."])
    
    if harness_name:
        harness_name = Path(harness_name)
        if not Path.exists(harness_name):
            return TestResult(success=False, score=0.0, messages=[f"Harness {harness_name} was not found."])
    return None

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
    # check file name and path exists:
    file_exists_result = _check_exists(filename, harness_name)
    if file_exists_result is not None:
        return file_exists_result
    
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
            success=False, score=0.0, messages=["Program did not assemble correctly"]
        )


def test_run(
    filename: Path | str,
    harness_name: Path | str | None = None,
    verbose: bool = False,
    max_steps: int | None = None,
) -> TestResult:
    # check file name and path exists:
    file_exists_result = _check_exists(filename, harness_name)
    if file_exists_result is not None:
        return file_exists_result
    

    # revert to defaults if max_steps not specified:
    if max_steps is None:
        max_steps = config.default_max_steps

    command = ["java", "-jar", str(config.mars_path)]

    # include harness if specified
    if harness_name is not None:
        command.append(f"{str(harness_name)}")

    command.extend([f"{filename}", str(max_steps), "nc", "se1", "ae1"])

    # run program:
    result = subprocess.getstatusoutput(" ".join(command))

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


def extract_memory_value(word_value: int, addr: int, size: MemorySize) -> int:
    """Extract the correct portion of a word based on address and size

    Args:
        word_value (int): The full word value (4 bytes)
        addr (int): The memory address to extract from
        size (MemorySize): The size of the memory address

    Returns:
        int: The extracted value based on size and alignment
    """
    byte_offset = addr % 4

    if size == MemorySize.BYTE:
        shamt = byte_offset * 8
        return (word_value >> shamt) & 0xFF
    elif size == MemorySize.HALFWORD:
        shamt = (byte_offset & ~1) * 8
        return (word_value >> shamt) & 0xFFFF
    else:  # WORD (default)
        return word_value


def test_final_state(
    expected_state: MipsState | dict,
    harness_name: Path | str,
    filename: Path | str,
    verbose: bool = False,
    max_steps: int | None = None,
) -> TestResult:
    # check file name and path exists:
    file_exists_result = _check_exists(filename, harness_name)
    if file_exists_result is not None:
        return file_exists_result
    

    # convert expected_state to MipsState if not already:
    if isinstance(expected_state, dict):
        expected_state = MipsState.from_dict(expected_state)

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

    # Add word-aligned memory addresses for MARS to check
    word_aligned_addresses = set()
    for addr_str in expected_state.memory:
        # Get the word-aligned address containing our target address
        addr_int = int(addr_str, 0)
        word_addr = addr_int & ~0x3  # Mask off bottom 2 bits to get word alignment
        word_aligned_addresses.add(f"0x{word_addr:08x}")

    # Add the word-aligned addresses to check targets
    for addr in word_aligned_addresses:
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

    # Store actual memory values for later processing
    actual_memory = {}
    for line in output_lines:
        if "Mem[0x" in line:
            parts = line.split()
            addr = parts[0].replace("Mem[", "").replace("]", "")
            value = parts[-1]
            actual_memory[addr] = int(value, 16)

    # check memory locations:
    for addr in expected_state.memory:
        available_marks += 1

        entry = expected_state.memory[addr]
        addr_int = int(addr, 0)

        # find the word-aligned address containing the target address:
        word_addr_int = addr_int & ~0x3  # set bottom 2 bits to 0 to make word aligned
        word_addr_hex = f"0x{word_addr_int:08x}"

        if word_addr_hex not in actual_memory:
            messages.append(f"Memory location {word_addr_hex} not found in output")
            if verbose:
                print(f"Memory location {word_addr_hex} not found in output")
            continue

        # get full word value from memory:
        word_value = actual_memory[word_addr_hex]

        # get correct portion of value based on memory entry size:
        actual_value = extract_memory_value(word_value, addr_int, entry.size)
        expected_value = int(entry.value, 0)

        # mask non-words to ensure proper comparison (not strictly necessary):
        if entry.size == MemorySize.BYTE:
            expected_value &= 0xFF
        elif entry.size == MemorySize.HALFWORD:
            expected_value &= 0xFFFF

        if actual_value == expected_value:
            total_marks += 1
            if verbose:
                print(f"Correct {entry.size.value} value at {addr}")
        else:
            message = f"Incorrect {entry.size.value} value at {addr}! Expected: {hex(expected_value)} Actual: {hex(actual_value)}"
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
            raise ValueError(f"${reg} not found in output, critical error occurred")

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
