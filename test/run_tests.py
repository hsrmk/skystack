import pytest
import sys
import os

if __name__ == '__main__':
    # Add the parent directory to sys.path to allow importing from skystack
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    # Run all tests in the test directory
    pytest.main([os.path.dirname(__file__)])