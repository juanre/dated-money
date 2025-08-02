#!/usr/bin/env python3
"""
Test script to extract and run all code examples from README.md
"""

import os
import re
import sys
from pathlib import Path

# Set up test database for consistent results
os.environ["DMON_RATES_CACHE"] = str(Path(__file__).parent / "test" / "res")


def extract_code_blocks(readme_path):
    """Extract all Python code blocks from README."""
    with open(readme_path) as f:
        content = f.read()

    # Find all ```python blocks
    pattern = r"```python\n(.*?)\n```"
    code_blocks = re.findall(pattern, content, re.DOTALL)

    return code_blocks


def test_code_block(code, block_num):
    """Test a single code block."""
    print(f"\n{'='*60}")
    print(f"Testing code block {block_num}:")
    print(f"{'='*60}")
    print(code)
    print(f"{'-'*60}")

    try:
        # Add necessary imports if not present
        if "from dated_money" not in code and any(
            term in code for term in ["DM", "DatedMoney", "Currency"]
        ):
            code = "from dated_money import DM, DatedMoney, Currency\n\n" + code

        # Create a namespace for execution
        namespace = {}
        exec(code, namespace)
        print("✓ Code block executed successfully")
        return True
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {e}")
        return False


def main():
    """Main test runner."""
    readme_path = Path(__file__).parent / "README.md"

    if not readme_path.exists():
        print("ERROR: README.md not found")
        sys.exit(1)

    code_blocks = extract_code_blocks(readme_path)
    print(f"Found {len(code_blocks)} code blocks in README.md")

    # Test each code block
    passed = 0
    failed = 0

    for i, code in enumerate(code_blocks, 1):
        # Skip code blocks that are just type signatures or incomplete
        if "DM(base_currency, base_date=None)" in code and len(code.strip().split("\n")) == 1:
            print(f"\n{'='*60}")
            print(f"Skipping code block {i} (type signature only)")
            continue

        if (
            "DatedMoney(amount, currency, on_date=None)" in code
            and len(code.strip().split("\n")) == 1
        ):
            print(f"\n{'='*60}")
            print(f"Skipping code block {i} (type signature only)")
            continue

        if "# Old" in code or "# New" in code or "# Be aware" in code:
            # Skip migration guide examples
            print(f"\n{'='*60}")
            print(f"Skipping code block {i} (migration guide example)")
            continue

        if "dmon-rates" in code:
            # Skip CLI examples
            print(f"\n{'='*60}")
            print(f"Skipping code block {i} (CLI command)")
            continue

        if "json" in code and "conversion_rates" in code:
            # Skip JSON example
            print(f"\n{'='*60}")
            print(f"Skipping code block {i} (JSON structure example)")
            continue

        if test_code_block(code, i):
            passed += 1
        else:
            failed += 1

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY:")
    print(f"{'='*60}")
    print(f"Total code blocks: {len(code_blocks)}")
    print(f"Tested: {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed > 0:
        sys.exit(1)
    else:
        print("\n✓ All testable code blocks passed!")


if __name__ == "__main__":
    main()
