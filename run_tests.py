#!/usr/bin/env python3
"""
Comprehensive test runner for BluePyll.

This script runs all unit tests with coverage reporting and generates
detailed test reports.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list, description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"{'='*50}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False


def main():
    """Run comprehensive tests."""
    print("🚀 Starting BluePyll Test Suite")
    print("=" * 60)

    # Change to project directory
    project_dir = Path(__file__).parent

    try:
        import chdir
        chdir(project_dir)
    except ImportError:
        import os
        os.chdir(project_dir)

    success_count = 0
    total_tests = 0

    # Test 1: Install dependencies
    if run_command([sys.executable, "-m", "pip", "install", "-e", "."], "Install package in development mode"):
        success_count += 1
    total_tests += 1

    # Test 2: Install dev dependencies
    if run_command([sys.executable, "-m", "pip", "install", "pytest", "pytest-cov", "pytest-mock"],
                   "Install development dependencies"):
        success_count += 1
    total_tests += 1

    # Test 3: Run basic tests
    if run_command([sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
                   "Run unit tests"):
        success_count += 1
    total_tests += 1

    # Test 4: Run tests with coverage
    if run_command([sys.executable, "-m", "pytest", "tests/", "--cov=bluepyll", "--cov-report=term-missing",
                    "--cov-report=html:htmlcov", "--cov-fail-under=80"],
                   "Run tests with coverage"):
        success_count += 1
    total_tests += 1

    # Test 5: Run specific test modules
    test_modules = [
        "test_exceptions.py",
        "test_constants.py",
        "test_state_machine.py",
        "test_app.py",
        "test_utils.py",
        "test_ui.py",
        "test_controller.py"
    ]

    for module in test_modules:
        if run_command([sys.executable, "-m", "pytest", f"tests/{module}", "-v"],
                       f"Run {module} tests"):
            success_count += 1
        total_tests += 1

    # Test 6: Check code quality
    if run_command([sys.executable, "-m", "pytest", "tests/", "--flakes"],
                   "Run code quality checks"):
        success_count += 1
    total_tests += 1

    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests passed: {success_count}/{total_tests}")
    print(f"Success rate: {(success_count/total_tests)*100:.1f}%")

    if success_count == total_tests:
        print("🎉 All tests passed! BluePyll is ready for production.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
