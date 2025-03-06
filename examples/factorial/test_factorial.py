from mips_tester import configure, MipsState, create_harness, test_final_state, JumpType

# Configure the Mars simulator location
configure(mars_path="./mars.jar")

# Create initial state
initial_state = MipsState(
    registers={
        "a0": "10"  # Input value for factorial
    }
)

# Create test harness
harness_path = create_harness(
    initial_state=initial_state,
    label="factorial",  # Label to jump to in the MIPS program
    jump_type=JumpType.JUMP_AND_LINK  # Type of jump instruction to use
)

# Define expected final state
expected_state = MipsState(
    registers={
        "v0": "3628800"  # Expected result (10!)
    }
)

# Test the program
result = test_final_state(
    expected_state=expected_state,
    harness_name=harness_path,
    filename="examples/factorial/factorial.asm"
)

# Check the result
print(f"Test {'passed' if result.score == 1 else 'failed'}")
if result.messages:
    print("Issues found:")
    for msg in result.messages:
        print(f"\t`- {msg}")
