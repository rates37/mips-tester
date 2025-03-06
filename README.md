# mips-tester

A Python library for testing MIPS assembly functions / programs using the Mars MIPS simulator.

## Features

- Test if programs assemble correctly
- Test if programs run without runtime errors
- Pre-initialise state of registers and memory before running program or function
- Check final state of registers and memory
- Strong type safety with Pydantic models
- Well tested and documented (hopefully)

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

## Usage

Todo


## How it Works:

Todo

## Examples

