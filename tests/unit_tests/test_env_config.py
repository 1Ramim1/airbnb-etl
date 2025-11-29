import os
import pytest
from unittest.mock import patch
from config.env_config import setup_env, cleanup_previous_env


@patch("os.path.exists")
def test_setup_env_file_not_found_dev(mock_exists):
    mock_exists.return_value = False
    with pytest.raises(
        FileNotFoundError, match="Environment file '.env.dev' not found"
    ):
        setup_env(["script_name", "dev"])


@patch("os.path.exists")
def test_setup_env_file_not_found_test(mock_exists):
    mock_exists.return_value = False
    with pytest.raises(
        FileNotFoundError, match="Environment file '.env.test' not found"
    ):
        setup_env(["script_name", "test"])


@patch("os.path.exists")
def test_setup_env_file_not_found_prod(mock_exists):
    mock_exists.return_value = False
    with pytest.raises(
        FileNotFoundError, match="Environment file '.env' not found"
    ):
        setup_env(["script_name", "prod"])


def test_setup_env_invalid_environment():
    with pytest.raises(ValueError, match="Please provide an environment"):
        setup_env(["script_name", "invalid"])


def test_setup_env_no_environment():
    with pytest.raises(ValueError, match="Please provide an environment"):
        setup_env(["script_name"])


def test_setup_env_too_many_args():
    with pytest.raises(ValueError, match="Please provide an environment"):
        setup_env(["script_name", "dev", "extra"])


def test_cleanup_previous_env():
    # Set some environment variables
    test_vars = {
        "SOURCE_DB_NAME": "test_db",
        "SOURCE_DB_USER": "test_user",
        "TARGET_DB_NAME": "target_db",
        "UNRELATED_VAR": "should_remain",
    }

    for key, value in test_vars.items():
        os.environ[key] = value

    cleanup_previous_env()

    # Check that DB vars are cleared but unrelated vars remain
    assert "SOURCE_DB_NAME" not in os.environ
    assert "SOURCE_DB_USER" not in os.environ
    assert "TARGET_DB_NAME" not in os.environ
    assert os.environ.get("UNRELATED_VAR") == "should_remain"

    # Clean up
    if "UNRELATED_VAR" in os.environ:
        del os.environ["UNRELATED_VAR"]


@patch("config.env_config.load_dotenv")
@patch("os.path.exists")
def test_setup_env_loads_correct_env_file(
    mock_exists, mock_load_dotenv, mocker
):
    mock_exists.return_value = True
    mocker.patch("config.env_config.cleanup_previous_env")

    setup_env(["script_name", "dev"])
    mock_load_dotenv.assert_called_with(".env.dev", override=True)

    setup_env(["script_name", "prod"])
    mock_load_dotenv.assert_called_with(".env", override=True)


@patch("os.path.exists")
def test_setup_env_file_not_found(mock_exists, mocker):
    mock_exists.return_value = False
    mocker.patch("config.env_config.cleanup_previous_env")

    with pytest.raises(
        FileNotFoundError, match="Environment file '.env.dev' not found"
    ):
        setup_env(["script_name", "dev"])
