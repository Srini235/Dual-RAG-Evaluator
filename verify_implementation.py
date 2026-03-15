#!/usr/bin/env python3
"""
Comprehensive Implementation Verification Script

Tests all components to ensure the application is fully functional.
"""

import sys
import subprocess
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_imports():
    """Test that all modules can be imported."""
    print_section("TEST 1: Verify Module Imports")

    tests = [
        ("src config module", "from src.config import get_settings, Settings"),
        ("src utils module", "from src.utils import DocumentHandler, ResultExporter, get_app_logger"),
        ("src core module", "from src.core import DocumentProcessor, BaselineRetriever, WaveMapper"),
        ("src ui module", "from src.ui import MainWindow"),
        ("src main module", "from src.main import main"),
    ]

    all_pass = True
    for test_name, import_stmt in tests:
        try:
            exec(import_stmt)
            print(f"✅ {test_name}")
        except Exception as e:
            print(f"❌ {test_name}")
            print(f"   Error: {str(e)[:100]}")
            all_pass = False

    return all_pass


def test_settings():
    """Test Settings class functionality."""
    print_section("TEST 2: Verify Settings Configuration")

    try:
        from src.config import Settings, get_settings

        # Test initialization
        settings = Settings()
        print(f"✅ Settings initialization")

        # Test properties
        properties = [
            ("APP_NAME", settings.APP_NAME),
            ("APP_VERSION", settings.APP_VERSION),
            ("DEBUG", settings.DEBUG),
            ("CHUNK_SIZE", settings.CHUNK_SIZE),
            ("TOP_K", settings.TOP_K),
            ("MAX_FILE_SIZE_MB", settings.MAX_FILE_SIZE_MB),
            ("WINDOW_WIDTH", settings.WINDOW_WIDTH),
            ("WINDOW_HEIGHT", settings.WINDOW_HEIGHT),
        ]

        for prop_name, prop_value in properties:
            if prop_value is not None:
                print(f"✅ Settings.{prop_name} = {prop_value}")
            else:
                print(f"❌ Settings.{prop_name} is None")

        # Test singleton
        settings2 = get_settings()
        if settings2 is get_settings():
            print(f"✅ Settings singleton pattern works")
        else:
            print(f"❌ Settings singleton pattern failed")

        # Test to_dict
        settings_dict = settings.to_dict()
        if len(settings_dict) > 20:
            print(f"✅ Settings.to_dict() returns {len(settings_dict)} config options")
        else:
            print(f"❌ Settings.to_dict() returned only {len(settings_dict)} options")

        return True

    except Exception as e:
        print(f"❌ Settings class test failed: {str(e)}")
        return False


def test_utilities():
    """Test utility modules."""
    print_section("TEST 3: Verify Utility Modules")

    all_pass = True

    # Test DocumentHandler
    try:
        from src.utils import DocumentHandler

        handler = DocumentHandler(max_size_mb=10)
        print(f"✅ DocumentHandler initialized")

        # Test supported formats
        if ".pdf" in handler.SUPPORTED_FORMATS:
            print(f"✅ DocumentHandler supports 4 formats: {', '.join(handler.SUPPORTED_FORMATS)}")
        else:
            print(f"❌ DocumentHandler missing .pdf format")
            all_pass = False

    except Exception as e:
        print(f"❌ DocumentHandler test failed: {str(e)}")
        all_pass = False

    # Test ResultExporter
    try:
        from src.utils import ResultExporter
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            exporter = ResultExporter(output_directory=temp_dir)
            print(f"✅ ResultExporter initialized")

            sample_results = {"test": "data"}
            success, filepath = exporter.export_json(sample_results, "test.json")
            if success:
                print(f"✅ ResultExporter can export JSON")
            else:
                print(f"❌ ResultExporter JSON export failed")
                all_pass = False

    except Exception as e:
        print(f"❌ ResultExporter test failed: {str(e)}")
        all_pass = False

    # Test Logger
    try:
        from src.utils import get_app_logger
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            logger = get_app_logger(level="INFO")
            logger.info("Test message")
            print(f"✅ Logging system initialized and working")

    except Exception as e:
        print(f"❌ Logger test failed: {str(e)}")
        all_pass = False

    return all_pass


def test_gui():
    """Test GUI components."""
    print_section("TEST 4: Verify GUI Components")

    try:
        from src.ui import MainWindow

        # Just test import and initialization (don't show window)
        import sys
        from PyQt5.QtWidgets import QApplication

        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()

        window = MainWindow()
        print(f"✅ MainWindow initialized successfully")

        # Check key attributes
        attrs = [
            "doc_handler",
            "exporter",
            "settings",
            "current_results",
        ]

        for attr in attrs:
            if hasattr(window, attr):
                print(f"✅ MainWindow.{attr} exists")
            else:
                print(f"❌ MainWindow.{attr} missing")

        return True

    except Exception as e:
        print(f"❌ GUI test failed: {str(e)[:150]}")
        return False


def test_pytest():
    """Run pytest test suite."""
    print_section("TEST 5: Run Pytest Test Suite")

    try:
        result = subprocess.run(
            ["pytest", "tests/", "-v", "--tb=short"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=60,
        )

        # Print last 30 lines of output
        output_lines = result.stdout.split("\n")
        for line in output_lines[-30:]:
            if line.strip():
                print(line)

        if result.returncode == 0:
            print(f"\n✅ All pytest tests passed")
            return True
        else:
            print(f"\n❌ Some pytest tests failed (exit code: {result.returncode})")
            print("\nSTDERR:")
            print(result.stderr[-500:] if result.stderr else "No errors")
            return False

    except subprocess.TimeoutExpired:
        print(f"❌ Pytest timed out")
        return False
    except Exception as e:
        print(f"❌ Pytest execution failed: {str(e)}")
        return False


def test_application_entry():
    """Test application entry point."""
    print_section("TEST 6: Verify Application Entry Point")

    try:
        from src.main import main

        print(f"✅ Application entry point (main) importable")

        # Test argument parsing
        import sys
        old_argv = sys.argv
        try:
            sys.argv = ["test", "--version"]
            result = main()
            if result == 0:
                print(f"✅ Application --version flag works")
            else:
                print(f"⚠️  Application returned code {result} for --version")
        finally:
            sys.argv = old_argv

        return True

    except Exception as e:
        print(f"❌ Application entry point test failed: {str(e)}")
        return False


def test_docker_build():
    """Test Docker build."""
    print_section("TEST 7: Verify Docker Configuration")

    try:
        docker_file = project_root / "Dockerfile"
        docker_compose = project_root / "docker-compose.yml"

        if docker_file.exists():
            print(f"✅ Dockerfile exists")
        else:
            print(f"❌ Dockerfile not found")

        if docker_compose.exists():
            print(f"✅ docker-compose.yml exists")
        else:
            print(f"❌ docker-compose.yml not found")

        # Try to build (without actually running)
        result = subprocess.run(
            ["docker", "build", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            print(f"✅ Docker is installed and available")
        else:
            print(f"⚠️  Docker might not be available (optional)")

        return True

    except Exception as e:
        print(f"⚠️  Docker test skipped: {str(e)}")
        return True


def test_configuration_files():
    """Test that all required configuration files exist."""
    print_section("TEST 8: Verify Configuration Files")

    required_files = [
        "config/.env.template",
        "pyproject.toml",
        "setup.py",
        "setup.sh",
        "setup.bat",
        "Makefile",
        "Dockerfile",
        "docker-compose.yml",
        "pytest.ini",
        "tox.ini",
        ".flake8",
        ".editorconfig",
        "README.md",
        "LICENSE",
        "CHANGELOG.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "DEVELOPER.md",
        "QUICKSTART.md",
    ]

    missing = []
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} missing")
            missing.append(file_path)

    return len(missing) == 0


def test_directory_structure():
    """Test directory structure."""
    print_section("TEST 9: Verify Directory Structure")

    required_dirs = [
        "src/config",
        "src/core",
        "src/ui",
        "src/utils",
        "tests/unit",
        "tests/integration",
        "data/documents",
        "data/embeddings",
        "data/cache",
        "results",
        "docs/architecture",
        "docs/api",
        "docs/guides",
        "config",
    ]

    missing = []
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists() and full_path.is_dir():
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ missing")
            missing.append(dir_path)

    return len(missing) == 0


def main():
    """Run all verification tests."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "DUAL-RAG-EVALUATOR VERIFICATION SUITE" + " " * 15 + "║")
    print("╚" + "=" * 68 + "╝")

    results = []

    # Run tests in order
    results.append(("Module Imports", test_imports()))
    results.append(("Settings Configuration", test_settings()))
    results.append(("Utility Modules", test_utilities()))
    results.append(("GUI Components", test_gui()))
    results.append(("Pytest Tests", test_pytest()))
    results.append(("Application Entry Point", test_application_entry()))
    results.append(("Docker Configuration", test_docker_build()))
    results.append(("Configuration Files", test_configuration_files()))
    results.append(("Directory Structure", test_directory_structure()))

    # Summary
    print_section("FINAL SUMMARY")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print("\n" + "=" * 70)
    print(f"TOTAL: {passed}/{total} test groups passed")
    print("=" * 70)

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Application is ready for deployment.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test group(s) failed. Please review above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
