#!/usr/bin/env python3
"""
Script to run all tests in the tests folder.
"""

import subprocess
import sys
import os

def run_all_tests():
    """Run all tests in the tests folder using pytest."""
    try:
        # Change to the project root directory
        project_root = os.path.dirname(os.path.abspath(__file__))
        os.chdir(project_root)
        
        # Run pytest on the tests folder
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "-v",  # Verbose output
            "-s"   # Show print statements
        ], capture_output=False, text=True)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error running tests: {e}")
        return False

if __name__ == "__main__":
    print("Running all tests...")
    success = run_all_tests()
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1) 