# Module 5 - Enhanced Calculator Application

This project is an advanced command-line calculator application built in Python. It demonstrates object-oriented programming, software design patterns, persistent calculation history using pandas, environment-based configuration, exception handling, automated testing, and continuous integration with GitHub Actions.

## Features

The calculator supports the following mathematical operations:

- Addition
- Subtraction
- Multiplication
- Division
- Power
- Root

Additional functionality includes:

- Interactive REPL command-line interface
- Calculation history
- Undo and redo
- Clear history
- Save and load history
- CSV persistence using pandas
- Automatic history saving
- Logging
- Environment-variable configuration
- Input validation
- Custom exception handling

## Design Patterns

The application demonstrates several software design patterns, including:

- Strategy Pattern
- Factory Pattern
- Observer Pattern
- Memento Pattern
- Facade Pattern

These patterns separate calculation behavior, operation creation, history management, notifications, and the calculator interface into modular components.

## Project Structure

```text
module5_is601/
├── app/
│   ├── calculator.py
│   ├── calculation.py
│   ├── calculator_config.py
│   ├── calculator_memento.py
│   ├── calculator_repl.py
│   ├── exceptions.py
│   ├── history.py
│   ├── input_validators.py
│   └── operations.py
├── tests/
│   ├── test_calculations.py
│   ├── test_calculator.py
│   ├── test_calculator_config.py
│   ├── test_calculator_memento.py
│   ├── test_calculator_repl.py
│   ├── test_exceptions.py
│   ├── test_history.py
│   ├── test_input_validators.py
│   └── test_operations.py
├── .github/
│   └── workflows/
│       └── tests.yml
├── main.py
├── pytest.ini
├── requirements.txt
└── readme.md
```

## Requirements

- Python 3.12 recommended
- pip
- Git

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd module5_is601
```

Create a virtual environment:

```bash
python3.12 -m venv venv
```

Activate it on macOS/Linux:

```bash
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Environment Configuration

The application supports configuration through environment variables and a local `.env` file.

Example:

```env
CALCULATOR_MAX_HISTORY_SIZE=100
CALCULATOR_AUTO_SAVE=true
CALCULATOR_PRECISION=10
CALCULATOR_MAX_INPUT_VALUE=1e999
CALCULATOR_DEFAULT_ENCODING=utf-8
```

Optional path-related settings include:

```env
CALCULATOR_BASE_DIR=/path/to/project
CALCULATOR_LOG_DIR=/path/to/logs
CALCULATOR_HISTORY_DIR=/path/to/history
CALCULATOR_HISTORY_FILE=/path/to/calculator_history.csv
CALCULATOR_LOG_FILE=/path/to/calculator.log
```

The `.env` file is excluded from Git to prevent local configuration from being committed.

## Running the Calculator

Start the application with:

```bash
python main.py
```

The calculator starts an interactive REPL:

```text
Calculator started. Type 'help' for commands.
```

## Calculator Commands

The following commands are supported:

| Command | Description |
| --- | --- |
| `add` | Add two numbers |
| `subtract` | Subtract two numbers |
| `multiply` | Multiply two numbers |
| `divide` | Divide two numbers |
| `power` | Raise a number to a power |
| `root` | Calculate a root |
| `history` | Display calculation history |
| `clear` | Clear calculation history |
| `undo` | Undo the last calculation |
| `redo` | Redo the last undone calculation |
| `save` | Save calculation history |
| `load` | Load calculation history |
| `help` | Display available commands |
| `exit` | Save history and exit |

When performing a calculation, enter `cancel` instead of a number to cancel the operation.

## Calculation History

Calculation history is managed using pandas and persisted in CSV format. The application can automatically save history and reload saved calculations.

The Observer pattern is used for logging and automatic saving, while the Memento pattern supports undo and redo functionality.

## Error Handling and Validation

The application provides validation and custom exception handling for invalid input and calculation errors. Examples include:

- Invalid numeric input
- Unsupported operations
- Division by zero
- Invalid roots
- Invalid configuration values

The project demonstrates both LBYL (Look Before You Leap) and EAFP (Easier to Ask Forgiveness than Permission) approaches to error handling.

## Testing

The project uses pytest for automated testing.

Run all tests:

```bash
pytest
```

Run the complete test suite with line and branch coverage:

```bash
pytest --cov=app --cov-branch --cov-report=term-missing --cov-fail-under=100 tests/
```

The project currently contains 156 automated tests and achieves 100% line and branch coverage.

To generate an HTML coverage report:

```bash
pytest --cov=app --cov-branch --cov-report=html tests/
```

Then open the generated `htmlcov/index.html` file.

## Continuous Integration

GitHub Actions automatically runs the test suite whenever code is pushed to the `main` branch or a pull request targets `main`.

The CI workflow:

1. Checks out the repository.
2. Sets up Python 3.12.
3. Installs project dependencies.
4. Runs the complete pytest suite.
5. Measures line and branch coverage.
6. Fails the build if total coverage falls below 100%.

The workflow configuration is located at:

```text
.github/workflows/tests.yml
```

## Technologies Used

- Python 3.12
- pandas
- python-dotenv
- pytest
- pytest-cov
- Git
- GitHub Actions

## Author

Navid Islam

## Course Assignment

Module 5: Enhanced Calculator Application with Advanced Design Patterns and pandas.