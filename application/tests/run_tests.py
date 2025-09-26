#!/usr/bin/env python3
"""
Test runner script for Currency Converter application
Supports multiple test execution modes and reporting options
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and return the result"""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    return result.returncode == 0


def setup_test_environment():
    """Setup the test environment"""
    test_dir = Path(__file__).parent
    
    print("Setting up test environment...")
    
    # Install test dependencies
    requirements_file = test_dir / "requirements.txt"
    if requirements_file.exists():
        cmd = [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)]
        if not run_command(cmd):
            print("Failed to install test dependencies", file=sys.stderr)
            return False
    
    return True


def run_unit_tests(coverage=False, html_report=False, verbose=False):
    """Run unit tests"""
    print("\n" + "="*50)
    print("RUNNING UNIT TESTS")
    print("="*50)
    
    test_dir = Path(__file__).parent
    cmd = [sys.executable, "-m", "pytest"]
    
    # Add test markers
    cmd.extend(["-m", "unit"])
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    
    # Add coverage if requested
    if coverage:
        cmd.extend(["--cov=../backend", "--cov-report=term-missing"])
        if html_report:
            cmd.extend(["--cov-report=html:htmlcov"])
    
    # Add HTML report if requested
    if html_report:
        cmd.extend(["--html=reports/unit_tests.html", "--self-contained-html"])
    
    # Run tests
    cmd.append(str(test_dir))
    
    return run_command(cmd, cwd=test_dir)


def run_integration_tests(verbose=False):
    """Run integration tests"""
    print("\n" + "="*50)
    print("RUNNING INTEGRATION TESTS")
    print("="*50)
    
    test_dir = Path(__file__).parent
    cmd = [sys.executable, "-m", "pytest"]
    
    # Add test markers
    cmd.extend(["-m", "integration"])
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    
    # Run tests
    cmd.append(str(test_dir))
    
    return run_command(cmd, cwd=test_dir)


def run_all_tests(coverage=False, html_report=False, verbose=False):
    """Run all tests"""
    print("\n" + "="*50)
    print("RUNNING ALL TESTS")
    print("="*50)
    
    test_dir = Path(__file__).parent
    cmd = [sys.executable, "-m", "pytest"]
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    
    # Add coverage if requested
    if coverage:
        cmd.extend(["--cov=../backend", "--cov-report=term-missing"])
        if html_report:
            cmd.extend(["--cov-report=html:htmlcov"])
    
    # Add HTML report if requested
    if html_report:
        cmd.extend(["--html=reports/all_tests.html", "--self-contained-html"])
    
    # Run tests
    cmd.append(str(test_dir))
    
    return run_command(cmd, cwd=test_dir)


def create_directories():
    """Create necessary directories for reports"""
    test_dir = Path(__file__).parent
    reports_dir = test_dir / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    htmlcov_dir = test_dir / "htmlcov"
    htmlcov_dir.mkdir(exist_ok=True)


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description="Currency Converter Test Runner")
    
    parser.add_argument("--setup", action="store_true",
                       help="Setup test environment (install dependencies)")
    parser.add_argument("--unit", action="store_true",
                       help="Run only unit tests")
    parser.add_argument("--integration", action="store_true",
                       help="Run only integration tests")
    parser.add_argument("--all", action="store_true", default=True,
                       help="Run all tests (default)")
    parser.add_argument("--coverage", action="store_true",
                       help="Generate coverage report")
    parser.add_argument("--html", action="store_true",
                       help="Generate HTML reports")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    parser.add_argument("--quick", action="store_true",
                       help="Quick test run (unit tests only, no reports)")
    
    args = parser.parse_args()
    
    # Create report directories
    create_directories()
    
    # Setup environment if requested
    if args.setup:
        if not setup_test_environment():
            sys.exit(1)
    
    success = True
    
    if args.quick:
        # Quick run - unit tests only
        success = run_unit_tests(coverage=False, html_report=False, verbose=args.verbose)
    elif args.unit:
        success = run_unit_tests(coverage=args.coverage, html_report=args.html, verbose=args.verbose)
    elif args.integration:
        success = run_integration_tests(verbose=args.verbose)
    else:
        # Run all tests
        success = run_all_tests(coverage=args.coverage, html_report=args.html, verbose=args.verbose)
    
    if success:
        print("\n" + "="*50)
        print("ALL TESTS PASSED! ✅")
        print("="*50)
        
        if args.html:
            print(f"\nHTML reports available in:")
            print(f"  - Test reports: {Path(__file__).parent}/reports/")
            if args.coverage:
                print(f"  - Coverage reports: {Path(__file__).parent}/htmlcov/")
    else:
        print("\n" + "="*50)
        print("SOME TESTS FAILED! ❌")
        print("="*50)
        sys.exit(1)


if __name__ == "__main__":
    main()