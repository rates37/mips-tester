# mips-tester

A Python library for testing MIPS assembly functions / programs using the Mars MIPS simulator.

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

This library provides tools to automate the testing of MIPS assembly programs using the MARS simulator. It currently supports the following features:

- Test if programs/subroutines assemble correctly
- Test if programs/subroutines run without runtime errors
- Pre-initialise state of registers and memory before running program or function
- Check final state of registers and memory

In addition, this library was written with:
- Strong type safety with Pydantic models
- Well tested and documented (hopefully)

## How it works

This library employs a systematic approach to testing MIPS assembly programs:

1. Define test scenario: **You** specify the initial and expected final states of the machine (registers and memory values).

2.  Harness generation: **The Library** automatically generates a "harness" assembly file that:
    * Sets up the specified initial state of the processor
    * Jumps to the target code (either using Jump or Jump-and-Link)

3. Program Execution: **The Library** uses the [Mars MIPS Simulator](https://dpetersanderson.github.io/download.html) to assemble and execute the combined harness and target assembly program.

4. State Verification: **The Library** compares the actual final state of the MIPS machine with the values (register and memory locations) in the expected state.

<!-- # diagram todo -->




## Requirements
* Python >= 3.13
* A Java Runtime Environment
* [Mars MIPS Simulator](https://dpetersanderson.github.io/download.html)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/rates37/mips-tester.git
```

2. Navigate to main project directory:
```bash
cd mips-tester
```

3. Setup a Virtual Environment (optional)
```bash
python3 -m venv .venv
source .venv/bin/activate
```

4. Install package locally:
```bash
pip install -e .
```

5. Verify installation:
If no errors occur, the package was installed successfully.
```bash
python -c "import mips_tester"
```

### Uninstallation
To remove the package:
```bash
pip uninstall mips_tester
```

## Quick Start

```python
from mips_tester import MipsState, create_harness, test_final_state

# Define initial state:
initial_state = MipsState(
    registers={"t0": "10", "a0": "0xFF"},
    memory={
        "0x10010000": {"value": "0x42", "size": MemorySize.BYTE},
        "0x10010002": {"value": "0xFACE", "size": MemorySize.HALFWORD},
        "0x10010004": {"value": "0x12345678", "size": MemorySize.WORD}
    }
)

# Create test harness:
harness_path = create_harness(initial_state, "main")

# Test program against final state:
expected_state = MipsState(
    registers={"v0": "42"},
    memory={
        "0x10010008": {"value": "0x99", "size": MemorySize.BYTE}
    }
)

result = test_final_state(
    expected_state=expected_state,
    harness_name=harness_path,
    filename="student_solution.asm",
    verbose=True
)

# Check results:
print(f"Score: {result.score * 100}%")
print("Feedback:")
for message in result.messages:
    print(f"- {message}")
```

## Configuration

The library can be configured using the `configure` function:

```py
from mips_tester import configure

configure(
    mars_path="/path/to/mars.jar",  # a path to the mars jar file on the local machine
    max_steps=10_000                # the default maximum number of steps to simulate the program for
)
```

## Key Components

### MipsState

Represents the state of a MIPS program, including registers and memory values:

```py
state = MipsState(
    registers={"t0": "10", "a0": "0xFF"},
    memory={
        "0x10010000": {"value": "0x42", "size": MemorySize.BYTE},
        "0x10010002": {"value": "0xFACE", "size": MemorySize.HALFWORD},
        "0x10010004": {"value": "0x12345678", "size": MemorySize.WORD}
    }
)
```

### Testing Functions

* `test_assemble`: Checks if a program assembles correctly
* `test_run`: Checks if a program runs without errors
* `test_final_state`: Verifies the final state matches expected final state values

All of the above functions return a `TestResult` object:
```py
class TestResult(BaseModel):
    success: bool
    score: float
    messages: list[str]
```

### Memory Access Sizes

The library supports the following memory access sizes (in accordance with the MIPS assembly language):

* `MemorySize.BYTE`: 1 byte (8 bits)
* `MemorySize.HALFWORD`: 2 bytes (16 bits)
* `MemorySize.WORD`: 4 bytes (32 bits)

Example:

```py
state = MipsState(
    memory={
        "0x10010000": {"value": "0x42", "size": MemorySize.BYTE},  # Single byte
        "0x10010002": {"value": "0xFACE", "size": MemorySize.HALFWORD},  # 2 bytes
        "0x10010004": {"value": "0x12345678", "size": MemorySize.WORD},  # 4 bytes
        "0x10010008": {"value": "0x43218765"},  # default is 4 bytes
    }
)
```

## License
MIT License - See LICENSE file for details.

## Contributions

Contributions are warmly welcome. Please feel free to fork this repo, add your features/bug fixes, and open a pull request.