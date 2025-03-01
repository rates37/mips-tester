"""
Functions to create and manage MIPS test harnesses.
"""

from pathlib import Path

from .models import MipsState, JumpType
from .core import config


def create_harness(
    initial_state: MipsState | dict,
    label: str = "main",
    output_harness_name: str | None = None,
    jump_type: JumpType | str = JumpType.JUMP,
) -> Path:
    """Creates a MIPS asm file that initialises register and memory locations with specified values
        before jumping to user code.

    Args:
        initial_state (MipsState | dict): MipsState or dict detailing the desired initial state
        label (str, optional): The label in user code to jump to after initialisation. Defaults to "main".
        output_harness_name (str | None, optional): The name of the output asm harness file. Defaults to config.default_output_harness.
        jump_type (JumpType | str, optional): The type of jump instruction to use to enter user code. Defaults to JumpType.JUMP.

    Returns:
        Path: Path to the created harness asm file.
    """

    # ensure initial_state is a MipsState object
    if isinstance(initial_state, dict):
        initial_state = MipsState(**initial_state)

    # resort to default output harness name
    if output_harness_name is None:
        output_harness_name = config.default_output_harness

    # ensure jump_type is an Enum
    if isinstance(jump_type, str):
        jump_type = JumpType(jump_type)

    # populate harness file with
    harness_path = Path(output_harness_name)
    with harness_path.open("w") as harness_file:
        harness_file.write("# Auto generated test harness\n")
        harness_file.write(".text\n\n")

        # initialise memory locations:
        for addr, val in initial_state.memory.values():
            harness_file.write(f"# Storing {val} in the location {addr}:\n")
            harness_file.write(f"li $t0, {val}\n")
            harness_file.write(f"la $t1, {addr}\n")
            harness_file.write("sw $t0, ($t1)\n\n")

        # initialise register values
        for reg, val in initial_state.registers.dict().items():
            if val is not None:
                harness_file.write(f"# Storing {val} in register ${reg}:\n")
                harness_file.write(f"la ${reg}, {val}\n\n")

        # jump to given label
        harness_file.write(f"# Jumping to user code at label {label}:\n")
        harness_file.write(f"{jump_type.value} {label}\n\n")

        # if using jal, add infinite loop for return
        if jump_type == JumpType.JUMP_AND_LINK:
            harness_file.write(f"# Infinite loop:\n")
            harness_file.write("endLabel: j endLabel\n")

    return harness_path
