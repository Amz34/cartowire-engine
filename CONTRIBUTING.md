# Contributing to Atlas Maps Engine

We welcome contributions to the **Atlas Maps Engine** project. To ensure stability and corporate-level code quality, please adhere to the following guidelines.

## Development Workflow

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-org/atlas-maps-engine.git
   cd atlas-maps-engine
   ```

2. **Virtual Environment Setup**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e ".[dev]"
   ```

3. **Running Quality Checks & Tests**
   Before submitting pull requests, verify all unit tests and protocol parsers pass:
   ```bash
   pytest tests/ -v
   ```

## Commit Conventions

Follow the standard [Conventional Commits](https://www.conventionalcommits.org/) specification:
- `feat(...)`: New user-facing or protocol capabilities
- `fix(...)`: Bug fixes or resilience patches
- `docs(...)`: Documentation updates
- `test(...)`: Adding or refactoring test suites
