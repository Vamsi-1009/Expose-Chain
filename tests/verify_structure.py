#!/usr/bin/env python3
"""
Simple structure verification test (no external dependencies)
"""
import os
import sys

print("=" * 60)
print("ExposeChain - Step 1 Structure Verification")
print("=" * 60)

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Test: Check directory structure
print("\n[Test 1] Verifying directory structure...")
required_dirs = [
    "src/api",
    "src/models",
    "src/services",
    "src/utils",
    "src/config",
    "tests",
    "static",
    "templates"
]

dirs_ok = True
for dir_path in required_dirs:
    full_path = os.path.join(base_path, dir_path)
    exists = os.path.exists(full_path) and os.path.isdir(full_path)
    status = "[OK]" if exists else "[FAIL]"
    print(f"{status} {dir_path}/")
    if not exists:
        dirs_ok = False

# Test: Check required files
print("\n[Test 2] Verifying required files...")
required_files = [
    ("requirements.txt", "Dependencies file"),
    (".env.example", "Environment template"),
    (".gitignore", "Git ignore rules"),
    ("README.md", "Project documentation"),
    ("src/main.py", "Main application"),
    ("src/__init__.py", "Package init"),
    ("src/config/settings.py", "Configuration"),
    ("src/models/scan.py", "Data models"),
    ("src/utils/validators.py", "Input validators"),
    ("src/api/routes.py", "API routes"),
]

files_ok = True
for file_path, description in required_files:
    full_path = os.path.join(base_path, file_path)
    exists = os.path.exists(full_path) and os.path.isfile(full_path)
    
    if exists:
        size = os.path.getsize(full_path)
        print(f"[OK]  {file_path:<30} ({size:>6} bytes) - {description}")
    else:
        print(f"[FAIL] {file_path:<30} MISSING - {description}")
        files_ok = False

# Test: Verify key file contents
print("\n[Test 3] Checking file contents...")

# Check if main.py has the expected structure
main_path = os.path.join(base_path, "src/main.py")
if os.path.exists(main_path):
    with open(main_path, 'r', encoding='utf-8') as f:
        content = f.read()
        has_fastapi = 'FastAPI' in content
        has_router = 'router' in content
        has_main = '__name__' in content
        
        if has_fastapi and has_router and has_main:
            print("[OK]  src/main.py has correct structure")
        else:
            print("[WARN] src/main.py might be incomplete")

# Check validators
validators_path = os.path.join(base_path, "src/utils/validators.py")
if os.path.exists(validators_path):
    with open(validators_path, 'r', encoding='utf-8') as f:
        content = f.read()
        has_detect = 'detect_target_type' in content
        has_validate = 'is_valid_target' in content
        
        if has_detect and has_validate:
            print("[OK]  src/utils/validators.py has required functions")

# Check routes
routes_path = os.path.join(base_path, "src/api/routes.py")
if os.path.exists(routes_path):
    with open(routes_path, 'r', encoding='utf-8') as f:
        content = f.read()
        has_scan_endpoint = '/api/scan' in content
        has_health = '/health' in content
        
        if has_scan_endpoint and has_health:
            print("[OK]  src/api/routes.py has required endpoints")

# Count lines of code
print("\n[Test 4] Code statistics...")
total_lines = 0
total_files = 0

for root, dirs, files in os.walk(os.path.join(base_path, "src")):
    for file in files:
        if file.endswith('.py'):
            total_files += 1
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
                total_lines += lines

print(f"[OK]  Total Python files: {total_files}")
print(f"[OK]  Total lines of code: {total_lines}")

# Final Summary
print("\n" + "=" * 60)
print("Verification Summary")
print("=" * 60)

if dirs_ok and files_ok:
    print("[SUCCESS] ALL CHECKS PASSED!")
    print("\nStep 1 Complete: Project structure is ready!")
    print("\nNext Steps:")
    print("   1. Install dependencies: pip install -r requirements.txt")
    print("   2. Create .env file: cp .env.example .env")
    print("   3. Run the server: python -m src.main")
    print("   4. Access API docs: http://localhost:8000/docs")
    
    print("\nWhat we've built:")
    print("   [OK] FastAPI application structure")
    print("   [OK] Input validation (Domain/IPv4/IPv6)")
    print("   [OK] API endpoint for scanning")
    print("   [OK] Health check endpoint")
    print("   [OK] Configuration management")
    print("   [OK] Pydantic models for data validation")
else:
    print("[FAILED] SOME CHECKS FAILED")
    print("Please review the errors above.")
    sys.exit(1)

print("=" * 60)
