"""Nox sessions for ReefConnect project automation."""

import nox

# Default to uv for faster environment creation
nox.options.default_venv_backend = "uv|venv"

SUPPORTED_PYTHON_VERSIONS = ["3.11", "3.12"]

# Default sessions when running just 'nox'
nox.options.sessions = ["lint", "test"]


@nox.session(python=SUPPORTED_PYTHON_VERSIONS)
def test(session):
    """Run pytest tests for the backend."""
    session.chdir("backend")

    # Install dependencies (adjust based on your backend structure)
    session.install("-r", "requirements.txt")
    session.install("pytest", "pytest-cov")

    # Filter out our custom args
    pytest_args = []
    for arg in session.posargs:
        if arg == "--install":
            continue  # Skip our custom arg
        pytest_args.append(arg)

    # Run tests with coverage
    session.run(
        "pytest",
        "--cov=.",
        "--cov-report=term-missing",
        "--cov-report=html",
        *pytest_args
    )


@nox.session(python=SUPPORTED_PYTHON_VERSIONS[0])
def lint(session):
    """Run ruff linting (check only, no fixes)."""
    session.install("ruff==0.9.9")

    # Check formatting
    session.run("ruff", "format", "--check", "backend/")

    # Run linter
    session.run("ruff", "check", "backend/")


@nox.session(python=SUPPORTED_PYTHON_VERSIONS[0])
def fix(session):
    """Run ruff with auto-fix."""
    session.install("ruff==0.9.9")

    # Format code
    session.run("ruff", "format", "backend/")

    # Fix linting issues
    session.run("ruff", "check", "--fix", "backend/")


@nox.session(python=SUPPORTED_PYTHON_VERSIONS[0])
def type_check(session):
    """Run mypy type checking."""
    session.chdir("backend")
    session.install("mypy")
    session.run("mypy", ".")


@nox.session(python=False)
def frontend_test(session):
    """Run frontend tests with npm."""
    session.chdir("frontend")
    session.run("npm", "test", external=True)


@nox.session(python=False)
def frontend_build(session):
    """Build the frontend."""
    session.chdir("frontend")
    session.run("npm", "run", "build", external=True)
