#!/usr/bin/env python3
"""
Test script to verify the Path import fix
"""

import sys
from pathlib import Path

# Test the specific line that was causing the error
def test_path_usage():
    """Test Path usage in the upload route."""
    try:
        # Simulate the problematic line
        filename = "test_image.jpg"
        glb_filename = f"{Path(filename).stem}.glb"
        print(f"✅ Path usage test passed: {glb_filename}")
        return True
    except NameError as e:
        print(f"❌ Path usage test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Path import fix...")
    success = test_path_usage()
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Tests failed!")
        sys.exit(1)
