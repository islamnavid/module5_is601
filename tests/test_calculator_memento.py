import datetime
from decimal import Decimal

import pytest

from app.calculation import Calculation
from app.calculator_memento import CalculatorMemento


@pytest.fixture
def sample_calculations():
    """Create sample calculations for memento tests."""
    return [
        Calculation("Addition", Decimal("2"), Decimal("3")),
        Calculation("Multiplication", Decimal("4"), Decimal("5")),
    ]


def test_memento_creation(sample_calculations):
    """Test creating a CalculatorMemento."""
    memento = CalculatorMemento(history=sample_calculations)

    assert memento.history == sample_calculations
    assert isinstance(memento.timestamp, datetime.datetime)


def test_memento_to_dict(sample_calculations):
    """Test serializing a memento to a dictionary."""
    timestamp = datetime.datetime(2026, 10, 5, 12, 0, 0)

    memento = CalculatorMemento(
        history=sample_calculations,
        timestamp=timestamp
    )

    data = memento.to_dict()

    assert data["timestamp"] == timestamp.isoformat()
    assert len(data["history"]) == 2

    assert data["history"][0]["operation"] == "Addition"
    assert data["history"][0]["operand1"] == "2"
    assert data["history"][0]["operand2"] == "3"
    assert data["history"][0]["result"] == "5"

    assert data["history"][1]["operation"] == "Multiplication"
    assert data["history"][1]["result"] == "20"


def test_memento_from_dict():
    """Test deserializing a dictionary into a CalculatorMemento."""
    data = {
        "history": [
            {
                "operation": "Addition",
                "operand1": "10",
                "operand2": "5",
                "result": "15",
                "timestamp": "2026-10-05T12:00:00",
            }
        ],
        "timestamp": "2026-10-05T12:30:00",
    }

    memento = CalculatorMemento.from_dict(data)

    assert len(memento.history) == 1
    assert isinstance(memento.history[0], Calculation)
    assert memento.history[0].operation == "Addition"
    assert memento.history[0].operand1 == Decimal("10")
    assert memento.history[0].operand2 == Decimal("5")
    assert memento.history[0].result == Decimal("15")
    assert memento.timestamp == datetime.datetime(2026, 10, 5, 12, 30, 0)


@pytest.mark.parametrize(
    "operation,operand1,operand2,expected_result",
    [
        ("Addition", "2", "3", Decimal("5")),
        ("Subtraction", "10", "4", Decimal("6")),
        ("Multiplication", "3", "5", Decimal("15")),
        ("Division", "20", "4", Decimal("5")),
        ("Power", "2", "3", Decimal("8")),
        ("Root", "9", "2", Decimal("3")),
    ],
)
def test_memento_serialization_with_operations(
    operation,
    operand1,
    operand2,
    expected_result,
):
    """Test memento serialization for all supported calculator operations."""
    calculation = Calculation(
        operation,
        Decimal(operand1),
        Decimal(operand2),
    )

    memento = CalculatorMemento(history=[calculation])

    restored = CalculatorMemento.from_dict(memento.to_dict())

    assert len(restored.history) == 1
    assert restored.history[0].operation == operation
    assert restored.history[0].result == expected_result