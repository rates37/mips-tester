import json
from .models import MipsState, JumpType
from .core import configure, config
from .harness import create_harness
from .runner import test_final_state


def load_and_run_tests(json_file: str) -> None:
    """Loads test cases from a JSON file and executes them, printing results to console."""
    with open(json_file, 'r') as f:
        test_data = json.load(f)

    for test_case in test_data['tests']:
        print(f"Running test: {test_case['name']} - {test_case['description']}")

        # Configure Mars path
        configure(mars_path=test_case['mars_path'])

        # Create initial state
        initial_state_data = test_case['initial_state']
        initial_state = MipsState.from_dict(initial_state_data)

        # Create test harness
        harness_path = create_harness(
            initial_state=initial_state,
            label=test_case['harness']['label'],
            jump_type=JumpType[test_case['harness']['jump_type']]
        )

        # Define expected final state
        expected_state_data = test_case['expected_state']
        expected_state = MipsState.from_dict(expected_state_data)
        try:
            max_steps = test_case['max_steps']
        except:
            max_steps = config.default_max_steps

        # Test the program
        result = test_final_state(
            expected_state=expected_state,
            harness_name=harness_path,
            filename=test_case['program_file'],
            max_steps=max_steps
        )

        # Check the result
        print(f"Test {'passed' if result.score == 1 else 'failed'}")
        if result.messages:
            for msg in result.messages:
                print(f"\t- {msg}")
