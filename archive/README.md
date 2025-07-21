# Archive Directory

This directory contains files that have been moved from the root directory to keep the project organized. These files have been reviewed for unique functionality before archiving.

## Directory Structure

### `/test_results/`
Contains JSON and HTML test result files that were generated during testing phases:
- `api_key_test_results_*.json` - Multiple timestamped API key test results
- `complete_functionality_test_results_*.json` - Complete functionality test results from July 11
- `geographic_limiting_test_results.json` - Geographic rate limiting test results
- `chart_test*.html` - Chart visualization test files
- `feature_status_results.json` - Feature status test results
- `test_output.json` - General test output

### `/legacy_tests/`
Contains test files that have been superseded by more comprehensive versions or are no longer needed:
- `phpmyadmin_connection_test.py` - Empty placeholder file
- `mock_test_server.py` - Empty placeholder file
- `basic_connection_test.py` - Basic DB connection test (superseded by `test_db_connections.py`)
- `test_docker_connection.py` - Docker connection test (superseded by `final_docker_connection_test.py`)
- `test_docker_env_connection.py` - Environment-based Docker test
- `test_app_docker_migration.py` - App migration test (migration complete)
- `verify_migration.py` - Migration verification (migration complete)
- `final_migration_verification.py` - Final migration verification
- `Rate_limit_test.py` - Basic rate limit test (superseded by `comprehensive_rate_limit_test.py`)
- `pytest.ini.bak` - Backup of pytest configuration
- `CHANGES_LOG.md.backup` - Backup of changes log

### `/demo_files/`
Contains demonstration and example files that are useful for documentation but not for production:
- `demo_abuse_detection.py` - Abuse detection system demo
- `integrated_rate_limiting_demo.py` - Comprehensive rate limiting integration demo

## Files Kept in Root (and why)

The following files were kept in the root directory because they have unique functionality:

- `test_db_connections.py` - Tests both old and new database connections (unique)
- `comprehensive_rate_limit_test.py` - Most comprehensive rate limiting test suite
- `database_export_for_docker.py` - Comprehensive database export functionality
- `final_docker_connection_test.py` - Final version of Docker connection testing
- `simple_test_runner.py` - Unique dependency checking and pytest installation functionality
- `setup_abuse_detection.py` - Setup script with dependency checking
- Active test files in `/tests/` directory

## Restoration

If any of these archived files are needed, they can be moved back to the root directory. All files have been preserved with their original functionality intact.

Date archived: July 20, 2025
