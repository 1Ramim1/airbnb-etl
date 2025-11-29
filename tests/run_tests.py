import sys
import subprocess


def main():
    command = sys.argv[1]

    # Define test directories and corresponding coverage targets
    test_config = {
        'unit': {'dir': 'tests/unit_tests', 'cov': ['config', 'src']},
        'integration': {'dir': 'tests/integration_tests', 'cov': []},
        'component': {'dir': 'tests/component_tests', 'cov': []},
        'all': {'dir': 'tests', 'cov': ['config', 'etl']},
    }

    # Check to see if a command was supplied for the test run
    if command in test_config:
        # Access the test_config dictionary to get the test directory
        # and coverage targets
        test_dir = test_config[command]['dir']
        cov_sources = ','.join(test_config[command]['cov'])

        # Build the test command for tests with coverage
        if cov_sources:
            cov_command = (
                f'ENV=test coverage run --source={cov_sources} '
                f'--omit=*/__init__.py -m pytest --verbose {test_dir} '
                '&& coverage report -m && coverage html '
                '&& coverage report --fail-under=90'
            )
        else:
            cov_command = f'ENV=test pytest --verbose {test_dir}'

        subprocess.run(cov_command, shell=True)
    elif command == 'lint':
        subprocess.run(['flake8', '.'])
    else:
        raise ValueError(f"Unknown command: {command}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError(
            "Usage: run_tests.py <unit|integration|component|all|lint>"
        )
    else:
        main()
