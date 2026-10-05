import datetime
from pathlib import Path
import pandas as pd
import pytest
from unittest.mock import Mock, patch, PropertyMock
from decimal import Decimal
from tempfile import TemporaryDirectory
from app.calculator import Calculator
from app.calculator_repl import calculator_repl
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError, ValidationError
from app.history import LoggingObserver, AutoSaveObserver
from app.operations import OperationFactory

# Fixture to initialize Calculator with a temporary directory for file paths
@pytest.fixture
def calculator():
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = CalculatorConfig(base_dir=temp_path)

        # Patch properties to use the temporary directory paths
        with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
             patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file, \
             patch.object(CalculatorConfig, 'history_dir', new_callable=PropertyMock) as mock_history_dir, \
             patch.object(CalculatorConfig, 'history_file', new_callable=PropertyMock) as mock_history_file:
            
            # Set return values to use paths within the temporary directory
            mock_log_dir.return_value = temp_path / "logs"
            mock_log_file.return_value = temp_path / "logs/calculator.log"
            mock_history_dir.return_value = temp_path / "history"
            mock_history_file.return_value = temp_path / "history/calculator_history.csv"
            
            # Return an instance of Calculator with the mocked config
            yield Calculator(config=config)

# Test Calculator Initialization

def test_calculator_initialization(calculator):
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []
    assert calculator.operation_strategy is None

# Test Logging Setup

@patch('app.calculator.logging.info')
def test_logging_setup(logging_info_mock):
    with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
         patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file:
        mock_log_dir.return_value = Path('/tmp/logs')
        mock_log_file.return_value = Path('/tmp/logs/calculator.log')
        
        # Instantiate calculator to trigger logging
        calculator = Calculator(CalculatorConfig())
        logging_info_mock.assert_any_call("Calculator initialized with configuration")

# Test Adding and Removing Observers

def test_add_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    assert observer in calculator.observers

def test_remove_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    calculator.remove_observer(observer)
    assert observer not in calculator.observers

# Test Setting Operations

def test_set_operation(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    assert calculator.operation_strategy == operation

# Test Performing Operations

def test_perform_operation_addition(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    result = calculator.perform_operation(2, 3)
    assert result == Decimal('5')

def test_perform_operation_validation_error(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    with pytest.raises(ValidationError):
        calculator.perform_operation('invalid', 3)

def test_perform_operation_operation_error(calculator):
    with pytest.raises(OperationError, match="No operation set"):
        calculator.perform_operation(2, 3)

# Test Undo/Redo Functionality

def test_undo(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.undo()
    assert calculator.history == []

def test_redo(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.undo()
    calculator.redo()
    assert len(calculator.history) == 1

# Test History Management

@patch('app.calculator.pd.DataFrame.to_csv')
def test_save_history(mock_to_csv, calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.save_history()
    mock_to_csv.assert_called_once()

@patch('app.calculator.pd.read_csv')
@patch('app.calculator.Path.exists', return_value=True)
def test_load_history(mock_exists, mock_read_csv, calculator):
    # Mock CSV data to match the expected format in from_dict
    mock_read_csv.return_value = pd.DataFrame({
        'operation': ['Addition'],
        'operand1': ['2'],
        'operand2': ['3'],
        'result': ['5'],
        'timestamp': [datetime.datetime.now().isoformat()]
    })
    
    # Test the load_history functionality
    try:
        calculator.load_history()
        # Verify history length after loading
        assert len(calculator.history) == 1
        # Verify the loaded values
        assert calculator.history[0].operation == "Addition"
        assert calculator.history[0].operand1 == Decimal("2")
        assert calculator.history[0].operand2 == Decimal("3")
        assert calculator.history[0].result == Decimal("5")
    except OperationError:
        pytest.fail("Loading history failed due to OperationError")
        
            
# Test Clearing History

def test_clear_history(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.clear_history()
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []

# Test REPL Commands (using patches for input/output handling)

@patch('builtins.input', side_effect=['exit'])
@patch('builtins.print')
def test_calculator_repl_exit(mock_print, mock_input):
    with patch('app.calculator.Calculator.save_history') as mock_save_history:
        calculator_repl()
        mock_save_history.assert_called_once()
        mock_print.assert_any_call("History saved successfully.")
        mock_print.assert_any_call("Goodbye!")

@patch('builtins.input', side_effect=['help', 'exit'])
@patch('builtins.print')
def test_calculator_repl_help(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("\nAvailable commands:")

@patch('builtins.input', side_effect=['add', '2', '3', 'exit'])
@patch('builtins.print')
def test_calculator_repl_addition(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("\nResult: 5")
def test_notify_observers(calculator):
    """Test that all registered observers are notified."""
    observer1 = Mock()
    observer2 = Mock()

    calculator.add_observer(observer1)
    calculator.add_observer(observer2)

    calculation = Mock()

    calculator.notify_observers(calculation)

    observer1.update.assert_called_once_with(calculation)
    observer2.update.assert_called_once_with(calculation)


def test_perform_operation_trims_history(calculator):
    """Test that history does not exceed the configured maximum size."""
    calculator.config.max_history_size = 1
    calculator.set_operation(OperationFactory.create_operation("add"))

    calculator.perform_operation(1, 2)
    calculator.perform_operation(3, 4)

    assert len(calculator.history) == 1
    assert calculator.history[0].operand1 == Decimal("3")
    assert calculator.history[0].operand2 == Decimal("4")


def test_perform_operation_unexpected_exception(calculator):
    """Test conversion of unexpected operation errors to OperationError."""
    operation = Mock()
    operation.execute.side_effect = RuntimeError("operation exploded")

    calculator.set_operation(operation)

    with pytest.raises(
        OperationError,
        match="Operation failed: operation exploded"
    ):
        calculator.perform_operation(2, 3)


def test_save_empty_history(calculator):
    """Test saving when calculation history is empty."""
    calculator.history = []

    with patch("app.calculator.pd.DataFrame.to_csv") as mock_to_csv:
        calculator.save_history()

    mock_to_csv.assert_called_once()


def test_save_history_failure(calculator):
    """Test error handling when history cannot be saved."""
    calculator.set_operation(OperationFactory.create_operation("add"))
    calculator.perform_operation(2, 3)

    with patch(
        "app.calculator.pd.DataFrame.to_csv",
        side_effect=OSError("write failed"),
    ):
        with pytest.raises(
            OperationError,
            match="Failed to save history: write failed",
        ):
            calculator.save_history()







def test_load_empty_history_file(calculator):
    """Test loading an existing but empty history CSV."""
    with patch(
        "app.calculator.Path.exists",
        return_value=True,
    ), patch(
        "app.calculator.pd.read_csv",
        return_value=pd.DataFrame(),
    ):
        calculator.load_history()

    assert calculator.history == []


def test_load_history_file_does_not_exist(calculator):
    """Test loading history when no history file exists."""
    calculator.history = []

    with patch(
        "app.calculator.Path.exists",
        return_value=False,
    ):
        calculator.load_history()

    assert calculator.history == []


def test_load_history_failure(calculator):
    """Test error handling when reading history fails."""
    with patch(
        "app.calculator.Path.exists",
        return_value=True,
    ), patch(
        "app.calculator.pd.read_csv",
        side_effect=OSError("read failed"),
    ):
        with pytest.raises(
            OperationError,
            match="Failed to load history: read failed",
        ):
            calculator.load_history()


def test_get_history_dataframe(calculator):
    """Test conversion of calculation history to a pandas DataFrame."""
    calculator.set_operation(OperationFactory.create_operation("add"))
    calculator.perform_operation(2, 3)

    dataframe = calculator.get_history_dataframe()

    assert isinstance(dataframe, pd.DataFrame)
    assert len(dataframe) == 1
    assert dataframe.iloc[0]["operation"] == "Addition"
    assert dataframe.iloc[0]["operand1"] == "2"
    assert dataframe.iloc[0]["operand2"] == "3"
    assert dataframe.iloc[0]["result"] == "5"


def test_show_history(calculator):
    """Test formatted calculation history."""
    calculator.set_operation(OperationFactory.create_operation("add"))
    calculator.perform_operation(2, 3)

    history = calculator.show_history()

    assert history == ["Addition(2, 3) = 5"]


def test_undo_when_stack_empty(calculator):
    """Test undo when there is nothing to undo."""
    assert calculator.undo() is False


def test_redo_when_stack_empty(calculator):
    """Test redo when there is nothing to redo."""
    assert calculator.redo() is False


def test_calculator_default_configuration():
    """Test Calculator creates a default configuration when none is supplied."""
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        with patch("app.calculator.Path") as mock_path, \
             patch("app.calculator.CalculatorConfig") as mock_config_class:

            mock_path.return_value.parent.parent = temp_path

            mock_config = Mock()
            mock_config.log_dir = temp_path / "logs"
            mock_config.log_file = temp_path / "logs/calculator.log"
            mock_config.history_dir = temp_path / "history"
            mock_config.history_file = temp_path / "history/calculator_history.csv"

            mock_config_class.return_value = mock_config

            calculator = Calculator()

            mock_config_class.assert_called_once_with(base_dir=temp_path)
            mock_config.validate.assert_called_once()
            assert calculator.config is mock_config


def test_calculator_initialization_handles_load_failure():
    """Test initialization continues when history loading fails."""
    with TemporaryDirectory() as temp_dir:
        config = CalculatorConfig(base_dir=Path(temp_dir))

        with patch.object(
            Calculator,
            "load_history",
            side_effect=OperationError("load failed"),
        ), patch(
            "app.calculator.logging.warning"
        ) as warning_mock:

            calculator = Calculator(config=config)

            warning_mock.assert_called_once_with(
                "Could not load existing history: load failed"
            )
            assert calculator.history == []


def test_setup_logging_failure(calculator, capsys):
    """Test that logging setup errors are re-raised."""
    with patch(
        "app.calculator.logging.basicConfig",
        side_effect=OSError("logging failed"),
    ):
        with pytest.raises(OSError, match="logging failed"):
            calculator._setup_logging()

    assert "Error setting up logging: logging failed" in capsys.readouterr().out