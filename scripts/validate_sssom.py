import sys
from sssom.cli import validate

if __name__ == "__main__":
    for file in sys.argv[1:]:
        print(f"Validating {file}...")
        validate([file])
