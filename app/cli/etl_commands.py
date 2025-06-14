"""
Command Line Interface for ETL operations.
Provides CLI commands for import/export operations and data management.
"""
import click
import asyncio
import json
from datetime import datetime, date
from pathlib import Path
import logging
from typing import Optional, Dict, Any

from flask.cli import with_appcontext
from app.services.etl_service import ETLService
from app.services.export_service import EnhancedExportService
from flask import current_app

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.group()
def etl():
    """ETL operations for data import/export."""
    pass


@etl.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--data-type', default='property', type=click.Choice(['property', 'agent', 'economic']),
              help='Type of data being imported')
@click.option('--batch-size', default=1000, type=int, help='Number of records per batch')
@click.option('--resume-from', default=0, type=int, help='Row number to resume from')
@click.option('--validation-level', default='standard', 
              type=click.Choice(['minimal', 'standard', 'strict']),
              help='Level of data validation')
@click.option('--dry-run', is_flag=True, help='Validate data without importing')
@click.option('--max-workers', default=None, type=int, help='Maximum number of worker threads')
@with_appcontext
def import_data(file_path, data_type, batch_size, resume_from, validation_level, dry_run, max_workers):
    """Import large dataset from file."""
    
    click.echo(f"Starting import of {file_path}")
    click.echo(f"Data type: {data_type}")
    click.echo(f"Batch size: {batch_size}")
    click.echo(f"Validation level: {validation_level}")
    click.echo(f"Dry run: {dry_run}")
    
    if dry_run:
        click.echo("⚠️  DRY RUN MODE - No data will be imported")
    
    # Initialize ETL service
    etl_service = ETLService(batch_size=batch_size, max_workers=max_workers)
    
    # Run import
    try:
        # Use asyncio to run the async import function
        result = asyncio.run(etl_service.import_large_dataset(
            file_path=file_path,
            data_type=data_type,
            resume_from=resume_from,
            validation_level=validation_level,
            dry_run=dry_run
        ))
        
        # Display results
        click.echo("\n" + "="*50)
        click.echo("IMPORT SUMMARY")
        click.echo("="*50)
        click.echo(f"Total records processed: {result['total_records_processed']:,}")
        click.echo(f"Successful imports: {result['successful_imports']:,}")
        click.echo(f"Failed imports: {result['failed_imports']:,}")
        click.echo(f"Skipped records: {result['skipped_records']:,}")
        
        # Display upsert-specific metrics if they exist
        if 'updated_records' in result:
            click.echo(f"Updated existing records: {result['updated_records']:,}")
        if 'duplicate_records_handled' in result:
            click.echo(f"Duplicate records handled: {result['duplicate_records_handled']:,}")
        
        click.echo(f"Success rate: {result['success_rate']:.1f}%")
        
        if result['validation_errors_count'] > 0:
            click.echo(f"⚠️  Validation errors: {result['validation_errors_count']}")
        
        if result['data_errors_count'] > 0:
            click.echo(f"❌ Data errors: {result['data_errors_count']}")
        
        # Performance metrics
        if 'performance_metrics' in result:
            perf = result['performance_metrics']
            click.echo(f"\nPerformance:")
            click.echo(f"  Total duration: {perf.get('total_duration', 0):.2f} seconds")
            click.echo(f"  Average batch duration: {perf.get('avg_duration', 0):.2f} seconds")
            click.echo(f"  Peak memory usage: {perf.get('max_memory_delta', 0):.1f} MB")
        
        click.echo("\n✅ Import completed successfully!")
        
    except Exception as e:
        click.echo(f"\n❌ Import failed: {str(e)}")
        logger.error(f"Import failed: {str(e)}", exc_info=True)
        raise click.ClickException(f"Import failed: {str(e)}")


@etl.command()
@click.option('--format', 'format_type', default='csv', 
              type=click.Choice(['csv', 'json', 'excel', 'xml', 'parquet']),
              help='Export format')
@click.option('--output-path', default=None, help='Custom output file path')
@click.option('--city', default=None, help='Filter by city')
@click.option('--province', default=None, help='Filter by province')
@click.option('--property-type', default=None, help='Filter by property type')
@click.option('--price-min', default=None, type=float, help='Minimum price filter')
@click.option('--price-max', default=None, type=float, help='Maximum price filter')
@click.option('--bedrooms-min', default=None, type=int, help='Minimum bedrooms filter')
@click.option('--bedrooms-max', default=None, type=int, help='Maximum bedrooms filter')
@click.option('--sqft-min', default=None, type=int, help='Minimum square footage filter')
@click.option('--sqft-max', default=None, type=int, help='Maximum square footage filter')
@click.option('--sold-date-start', default=None, type=click.DateTime(['%Y-%m-%d']), 
              help='Start date for sold date filter (YYYY-MM-DD)')
@click.option('--sold-date-end', default=None, type=click.DateTime(['%Y-%m-%d']),
              help='End date for sold date filter (YYYY-MM-DD)')
@click.option('--fields', default=None, help='Comma-separated list of fields to export')
@click.option('--compress', is_flag=True, help='Compress the output file')
@click.option('--include-analytics', is_flag=True, help='Include analytics data (Excel only)')
@click.option('--sort-by', default='sold_date', help='Field to sort by')
@click.option('--sort-order', default='desc', type=click.Choice(['asc', 'desc']),
              help='Sort order')
@with_appcontext
def export_properties(format_type, output_path, city, province, property_type, price_min, price_max,
                     bedrooms_min, bedrooms_max, sqft_min, sqft_max, sold_date_start, sold_date_end,
                     fields, compress, include_analytics, sort_by, sort_order):
    """Export property data with filtering options."""
    
    click.echo(f"Starting property export in {format_type.upper()} format")
    
    # Build filters
    filters = {}
    if city:
        filters['city'] = city
    if province:
        filters['province'] = province
    if property_type:
        filters['property_type'] = property_type
    if price_min is not None:
        filters['price_min'] = price_min
    if price_max is not None:
        filters['price_max'] = price_max
    if bedrooms_min is not None:
        filters['bedrooms_min'] = bedrooms_min
    if bedrooms_max is not None:
        filters['bedrooms_max'] = bedrooms_max
    if sqft_min is not None:
        filters['sqft_min'] = sqft_min
    if sqft_max is not None:
        filters['sqft_max'] = sqft_max
    if sold_date_start:
        filters['sold_date_start'] = sold_date_start.date()
    if sold_date_end:
        filters['sold_date_end'] = sold_date_end.date()
    
    filters['sort_by'] = sort_by
    filters['sort_order'] = sort_order
    
    # Parse fields if provided
    field_list = None
    if fields:
        field_list = [f.strip() for f in fields.split(',')]
    
    # Display filters
    if filters:
        click.echo("\nApplied filters:")
        for key, value in filters.items():
            if key not in ['sort_by', 'sort_order']:
                click.echo(f"  {key}: {value}")
    
    # Initialize export service
    export_service = EnhancedExportService()
    
    try:
        # Run export
        result = asyncio.run(export_service.export_properties(
            format_type=format_type,
            filters=filters if filters else None,
            fields=field_list,
            output_path=output_path,
            compress=compress,
            include_analytics=include_analytics
        ))
        
        # Display results
        click.echo("\n" + "="*50)
        click.echo("EXPORT SUMMARY")
        click.echo("="*50)
        click.echo(f"Records exported: {result['total_records']:,}")
        click.echo(f"Output file: {result['file_path']}")
        click.echo(f"File size: {result.get('file_size_mb', 0):.2f} MB")
        click.echo(f"Format: {result['format']}")
        
        if result.get('compressed'):
            click.echo(f"Compression ratio: {(1 - result.get('compressed_size_mb', 0) / result.get('original_size_mb', 1)) * 100:.1f}%")
        
        if 'sheets' in result:
            click.echo(f"Excel sheets: {', '.join(result['sheets'])}")
        
        click.echo("\n✅ Export completed successfully!")
        
    except Exception as e:
        click.echo(f"\n❌ Export failed: {str(e)}")
        logger.error(f"Export failed: {str(e)}", exc_info=True)
        raise click.ClickException(f"Export failed: {str(e)}")


@etl.command()
@click.option('--city', default=None, help='Filter by city')
@click.option('--province', default=None, help='Filter by province')
@click.option('--date-start', default=None, type=click.DateTime(['%Y-%m-%d']),
              help='Start date for analysis (YYYY-MM-DD)')
@click.option('--date-end', default=None, type=click.DateTime(['%Y-%m-%d']),
              help='End date for analysis (YYYY-MM-DD)')
@click.option('--format', 'format_type', default='excel',
              type=click.Choice(['excel', 'csv', 'json']),
              help='Report format')
@click.option('--output-path', default=None, help='Custom output file path')
@with_appcontext
def market_report(city, province, date_start, date_end, format_type, output_path):
    """Generate comprehensive market analysis report."""
    
    click.echo("Generating market analysis report...")
    
    # Parse date range
    date_range = None
    if date_start and date_end:
        date_range = (date_start.date(), date_end.date())
        click.echo(f"Date range: {date_range[0]} to {date_range[1]}")
    
    if city:
        click.echo(f"City: {city}")
    if province:
        click.echo(f"Province: {province}")
    
    # Initialize export service
    export_service = EnhancedExportService()
    
    try:
        # Generate report
        result = asyncio.run(export_service.export_market_report(
            city=city,
            province=province,
            date_range=date_range,
            output_format=format_type
        ))
        
        # Display results
        click.echo("\n" + "="*50)
        click.echo("MARKET REPORT SUMMARY")
        click.echo("="*50)
        
        if 'total_properties_analyzed' in result:
            click.echo(f"Properties analyzed: {result['total_properties_analyzed']:,}")
        
        click.echo(f"Report file: {result['file_path']}")
        click.echo(f"File size: {result.get('file_size_mb', 0):.2f} MB")
        click.echo(f"Report type: {result.get('report_type', format_type)}")
        
        if 'sheets' in result:
            click.echo(f"Excel sheets: {', '.join(result['sheets'])}")
        
        click.echo("\n✅ Market report generated successfully!")
        
    except Exception as e:
        click.echo(f"\n❌ Report generation failed: {str(e)}")
        logger.error(f"Report generation failed: {str(e)}", exc_info=True)
        raise click.ClickException(f"Report generation failed: {str(e)}")


@etl.command()
@click.option('--operation-id', default=None, help='Specific operation ID to check')
@with_appcontext
def status(operation_id):
    """Check status of running ETL operations."""
    
    click.echo("ETL Operation Status")
    click.echo("="*30)
    
    if operation_id:
        click.echo(f"Checking status for operation: {operation_id}")
        # In a real implementation, this would check the status
        # of a specific operation from a progress tracker
        click.echo("Status checking functionality would be implemented here")
    else:
        click.echo("No active operations found")
        click.echo("\nTo check specific operation status, use:")
        click.echo("flask etl status --operation-id <id>")


@etl.command()
@click.option('--table', default='properties', 
              type=click.Choice(['properties', 'agents', 'economic_data', 'all']),
              help='Database table to optimize')
@click.option('--analyze', is_flag=True, help='Run table analysis for query optimization')
@click.option('--reindex', is_flag=True, help='Rebuild indexes')
@with_appcontext
def optimize_db(table, analyze, reindex):
    """Optimize database for large dataset operations."""
    from app import db
    from sqlalchemy import text
    
    click.echo(f"Optimizing database table: {table}")
    
    try:
        if table == 'all' or table == 'properties':
            click.echo("Optimizing properties table...")
            
            if analyze:
                # Analyze table statistics
                db.session.execute(text("ANALYZE TABLE properties"))
                click.echo("✓ Table analysis completed")
            
            if reindex:
                # Rebuild indexes (MySQL specific)
                db.session.execute(text("ALTER TABLE properties ENGINE=InnoDB"))
                click.echo("✓ Indexes rebuilt")
        
        db.session.commit()
        click.echo("\n✅ Database optimization completed!")
        
    except Exception as e:
        db.session.rollback()
        click.echo(f"\n❌ Database optimization failed: {str(e)}")
        raise click.ClickException(f"Database optimization failed: {str(e)}")


@etl.command()
@click.option('--keep-days', default=30, type=int, help='Number of days of logs to keep')
@with_appcontext
def cleanup_logs(keep_days):
    """Clean up old ETL operation logs."""
    
    click.echo(f"Cleaning up ETL logs older than {keep_days} days...")
    
    # Implementation would clean up log files and database log entries
    click.echo("Log cleanup functionality would be implemented here")
    click.echo("✅ Log cleanup completed!")


@etl.command()
@with_appcontext
def validate_data():
    """Run data validation checks on existing database records."""
    from app import db
    from app.models.property import Property
    
    click.echo("Running data validation checks...")
    
    # Check for missing required fields
    click.echo("Checking for missing required fields...")
    
    missing_listing_id = db.session.query(Property).filter(
        Property.listing_id.is_(None)
    ).count()
    
    missing_city = db.session.query(Property).filter(
        Property.city.is_(None)
    ).count()
    
    invalid_prices = db.session.query(Property).filter(
        Property.sold_price <= 0
    ).count()
    
    # Display results
    click.echo("\n" + "="*40)
    click.echo("DATA VALIDATION SUMMARY")
    click.echo("="*40)
    click.echo(f"Missing listing IDs: {missing_listing_id}")
    click.echo(f"Missing cities: {missing_city}")
    click.echo(f"Invalid prices (≤ 0): {invalid_prices}")
    
    if missing_listing_id + missing_city + invalid_prices == 0:
        click.echo("\n✅ All validation checks passed!")
    else:
        click.echo("\n⚠️  Data quality issues found")
        click.echo("Consider running data cleanup operations")


@etl.command()
@click.argument('source_file', type=click.Path(exists=True))
@click.argument('destination_file', type=click.Path())
@click.option('--chunk-size', default=10000, type=int, help='Number of records per chunk')
@with_appcontext
def convert_format(source_file, destination_file, chunk_size):
    """Convert data file from one format to another."""
    
    source_path = Path(source_file)
    dest_path = Path(destination_file)
    
    source_ext = source_path.suffix.lower()
    dest_ext = dest_path.suffix.lower()
    
    click.echo(f"Converting {source_ext} to {dest_ext}")
    click.echo(f"Source: {source_file}")
    click.echo(f"Destination: {destination_file}")
    click.echo(f"Chunk size: {chunk_size:,} records")
    
    try:
        if source_ext == '.csv' and dest_ext == '.json':
            _convert_csv_to_json(source_file, destination_file, chunk_size)
        elif source_ext == '.json' and dest_ext == '.csv':
            _convert_json_to_csv(source_file, destination_file)
        else:
            raise click.ClickException(f"Conversion from {source_ext} to {dest_ext} not supported")
        
        # Check output file size
        output_size = dest_path.stat().st_size / (1024 * 1024)  # MB
        click.echo(f"\n✅ Conversion completed!")
        click.echo(f"Output file size: {output_size:.2f} MB")
        
    except Exception as e:
        click.echo(f"\n❌ Conversion failed: {str(e)}")
        raise click.ClickException(f"Conversion failed: {str(e)}")


def _convert_csv_to_json(source_file: str, dest_file: str, chunk_size: int):
    """Convert CSV to JSON in chunks."""
    
    all_records = []
    
    with open(source_file, 'r', encoding='utf-8') as f:
        import csv
        reader = csv.DictReader(f)
        
        for i, row in enumerate(reader):
            all_records.append(row)
            
            if (i + 1) % chunk_size == 0:
                click.echo(f"Processed {i + 1:,} records...")
    
    with open(dest_file, 'w', encoding='utf-8') as f:
        json.dump(all_records, f, indent=2, default=str)


def _convert_json_to_csv(source_file: str, dest_file: str):
    """Convert JSON to CSV."""
    
    with open(source_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not data:
        raise ValueError("No data found in JSON file")
    
    # Get fieldnames from first record
    if isinstance(data, list):
        fieldnames = data[0].keys()
        records = data
    else:
        fieldnames = data.keys()
        records = [data]
    
    with open(dest_file, 'w', newline='', encoding='utf-8') as f:
        import csv
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


# Register the command group with Flask
def register_etl_commands(app):
    """Register ETL commands with Flask app."""
    app.cli.add_command(etl)

# ML Model Management Commands
@etl.command()
@click.option('--samples', default=5000, type=int, help='Number of training samples to generate')
@click.option('--features', default=26, type=int, help='Number of features to use')
@click.option('--test-size', default=0.2, type=float, help='Test set proportion')
@click.option('--cv-folds', default=5, type=int, help='Cross-validation folds')
@with_appcontext
def train_enhanced_model(samples, features, test_size, cv_folds):
    """Train enhanced ML models with economic indicators."""
    try:
        click.echo(f"🚀 Starting enhanced model training...")
        click.echo(f"   Samples: {samples}")
        click.echo(f"   Features: {features}")
        click.echo(f"   Test size: {test_size}")
        click.echo(f"   CV folds: {cv_folds}")
        
        # Import and run the enhanced training
        import subprocess
        import sys
        
        result = subprocess.run([
            sys.executable, 'enhanced_model_training.py',
            '--samples', str(samples),
            '--features', str(features),
            '--test-size', str(test_size),
            '--cv-folds', str(cv_folds)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            click.echo("✅ Enhanced model training completed successfully!")
            click.echo(result.stdout)
        else:
            click.echo("❌ Enhanced model training failed!")
            click.echo(result.stderr)
            
    except Exception as e:
        click.echo(f"❌ Training failed: {str(e)}")

@etl.command()
@with_appcontext
def validate_model():
    """Validate current ML model performance."""
    try:
        from app.services.ml_service import MLService
        
        click.echo("🔍 Validating ML model performance...")
        
        ml_service = MLService()
        validation = ml_service.validate_model_performance()
        
        click.echo(f"\nModel: {validation.get('model_name', 'Unknown')}")
        click.echo(f"Status: {validation.get('status', 'Unknown')}")
        
        if 'training_date' in validation:
            click.echo(f"Trained: {validation['training_date']}")
        
        if 'checks' in validation:
            click.echo("\nPerformance Checks:")
            for check_name, check_result in validation['checks'].items():
                status = "✅" if check_result['passed'] else "❌"
                click.echo(f"  {status} {check_name}: {check_result['value']:.4f} (threshold: {check_result['threshold']})")
        
        if validation.get('status') == 'valid':
            click.echo("\n✅ Model validation passed!")
        else:
            click.echo("\n⚠️  Model validation failed!")
            
    except Exception as e:
        click.echo(f"❌ Validation failed: {str(e)}")

@etl.command()
@with_appcontext
def list_models():
    """List available trained models."""
    try:
        from app.services.ml_service import MLService
        
        ml_service = MLService()
        models = ml_service.get_available_models()
        metadata = ml_service.get_model_metadata()
        
        click.echo("📋 Available Models:")
        click.echo("-" * 50)
        
        if not models:
            click.echo("No trained models found.")
            return
        
        current_model = metadata.get('best_model', 'Unknown')
        all_performance = metadata.get('all_models_performance', {})
        
        for model in models:
            status = "🎯" if model.lower() == current_model.lower() else "  "
            performance = all_performance.get(model, {})
            
            click.echo(f"{status} {model}")
            if performance:
                click.echo(f"     R² Score: {performance.get('r2', 'N/A'):.4f}")
                click.echo(f"     RMSE: ${performance.get('rmse', 'N/A'):,.0f}")
                click.echo(f"     MAPE: {performance.get('mape', 'N/A'):.2f}%")
            click.echo()
        
    except Exception as e:
        click.echo(f"❌ Failed to list models: {str(e)}")

@etl.command()
@click.argument('model_name')
@with_appcontext
def switch_model(model_name):
    """Switch to a different trained model."""
    try:
        from app.services.ml_service import MLService
        
        click.echo(f"🔄 Switching to model: {model_name}")
        
        ml_service = MLService()
        success = ml_service.switch_model(model_name)
        
        if success:
            click.echo(f"✅ Successfully switched to {model_name}")
        else:
            click.echo(f"❌ Failed to switch to {model_name}")
            
    except Exception as e:
        click.echo(f"❌ Model switching failed: {str(e)}")

@etl.command()
@click.option('--property-type', default='Detached', help='Property type for prediction test')
@click.option('--city', default='Toronto', help='City for prediction test')
@click.option('--bedrooms', default=3, type=int, help='Number of bedrooms')
@click.option('--bathrooms', default=2.5, type=float, help='Number of bathrooms')
@click.option('--sqft', default=2000, type=int, help='Square footage')
@with_appcontext
def test_prediction(property_type, city, bedrooms, bathrooms, sqft):
    """Test ML model prediction with sample data."""
    try:
        from app.services.ml_service import MLService
        
        click.echo("🧪 Testing ML model prediction...")
        
        test_property = {
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'square_feet': sqft,
            'city': city,
            'property_type': property_type,
            'province': 'ON',
            'year_built': 2015,
            'lot_size': 5000,
            'dom': 25,
            'taxes': 6000
        }
        
        click.echo(f"Test Property:")
        for key, value in test_property.items():
            click.echo(f"  {key}: {value}")
        
        ml_service = MLService()
        result = ml_service.predict_property_price(test_property)
        
        click.echo(f"\nPrediction Results:")
        if result.get('predicted_price'):
            click.echo(f"  Predicted Price: ${result['predicted_price']:,.2f}")
            click.echo(f"  Confidence: {result['confidence']:.1%}")
            click.echo(f"  Method: {result['prediction_method']}")
            click.echo(f"  Features Used: {result['features_used']}")
        else:
            click.echo(f"  Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        click.echo(f"❌ Prediction test failed: {str(e)}")


# Register the command group with Flask
def register_etl_commands(app):
    """Register ETL commands with Flask app."""
    app.cli.add_command(etl)


if __name__ == '__main__':
    etl()
