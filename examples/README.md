# BluePyll Examples

This directory contains example scripts demonstrating how to use BluePyll effectively.

## Available Examples

### `logging_example.py`

Demonstrates proper logging configuration and best practices for BluePyll usage.

**Features:**

- Basic usage examples with different logging levels
- Error handling with custom exceptions
- Production-ready logging configuration
- Third-party library logging management

**Usage:**

```bash
# Run with debug logging
python examples/logging_example.py

# Or configure logging in your own script
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Running Examples

1. Ensure BluePyll is installed:
   ```bash
   uv add bluepyll
   ```

2. Run examples:
   ```bash
   cd examples/
   python logging_example.py
   ```

## Logging Best Practices

- **DEBUG**: Use during development for detailed internal operations
- **INFO**: Use for normal operation and state changes
- **WARNING**: Use for recoverable issues and deprecated features
- **ERROR**: Use for failed operations and exceptions
- **CRITICAL**: Use for system-level failures

Configure logging levels for third-party libraries:

```python
import logging
logging.getLogger('easyocr').setLevel(logging.WARNING)
logging.getLogger('PIL').setLevel(logging.WARNING)
```