#!/usr/bin/env python3
"""
Core validation script for Dual-RAG-Evaluator
Tests core functionality without requiring PyQt5, python-docx, or external services
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_settings():
    """Test settings configuration"""
    print("\n" + "="*70)
    print("TEST 1: Settings Configuration")
    print("="*70)
    try:
        from config.settings import Settings, get_settings
        
        settings = get_settings()
        print(f"✅ Settings class initialized via get_settings()")
        print(f"   APP_NAME: {settings.APP_NAME}")
        print(f"   APP_VERSION: {settings.APP_VERSION}")
        print(f"   DEBUG: {settings.DEBUG}")
        print(f"   CHUNK_SIZE: {settings.CHUNK_SIZE}")
        print(f"   TOP_K: {settings.TOP_K}")
        print(f"   MAX_FILE_SIZE_MB: {settings.MAX_FILE_SIZE_MB}")
        
        # Test singleton
        settings2 = get_settings()
        assert settings is settings2, "Singleton pattern failed"
        print(f"✅ Singleton pattern works")
        
        # Test to_dict
        config_dict = settings.to_dict()
        assert len(config_dict) > 30, f"Expected 30+ config options, got {len(config_dict)}"
        print(f"✅ Settings.to_dict() returns {len(config_dict)} options")
        
        return True
    except Exception as e:
        print(f"❌ Settings test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_core_modules():
    """Test core module structure"""
    print("\n" + "="*70)
    print("TEST 2: Core Module Structure")
    print("="*70)
    try:
        # Test imports without actually using external services
        from core.doc_processor import DocumentProcessor
        print("✅ DocumentProcessor imported")
        
        # Check basic attributes
        assert hasattr(DocumentProcessor, 'chunk_text'), "chunk_text method missing"
        assert hasattr(DocumentProcessor, 'embed_chunks'), "embed_chunks method missing"
        assert hasattr(DocumentProcessor, 'process_text'), "process_text method missing"
        print("✅ DocumentProcessor has expected methods")
        
        try:
            from core.baseline_retriever import BaselineRetriever
            print("✅ BaselineRetriever imported")
        except ImportError as e:
            if "chromadb" in str(e).lower():
                print("⚠️  BaselineRetriever requires chromadb (not critical)")
            else:
                raise
        
        try:
            from core.evaluator import DualRAGEvaluator
            print("✅ DualRAGEvaluator imported")
        except ImportError as e:
            if "chromadb" in str(e).lower() or "resonance" in str(e).lower():
                print("⚠️  DualRAGEvaluator requires optional dependencies")
            else:
                raise
        
        from core.wave_mapper import WaveMapper
        print("✅ WaveMapper imported")
        
        from core.resonance_client import MockResonanceDBClient
        print("✅ MockResonanceDBClient imported")
        
        return True
    except Exception as e:
        print(f"❌ Core modules test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_utils():
    """Test utility modules - basic structure"""
    print("\n" + "="*70)
    print("TEST 3: Utility Modules")
    print("="*70)
    try:
        # Logger should work without external deps
        from utils.logger import configure_logging, get_app_logger
        configure_logging()
        logger = get_app_logger()
        print("✅ Logger module works")
        logger.info("Logging system initialized successfully")
        
        # Test file_handler basic structure (without docx dependency)
        from utils.file_handler import DocumentHandler
        handler = DocumentHandler()
        assert hasattr(handler, 'validate_file'), "validate_file method missing"
        assert hasattr(handler, 'is_supported_format'), "is_supported_format method missing"
        print("✅ DocumentHandler class loaded (methods present)")
        
        # Test that supported formats are defined
        print(f"   Supported formats: {handler.SUPPORTED_FORMATS}")
        
        # Test export module structure
        from utils.export import ResultExporter
        exporter = ResultExporter()
        assert hasattr(exporter, 'export_json'), "export_json method missing"
        assert hasattr(exporter, 'export_csv'), "export_csv method missing"
        assert hasattr(exporter, 'export_pdf'), "export_pdf method missing"
        assert hasattr(exporter, 'export_html'), "export_html method missing"
        print("✅ ResultExporter class loaded (export methods present)")
        
        return True
    except Exception as e:
        print(f"❌ Utils test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_file_structure():
    """Verify all expected files exist"""
    print("\n" + "="*70)
    print("TEST 4: File Structure Validation")
    print("="*70)
    
    base_path = Path(__file__).parent
    required_files = [
        "src/__init__.py",
        "src/config/__init__.py",
        "src/config/settings.py",
        "src/core/__init__.py",
        "src/core/doc_processor.py",
        "src/utils/__init__.py",
        "src/utils/logger.py",
        "src/utils/file_handler.py",
        "src/utils/export.py",
        "pyproject.toml",
        "setup.py",
        "requirements.txt",
        "Dockerfile",
        "README.md",
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - NOT FOUND")
            all_exist = False
    
    return all_exist


def test_directory_structure():
    """Verify directory structure"""
    print("\n" + "="*70)
    print("TEST 5: Directory Structure")
    print("="*70)
    
    base_path = Path(__file__).parent
    required_dirs = [
        "src", "src/config", "src/core", "src/ui", "src/utils",
        "tests", "tests/unit", "tests/integration",
        "data", "data/documents", "data/embeddings", "data/cache",
        "results", "docs", "config"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        full_path = base_path / dir_path
        if full_path.is_dir():
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ - NOT FOUND")
            all_exist = False
    
    return all_exist


def test_syntax():
    """Check Python syntax of main modules"""
    print("\n" + "="*70)
    print("TEST 6: Python Syntax Validation")
    print("="*70)
    
    import ast
    import glob
    
    base_path = Path(__file__).parent
    python_files = list(base_path.glob("src/**/*.py"))
    
    syntax_ok = True
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                ast.parse(f.read())
            print(f"✅ {py_file.relative_to(base_path)}")
        except SyntaxError as e:
            print(f"❌ {py_file.relative_to(base_path)}: {e}")
            syntax_ok = False
    
    return syntax_ok


def main():
    """Run all validation tests"""
    print("\n" + "="*70)
    print("DUAL-RAG-EVALUATOR CORE VALIDATION".center(70))
    print("="*70)
    
    results = {
        "Settings Configuration": test_settings(),
        "Core Module Structure": test_core_modules(),
        "Utility Modules": test_utils(),
        "File Structure": test_file_structure(),
        "Directory Structure": test_directory_structure(),
        "Python Syntax": test_syntax(),
    }
    
    print("\n" + "="*70)
    print("VALIDATION SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} - {test_name}")
    
    print("="*70)
    print(f"TOTAL: {passed}/{total} validation groups passed")
    print("="*70)
    
    if passed == total:
        print("\n🎉 ALL VALIDATIONS PASSED! Core implementation is solid.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} validation(s) failed. Review above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
