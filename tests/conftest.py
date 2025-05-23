import sys
print("PYTHON sys.path:", sys.path)
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
print("PYTHON sys.path AFTER insert:", sys.path)
