from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from app.calculator_repl import calculator_repl
from app.exceptions import OperationError, ValidationError


def run_repl(inputs, calculator=None):
    """Run the calculator REPL with mocked user input."""
    if calculator is None:
        calculator = MagicMock()

    with patch("app.calculator_repl.Calculator", return_value=calculator), \
         patch("builtins.input", side_effect=inputs):
        calculator_repl()

    return calculator


def test_help_command(capsys):
    run_repl(["help", "exit"])

    output = capsys.readouterr().out

    assert "Available commands:" in output
    assert "add, subtract, multiply, divide, power, root" in output
    assert "history - Show calculation history" in output
    assert "Goodbye!" in output


def test_exit_saves_history(capsys):
    calc = MagicMock()

    run_repl(["exit"], calc)

    calc.save_history.assert_called_once()
    assert "History saved successfully." in capsys.readouterr().out


def test_exit_save_failure(capsys):
    calc = MagicMock()
    calc.save_history.side_effect = Exception("save failed")

    run_repl(["exit"], calc)

    output = capsys.readouterr().out

    assert "Warning: Could not save history: save failed" in output
    assert "Goodbye!" in output


@pytest.mark.parametrize(
    "history, expected",
    [
        ([], "No calculations in history"),
        (["2 + 3 = 5"], "1. 2 + 3 = 5"),
    ],
)
def test_history_command(history, expected, capsys):
    calc = MagicMock()
    calc.show_history.return_value = history

    run_repl(["history", "exit"], calc)

    assert expected in capsys.readouterr().out


def test_clear_command(capsys):
    calc = MagicMock()

    run_repl(["clear", "exit"], calc)

    calc.clear_history.assert_called_once()
    assert "History cleared" in capsys.readouterr().out


@pytest.mark.parametrize(
    "command, method_name, return_value, expected",
    [
        ("undo", "undo", True, "Operation undone"),
        ("undo", "undo", False, "Nothing to undo"),
        ("redo", "redo", True, "Operation redone"),
        ("redo", "redo", False, "Nothing to redo"),
    ],
)
def test_undo_redo_commands(command, method_name, return_value, expected, capsys):
    calc = MagicMock()
    getattr(calc, method_name).return_value = return_value

    run_repl([command, "exit"], calc)

    assert expected in capsys.readouterr().out


def test_save_command_success(capsys):
    calc = MagicMock()

    run_repl(["save", "exit"], calc)

    assert calc.save_history.call_count == 2
    assert "History saved successfully" in capsys.readouterr().out


def test_save_command_failure(capsys):
    calc = MagicMock()
    calc.save_history.side_effect = [Exception("save failed"), None]

    run_repl(["save", "exit"], calc)

    assert "Error saving history: save failed" in capsys.readouterr().out


def test_load_command_success(capsys):
    calc = MagicMock()

    run_repl(["load", "exit"], calc)

    calc.load_history.assert_called_once()
    assert "History loaded successfully" in capsys.readouterr().out


def test_load_command_failure(capsys):
    calc = MagicMock()
    calc.load_history.side_effect = Exception("load failed")

    run_repl(["load", "exit"], calc)

    assert "Error loading history: load failed" in capsys.readouterr().out


def test_arithmetic_operation_decimal_result(capsys):
    calc = MagicMock()
    calc.perform_operation.return_value = Decimal("5.00")

    with patch("app.calculator_repl.OperationFactory.create_operation") as factory:
        operation = MagicMock()
        factory.return_value = operation

        run_repl(["add", "2", "3", "exit"], calc)

        factory.assert_called_once_with("add")
        calc.set_operation.assert_called_once_with(operation)
        calc.perform_operation.assert_called_once_with("2", "3")

    assert "Result: 5" in capsys.readouterr().out


def test_arithmetic_operation_non_decimal_result(capsys):
    calc = MagicMock()
    calc.perform_operation.return_value = 5

    run_repl(["add", "2", "3", "exit"], calc)

    assert "Result: 5" in capsys.readouterr().out


@pytest.mark.parametrize(
    "inputs",
    [
        ["add", "cancel", "exit"],
        ["add", "2", "cancel", "exit"],
    ],
)
def test_cancel_operation(inputs, capsys):
    run_repl(inputs)

    assert "Operation cancelled" in capsys.readouterr().out


@pytest.mark.parametrize(
    "exception",
    [
        ValidationError("invalid input"),
        OperationError("operation failed"),
    ],
)
def test_known_operation_errors(exception, capsys):
    calc = MagicMock()
    calc.perform_operation.side_effect = exception

    run_repl(["add", "2", "3", "exit"], calc)

    assert f"Error: {exception}" in capsys.readouterr().out


def test_unexpected_operation_error(capsys):
    calc = MagicMock()
    calc.perform_operation.side_effect = RuntimeError("unexpected")

    run_repl(["add", "2", "3", "exit"], calc)

    assert "Unexpected error: unexpected" in capsys.readouterr().out


def test_unknown_command(capsys):
    run_repl(["something", "exit"])

    assert "Unknown command: 'something'" in capsys.readouterr().out


def test_keyboard_interrupt(capsys):
    run_repl([KeyboardInterrupt(), "exit"])

    assert "Operation cancelled" in capsys.readouterr().out


def test_eof_error(capsys):
    run_repl([EOFError()])

    assert "Input terminated. Exiting..." in capsys.readouterr().out


def test_general_loop_exception(capsys):
    run_repl([RuntimeError("input failure"), "exit"])

    assert "Error: input failure" in capsys.readouterr().out


def test_fatal_initialization_error(capsys):
    with patch(
        "app.calculator_repl.Calculator",
        side_effect=RuntimeError("initialization failed"),
    ), patch("app.calculator_repl.logging.error") as log_error:

        with pytest.raises(RuntimeError, match="initialization failed"):
            calculator_repl()

    output = capsys.readouterr().out

    assert "Fatal error: initialization failed" in output
    log_error.assert_called_once()