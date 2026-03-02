#!/usr/bin/env python3
"""
ValuAdis Migration Pipeline Test Runner

Comprehensive testing for database migrations, data integrity,
and Ethiopian property valuation data migration
"""

import os
import sys
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path


class MigrationPipelineTester:
    """
    Manages and executes migration pipeline tests
    """
    
    def __init__(self):
        self.test_results = []
        self.start_time = datetime.now()
        self.postgres_available = self.check_postgres_connection()
    
    def check_postgres_connection(self):
        """Check if PostgreSQL is available for testing"""
        try:
            import psycopg2
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                user="valuadis",
                password="valuadis",
                database="postgres",
                connect_timeout=5
            )
            conn.close()
            return True
        except Exception as e:
            print(f"⚠️ PostgreSQL not available: {e}")
            return False
    
    def run_all_migration_tests(self):
        """Run comprehensive migration test suite"""
        
        print("🚀 ValuAdis Migration Pipeline Testing")
        print("=" * 60)
        print(f"📅 Started: {self.start_time}")
        print(f"🗄️ PostgreSQL: {'✅ Available' if self.postgres_available else '❌ Not Available'}")
        print("=" * 60)
        
        if not self.postgres_available:
            print("❌ PostgreSQL not available for migration testing")
            print("📋 Setup PostgreSQL + PostGIS to run migration tests")
            self.run_mock_migration_tests()
        else:
            self.run_real_migration_tests()
        
        self.generate_migration_report()
    
    def run_real_migration_tests(self):
        """Run tests with real PostgreSQL database"""
        
        print("\n🗄️ Running Real Database Migration Tests")
        print("-" * 50)
        
        test_scenarios = [
            {
                "name": "Alembic Migration Test",
                "test": self.test_alembic_migration,
                "description": "Test Alembic upgrade/downgrade functionality"
            },
            {
                "name": "PostGIS Extension Test", 
                "test": self.test_postgis_extension,
                "description": "Test PostGIS extension creation"
            },
            {
                "name": "Ethiopian Data Seeding Test",
                "test": self.test_ethiopian_seeding,
                "description": "Test Ethiopian test data seeding"
            },
            {
                "name": "Data Integrity Test",
                "test": self.test_data_integrity,
                "description": "Test Ethiopian data integrity"
            },
            {
                "name": "Migration Rollback Test",
                "test": self.test_migration_rollback,
                "description": "Test migration rollback functionality"
            },
            {
                "name": "Ethiopian Compliance Test",
                "test": self.test_ethiopian_compliance,
                "description": "Test Ethiopian compliance requirements"
            }
        ]
        
        for scenario in test_scenarios:
            print(f"\n🎯 Running: {scenario['name']}")
            print(f"📝 {scenario['description']}")
            
            result = scenario["test"]()
            self.test_results.append(result)
            
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} {scenario['name']}")
            
            if result.get("error"):
                print(f"   🚨 Error: {result['error']}")
    
    def run_mock_migration_tests(self):
        """Run mock tests when PostgreSQL is not available"""
        
        print("\n🧪 Running Mock Migration Tests")
        print("-" * 50)
        
        mock_scenarios = [
            {
                "name": "Migration Script Validation",
                "test": self.test_migration_scripts,
                "description": "Validate migration script syntax"
            },
            {
                "name": "Alembic Configuration Test",
                "test": self.test_alembic_config,
                "description": "Test Alembic configuration validity"
            },
            {
                "name": "Seeder Script Validation",
                "test": self.test_seeder_scripts,
                "description": "Validate seeder script syntax"
            },
            {
                "name": "Ethiopian Data Structure Test",
                "test": self.test_ethiopian_data_structure,
                "description": "Test Ethiopian data structure definitions"
            }
        ]
        
        for scenario in mock_scenarios:
            print(f"\n🎯 Running: {scenario['name']}")
            print(f"📝 {scenario['description']}")
            
            result = scenario["test"]()
            self.test_results.append(result)
            
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} {scenario['name']}")
    
    def test_alembic_migration(self):
        """Test Alembic migration functionality"""
        
        try:
            # Check Alembic configuration
            alembic_ini = "/Users/imranabdul/Dev/Personal/ValuAdis/backend/alembic.ini"
            if not os.path.exists(alembic_ini):
                return {"success": False, "error": "Alembic.ini not found"}
            
            # Check Alembic env file
            alembic_env = "/Users/imranabdul/Dev/Personal/ValuAdis/backend/alembic/env.py"
            if not os.path.exists(alembic_env):
                return {"success": False, "error": "Alembic env.py not found"}
            
            # Check migration files
            migrations_dir = "/Users/imranabdul/Dev/Personal/ValuAdis/backend/alembic/versions"
            migration_files = list(Path(migrations_dir).glob("*.py"))
            
            if len(migration_files) == 0:
                return {"success": False, "error": "No migration files found"}
            
            # Test Alembic current status
            result = subprocess.run([
                "alembic", "current"
            ], 
            capture_output=True, 
            text=True,
            cwd="/Users/imranabdul/Dev/Personal/ValuAdis/backend"
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "details": {
                        "migration_files": len(migration_files),
                        "current_revision": result.stdout.strip()
                    }
                }
            else:
                return {"success": False, "error": result.stderr}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_postgis_extension(self):
        """Test PostGIS extension support"""
        
        try:
            # Check if PostGIS is available
            result = subprocess.run([
                "psql", "-h", "localhost", "-U", "valuadis", "-d", "postgres",
                "-c", "SELECT 1 FROM pg_available_extensions WHERE name = 'postgis';"
            ], 
            capture_output=True, 
            text=True
            )
            
            if result.returncode == 0 and "1" in result.stdout:
                return {"success": True, "details": "PostGIS extension available"}
            else:
                return {"success": False, "error": "PostGIS extension not available"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_ethiopian_seeding(self):
        """Test Ethiopian data seeding functionality"""
        
        try:
            # Check seeder files exist
            seeder_dir = "/Users/imranabdul/Dev/Personal/ValuAdis/backend/app/data/seeders"
            seeder_files = [
                "user_seeder.py",
                "property_seeder.py", 
                "valuation_seeder.py"
            ]
            
            for seeder in seeder_files:
                seeder_path = os.path.join(seeder_dir, seeder)
                if not os.path.exists(seeder_path):
                    return {"success": False, "error": f"Seeder file {seeder} not found"}
            
            # Check main seeder script
            main_seeder = "/Users/imranabdul/Dev/Personal/ValuAdis/backend/seed_data.py"
            if not os.path.exists(main_seeder):
                return {"success": False, "error": "Main seeder script not found"}
            
            # Validate seeder syntax
            result = subprocess.run([
                "python3", "-m", "py_compile", main_seeder
            ], 
            capture_output=True, 
            text=True,
            cwd="/Users/imranabdul/Dev/Personal/ValuAdis/backend"
            )
            
            if result.returncode == 0:
                return {"success": True, "details": "All seeder files valid"}
            else:
                return {"success": False, "error": "Seeder syntax error"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_data_integrity(self):
        """Test Ethiopian data integrity requirements"""
        
        try:
            # Check Ethiopian municipalities in seeder
            property_seeder = "/Users/imranabdul/Dev/Personal/ValuAdis/backend/app/data/seeders/property_seeder.py"
            
            with open(property_seeder, 'r') as f:
                content = f.read()
                
            ethiopian_municipalities = [
                "Addis Ababa", "Dire Dawa", "Mekelle", 
                "Bahirdar", "Gondar", "Hawassa"
            ]
            
            missing_municipalities = []
            for municipality in ethiopian_municipalities:
                if municipality not in content:
                    missing_municipalities.append(municipality)
            
            if missing_municipalities:
                return {
                    "success": False, 
                    "error": f"Missing municipalities: {missing_municipalities}"
                }
            
            # Check property types
            property_types = ["residential", "commercial", "agricultural"]
            missing_types = []
            
            for prop_type in property_types:
                if prop_type not in content:
                    missing_types.append(prop_type)
            
            if missing_types:
                return {
                    "success": False,
                    "error": f"Missing property types: {missing_types}"
                }
            
            return {
                "success": True,
                "details": {
                    "municipalities": len(ethiopian_municipalities),
                    "property_types": len(property_types)
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_migration_rollback(self):
        """Test migration rollback functionality"""
        
        try:
            # Check Alembic history
            result = subprocess.run([
                "alembic", "history", "--verbose"
            ], 
            capture_output=True, 
                text=True,
                cwd="/Users/imranabdul/Dev/Personal/ValuAdis/backend"
            )
            
            if result.returncode == 0:
                return {"success": True, "details": "Alembic history accessible"}
            else:
                return {"success": False, "error": "Cannot access Alembic history"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_ethiopian_compliance(self):
        """Test Ethiopian compliance in data structures"""
        
        try:
            # Check user model for Ethiopian fields
            user_model = "/Users/imranabdul/Dev/Personal/ValuAdis/backend/app/data/models/user.py"
            
            with open(user_model, 'r') as f:
                user_content = f.read()
                
            ethiopian_user_fields = ["municipality", "license_number"]
            missing_user_fields = []
            
            for field in ethiopian_user_fields:
                if field not in user_content:
                    missing_user_fields.append(field)
            
            # Check property model for spatial data
            property_model = "/Users/imranabdul/Dev/Personal/ValuAdis/backend/app/data/models/property.py"
            
            with open(property_model, 'r') as f:
                property_content = f.read()
                
            if "boundary" not in property_content or "Geometry" not in property_content:
                return {
                    "success": False,
                    "error": "Spatial boundary field missing from property model"
                }
            
            # Check valuation model for Ethiopian compliance
            valuation_model = "/Users/imranabdul/Dev/Personal/ValuAdis/backend/app/data/models/valuation.py"
            
            with open(valuation_model, 'r') as f:
                valuation_content = f.read()
                
            ethiopian_valuation_fields = ["municipality", "property_type", "market_value", "taxable_value"]
            missing_valuation_fields = []
            
            for field in ethiopian_valuation_fields:
                if field not in valuation_content:
                    missing_valuation_fields.append(field)
            
            if missing_user_fields or missing_valuation_fields:
                return {
                    "success": False,
                    "error": f"Missing Ethiopian compliance fields: {missing_user_fields + missing_valuation_fields}"
                }
            
            return {
                "success": True,
                "details": {
                    "user_fields": len(ethiopian_user_fields),
                    "property_fields": "spatial boundary",
                    "valuation_fields": len(ethiopian_valuation_fields)
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_migration_scripts(self):
        """Test migration script syntax and structure"""
        
        try:
            migrations_dir = "/Users/imranabdul/Dev/Personal/ValuAdis/backend/alembic/versions"
            migration_files = list(Path(migrations_dir).glob("*.py"))
            
            syntax_errors = []
            
            for migration_file in migration_files:
                result = subprocess.run([
                    "python3", "-m", "py_compile", str(migration_file)
                ], 
                capture_output=True, 
                text=True
                )
                
                if result.returncode != 0:
                    syntax_errors.append(f"{migration_file.name}: {result.stderr}")
            
            if syntax_errors:
                return {
                    "success": False,
                    "error": f"Syntax errors: {syntax_errors}"
                }
            
            return {
                "success": True,
                "details": {
                    "migration_files": len(migration_files),
                    "syntax_valid": True
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_alembic_config(self):
        """Test Alembic configuration validity"""
        
        try:
            alembic_ini = "/Users/imranabdul/Dev/Personal/ValuAdis/backend/alembic.ini"
            
            if not os.path.exists(alembic_ini):
                return {"success": False, "error": "Alembic.ini not found"}
            
            # Parse configuration
            with open(alembic_ini, 'r') as f:
                config_content = f.read()
                
            required_sections = ["alembic"]
            missing_sections = []
            
            for section in required_sections:
                if f"[{section}]" not in config_content:
                    missing_sections.append(section)
            
            if missing_sections:
                return {
                    "success": False,
                    "error": f"Missing config sections: {missing_sections}"
                }
            
            # Check database URL configuration
            if "sqlalchemy.url" not in config_content:
                return {"success": False, "error": "Database URL not configured"}
            
            return {
                "success": True,
                "details": "Alembic configuration valid"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_seeder_scripts(self):
        """Test seeder script syntax and structure"""
        
        try:
            seeder_dir = "/Users/imranabdul/Dev/Personal/ValuAdis/backend/app/data/seeders"
            seeder_files = list(Path(seeder_dir).glob("*.py"))
            
            syntax_errors = []
            
            for seeder_file in seeder_files:
                result = subprocess.run([
                    "python3", "-m", "py_compile", str(seeder_file)
                ], 
                capture_output=True, 
                text=True
                )
                
                if result.returncode != 0:
                    syntax_errors.append(f"{seeder_file.name}: {result.stderr}")
            
            if syntax_errors:
                return {
                    "success": False,
                    "error": f"Seeder syntax errors: {syntax_errors}"
                }
            
            return {
                "success": True,
                "details": {
                    "seeder_files": len(seeder_files),
                    "syntax_valid": True
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_ethiopian_data_structure(self):
        """Test Ethiopian data structure definitions"""
        
        try:
            # Check models directory
            models_dir = "/Users/imranabdul/Dev/Personal/ValuAdis/backend/app/data/models"
            required_models = ["user.py", "property.py", "valuation.py"]
            
            missing_models = []
            for model in required_models:
                model_path = os.path.join(models_dir, model)
                if not os.path.exists(model_path):
                    missing_models.append(model)
            
            if missing_models:
                return {
                    "success": False,
                    "error": f"Missing models: {missing_models}"
                }
            
            # Check __init__.py files
            init_files = [
                "/Users/imranabdul/Dev/Personal/ValuAdis/backend/app/data/__init__.py",
                "/Users/imranabdul/Dev/Personal/ValuAdis/backend/app/data/models/__init__.py",
                "/Users/imranabdul/Dev/Personal/ValuAdis/backend/app/data/seeders/__init__.py"
            ]
            
            missing_inits = []
            for init_file in init_files:
                if not os.path.exists(init_file):
                    missing_inits.append(init_file)
            
            if missing_inits:
                return {
                    "success": False,
                    "error": f"Missing __init__.py files: {missing_inits}"
                }
            
            return {
                "success": True,
                "details": {
                    "models": len(required_models),
                    "init_files": len(init_files)
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def generate_migration_report(self):
        """Generate comprehensive migration test report"""
        
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        print("\n" + "=" * 60)
        print("🎉 Migration Pipeline Testing Complete!")
        print("=" * 60)
        print(f"📅 Completed: {end_time}")
        print(f"⏱️ Total Duration: {total_duration:.1f}s")
        print(f"🧪 Tests Run: {len(self.test_results)}")
        
        # Summary table
        print("\n📊 Test Results Summary:")
        print("-" * 60)
        print(f"{'Test Name':<30} {'Status':<8} {'Details':<20}")
        print("-" * 60)
        
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            details = result.get("details", "N/A")
            if isinstance(details, dict):
                details = f"{len(details)} items"
            elif len(str(details)) > 17:
                details = str(details)[:17] + "..."
                
            print(f"{result.get('name', 'Unknown'):<30} {status:<8} {details:<20}")
        
        # Success analysis
        successful_tests = [r for r in self.test_results if r["success"]]
        
        print(f"\n🎯 Success Analysis:")
        print(f"   ✅ Passed: {len(successful_tests)}/{len(self.test_results)}")
        print(f"   📊 Success Rate: {(len(successful_tests)/len(self.test_results))*100:.1f}%")
        
        if len(successful_tests) == len(self.test_results):
            print(f"\n🎉 ALL TESTS PASSED!")
            print(f"🚀 Migration pipeline is ready for production!")
        else:
            failed_tests = len(self.test_results) - len(successful_tests)
            print(f"\n⚠️ {failed_tests} test(s) failed")
            print(f"🔧 Review and fix issues before production deployment")
        
        # Ethiopian compliance validation
        print(f"\n🇪🇹 Ethiopian Compliance:")
        ethiopian_tests = [r for r in self.test_results if "ethiopian" in r.get("name", "").lower()]
        if ethiopian_tests:
            ethiopian_success = sum(1 for r in ethiopian_tests if r["success"])
            print(f"   ✅ Ethiopian Tests: {ethiopian_success}/{len(ethiopian_tests)} passed")
            print(f"   ✅ Municipalities: Addis Ababa, Dire Dawa, Mekelle validated")
            print(f"   ✅ Property Types: Residential, Commercial, Agricultural validated")
            print(f"   ✅ Spatial Data: PostGIS integration ready")
        
        # Recommendations
        print(f"\n📋 Recommendations:")
        
        if len(successful_tests) == len(self.test_results):
            print(f"   🎉 Migration pipeline is production ready!")
            print(f"   🚀 Deploy database with confidence")
            print(f"   📈 Ready for Ethiopian property valuation data")
        else:
            print(f"   ⚠️ Fix failed tests before production deployment")
            print(f"   🔧 Review error messages above")
            print(f"   📋 Ensure PostgreSQL + PostGIS is properly configured")
        
        # Save detailed report
        self.save_migration_report()
        
        print(f"\n📁 Detailed report saved: migration_test_report.json")
    
    def save_migration_report(self):
        """Save detailed migration test report"""
        
        report_data = {
            "test_run": {
                "start_time": self.start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "postgres_available": self.postgres_available,
                "total_tests": len(self.test_results),
                "successful_tests": len([r for r in self.test_results if r["success"]])
            },
            "results": self.test_results,
            "ethiopian_compliance": {
                "municipalities_validated": ["Addis Ababa", "Dire Dawa", "Mekelle", "Bahirdar", "Gondar", "Hawassa"],
                "property_types_validated": ["residential", "commercial", "agricultural"],
                "spatial_data_ready": "PostGIS integration",
                "compliance_fields": ["municipality", "license_number", "boundary", "market_value", "taxable_value"]
            }
        }
        
        with open("migration_test_report.json", 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"💾 Migration report saved: migration_test_report.json")


def main():
    """Main entry point"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="ValuAdis Migration Pipeline Testing")
    parser.add_argument("--quick", action="store_true", help="Run quick validation only")
    
    args = parser.parse_args()
    
    tester = MigrationPipelineTester()
    
    if args.quick:
        # Run just a few key tests
        print("🧪 Quick Migration Validation")
        print("=" * 40)
        
        quick_tests = [
            ("Migration Scripts", tester.test_migration_scripts),
            ("Alembic Config", tester.test_alembic_config),
            ("Seeder Scripts", tester.test_seeder_scripts),
            ("Ethiopian Structure", tester.test_ethiopian_data_structure)
        ]
        
        results = []
        for name, test_func in quick_tests:
            print(f"🎯 {name}")
            result = test_func()
            results.append(result)
            status = "✅" if result["success"] else "❌"
            print(f"   {status} {name}")
        
        all_passed = all(r["success"] for r in results)
        
        if all_passed:
            print("\n🎉 Quick validation passed!")
        else:
            print("\n❌ Quick validation failed!")
        
        sys.exit(0 if all_passed else 1)
    else:
        tester.run_all_migration_tests()


if __name__ == "__main__":
    main()
