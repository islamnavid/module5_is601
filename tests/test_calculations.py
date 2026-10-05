import pytest
from decimal import Decimal
from datetime import datetime
from app.calculation import Calculation
from app.exceptions import OperationError
import logging
from unittest.mock import Mock, patch


def test_addition():
    calc = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    assert calc.result == Decimal("5")


def test_subtraction():
    calc = Calculation(operation="Subtraction", operand1=Decimal("5"), operand2=Decimal("3"))
    assert calc.result == Decimal("2")


def test_multiplication():
    calc = Calculation(operation="Multiplication", operand1=Decimal("4"), operand2=Decimal("2"))
    assert calc.result == Decimal("8")


def test_division():
    calc = Calculation(operation="Division", operand1=Decimal("8"), operand2=Decimal("2"))
    assert calc.result == Decimal("4")


def test_division_by_zero():
    with pytest.raises(OperationError, match="Division by zero is not allowed"):
        Calculation(operation="Division", operand1=Decimal("8"), operand2=Decimal("0"))


def test_power():
    calc = Calculation(operation="Power", operand1=Decimal("2"), operand2=Decimal("3"))
    assert calc.result == Decimal("8")


def test_negative_power():
    with pytest.raises(OperationError, match="Negative exponents are not supported"):
        Calculation(operation="Power", operand1=Decimal("2"), operand2=Decimal("-3"))


def test_root():
    calc = Calculation(operation="Root", operand1=Decimal("16"), operand2=Decimal("2"))
    assert calc.result == Decimal("4")


def test_invalid_root():
    with pytest.raises(OperationError, match="Cannot calculate root of negative number"):
        Calculation(operation="Root", operand1=Decimal("-16"), operand2=Decimal("2"))


def test_unknown_operation():
    with pytest.raises(OperationError, match="Unknown operation"):
        Calculation(operation="Unknown", operand1=Decimal("5"), operand2=Decimal("3"))


def test_to_dict():
    calc = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    result_dict = calc.to_dict()
    assert result_dict == {
        "operation": "Addition",
        "operand1": "2",
        "operand2": "3",
        "result": "5",
        "timestamp": calc.timestamp.isoformat()
    }


def test_from_dict():
    data = {
        "operation": "Addition",
        "operand1": "2",
        "operand2": "3",
        "result": "5",
        "timestamp": datetime.now().isoformat()
    }
    calc = Calculation.from_dict(data)
    assert calc.operation == "Addition"
    assert calc.operand1 == Decimal("2")
    assert calc.operand2 == Decimal("3")
    assert calc.result == Decimal("5")


def test_invalid_from_dict():
    data = {
        "operation": "Addition",
        "operand1": "invalid",
        "operand2": "3",
        "result": "5",
        "timestamp": datetime.now().isoformat()
    }
    with pytest.raises(OperationError, match="Invalid calculation data"):
        Calculation.from_dict(data)


def test_format_result():
    calc = Calculation(operation="Division", operand1=Decimal("1"), operand2=Decimal("3"))
    assert calc.format_result(precision=2) == "0.33"
    assert calc.format_result(precision=10) == "0.3333333333"


def test_equality():
    calc1 = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    calc2 = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    calc3 = Calculation(operation="Subtraction", operand1=Decimal("5"), operand2=Decimal("3"))
    assert calc1 == calc2
    assert calc1 != calc3


# New Test to Cover Logging Warning
def test_from_dict_result_mismatch(caplog):
    """
    Test the from_dict method to ensure it logs a warning when the saved result
    does not match the computed result.
    """
    # Arrange
    data = {
        "operation": "Addition",
        "operand1": "2",
        "operand2": "3",
        "result": "10",  # Incorrect result to trigger logging.warning
        "timestamp": datetime.now().isoformat()
    }

    # Act
    with caplog.at_level(logging.WARNING):
        calc = Calculation.from_dict(data)

    # Assert
    assert "Loaded calculation result 10 differs from computed result 5" in caplog.text
def test_calculation_post_init_sets_result():
    """Test that post initialization automatically calculates the result."""
    calc = Calculation("Addition", Decimal("2"), Decimal("3"))

    assert calc.result == Decimal("5")


def test_raise_helper_methods():
    """Test calculation error helper methods."""
    with pytest.raises(OperationError, match="Division by zero is not allowed"):
        Calculation._raise_div_zero()

    with pytest.raises(OperationError, match="Negative exponents are not supported"):
        Calculation._raise_neg_power()

    with pytest.raises(OperationError, match="Zero root is undefined"):
        Calculation._raise_invalid_root(Decimal("4"), Decimal("0"))

    with pytest.raises(
        OperationError,
        match="Cannot calculate root of negative number"
    ):
        Calculation._raise_invalid_root(Decimal("-4"), Decimal("2"))

    with pytest.raises(OperationError, match="Invalid root operation"):
        Calculation._raise_invalid_root(Decimal("4"), Decimal("2"))


def test_calculation_equality_with_non_calculation():
    """Test comparison with an unrelated object."""
    calc = Calculation("Addition", Decimal("2"), Decimal("3"))

    assert calc.__eq__("not a calculation") is NotImplemented


def test_from_dict_with_different_saved_result(caplog):
    """Test loading data whose stored result differs from the computed result."""
    data = {
        "operation": "Addition",
        "operand1": "2",
        "operand2": "3",
        "result": "999",
        "timestamp": "2026-10-05T12:00:00",
    }

    calc = Calculation.from_dict(data)

    assert calc.result == Decimal("5")
    assert "differs from computed result" in caplog.text


def test_calculate_wraps_arithmetic_error():
    """Test that calculation errors are wrapped in OperationError."""
    calc = Calculation("Addition", Decimal("2"), Decimal("3"))

    with patch.object(
        calc,
        "operand1",
        Mock(__add__=Mock(side_effect=ArithmeticError("test arithmetic error")))
    ):
        with pytest.raises(
            OperationError,
            match="Calculation failed: test arithmetic error"
        ):
            calc.calculate()


def test_calculation_str():
    """Test the human-readable string representation."""
    calc = Calculation("Addition", Decimal("2"), Decimal("3"))

    assert str(calc) == "Addition(2, 3) = 5"


def test_calculation_repr():
    """Test the detailed representation of a calculation."""
    calc = Calculation("Addition", Decimal("2"), Decimal("3"))

    representation = repr(calc)

    assert "Calculation(operation='Addition'" in representation
    assert "operand1=2" in representation
    assert "operand2=3" in representation
    assert "result=5" in representation