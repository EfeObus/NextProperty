"""
ETL Service for NextProperty Real Estate Platform
Handles Extract, Transform, Load operations for large datasets.
Designed to process 50GB+ datasets efficiently with batch processing.
"""
import pandas as pd
import numpy as np
import csv
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Iterator, Tuple, Any
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import time
import gc
import psutil
import signal
import sys
from contextlib import contextmanager
import os

from app.models.property import Property
from app.models.agent import Agent
from app.models.economic_data import EconomicIndicator
from app.services.data_processors import DataValidator, PropertyDataProcessor, AgentDataProcessor, EconomicDataProcessor, DataMapper
from flask import current_app

logger = logging.getLogger(__name__)

class ETLService:
    """
    Comprehensive ETL service for handling large-scale real estate data operations.
    Features:
    - Batch processing for memory efficiency
    - Progress tracking and resumable imports
    - Data validation and cleaning
    - Error handling and logging
    - Multi-format support (CSV, JSON, Excel)
    - Parallel processing capabilities
    """
    
    def __init__(self, batch_size: int = 1000, max_workers: int = None):
        """
        Initialize ETL service with configuration.
        
        Args:
            batch_size: Number of records to process in each batch
            max_workers: Maximum number of worker threads/processes
        """
        self.batch_size = batch_size
        self.max_workers = max_workers or min(32, (mp.cpu_count() or 1) + 4)
        self.progress_tracker = ProgressTracker()
        self.data_validator = DataValidator()
        self.data_mapper = DataMapper()
        self.error_handler = ETLErrorHandler()
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self._shutdown_flag = False
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self._shutdown_flag = True
    
    @contextmanager
    def performance_context(self, operation_name: str):
        """Context manager for performance monitoring."""
        start_time = time.time()
        memory_before = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        try:
            yield
        finally:
            end_time = time.time()
            memory_after = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            self.performance_monitor.record_operation(
                operation_name,
                end_time - start_time,
                memory_after - memory_before
            )
    
    async def import_large_dataset(
        self,
        file_path: str,
        data_type: str = 'property',
        resume_from: int = 0,
        validation_level: str = 'standard',
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Import large dataset with batch processing and progress tracking.
        
        Args:
            file_path: Path to the data file
            data_type: Type of data being imported ('property', 'agent', 'economic')
            resume_from: Row number to resume from (for interrupted imports)
            validation_level: 'minimal', 'standard', or 'strict'
            dry_run: If True, validate data without importing
        
        Returns:
            Dictionary with import statistics and results
        """
        logger.info(f"Starting import of {file_path}, type: {data_type}")
        
        # Define operation_id that will be used throughout
        operation_id = f"import_{data_type}"
        
        with self.performance_context("large_dataset_import"):
            try:
                # Initialize progress tracking
                total_rows = await self._count_file_rows(file_path)
                self.progress_tracker.start_operation(
                    operation_id,
                    total_rows,
                    resume_from
                )
                
                # Setup data processor based on type
                processor = self._get_data_processor(data_type)
                
                # Process file in batches
                results = await self._process_file_batches(
                    file_path,
                    processor,
                    operation_id,
                    resume_from,
                    validation_level,
                    dry_run
                )
                
                # Generate summary report
                summary = self._generate_import_summary(results)
                logger.info(f"Import completed: {summary}")
                
                return summary
                
            except Exception as e:
                logger.error(f"Import failed: {str(e)}")
                self.error_handler.handle_critical_error(e, "import_large_dataset")
                raise
            finally:
                self.progress_tracker.end_operation(operation_id)
                gc.collect()  # Force garbage collection
    
    async def _count_file_rows(self, file_path: str) -> int:
        """Count total rows in file efficiently."""
        try:
            if file_path.endswith('.csv'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return sum(1 for _ in f) - 1  # Subtract header
            elif file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return len(data) if isinstance(data, list) else 1
            else:
                # For other formats, estimate based on file size
                file_size = Path(file_path).stat().st_size
                return file_size // 500  # Rough estimate
        except Exception as e:
            logger.warning(f"Could not count rows in {file_path}: {e}")
            return 0
    
    async def _process_file_batches(
        self,
        file_path: str,
        processor,
        operation_id: str,
        resume_from: int,
        validation_level: str,
        dry_run: bool
    ) -> Dict[str, Any]:
        """Process file in batches with parallel processing."""
        
        results = {
            'total_processed': 0,
            'successful_imports': 0,
            'failed_imports': 0,
            'validation_errors': [],
            'data_errors': [],
            'skipped_rows': 0
        }
        
        batch_generator = self._create_batch_generator(file_path, resume_from)
        
        # For database operations, process sequentially to maintain Flask context
        # For dry-run, can use parallel processing
        if dry_run:
            # Use ThreadPoolExecutor for I/O bound operations (validation only)
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                tasks = []
                
                async for batch_num, batch_data in batch_generator:
                    if self._shutdown_flag:
                        logger.info("Shutdown requested, stopping batch processing")
                        break
                    
                    # Submit batch for processing
                    task = executor.submit(
                        self._process_batch,
                        batch_data,
                        batch_num,
                        processor,
                        validation_level,
                        dry_run
                    )
                    tasks.append(task)
                    
                    # Wait for completed tasks and update results
                    if len(tasks) >= self.max_workers:
                        completed_tasks = [t for t in tasks if t.done()]
                        for task in completed_tasks:
                            batch_result = task.result()
                            self._merge_batch_results(results, batch_result)
                            tasks.remove(task)
                    
                    # Update progress
                    self.progress_tracker.update_progress(
                        operation_id,
                        results['total_processed']
                    )
                
                # Wait for remaining tasks
                for task in tasks:
                    batch_result = task.result()
                    self._merge_batch_results(results, batch_result)
        else:
            # Sequential processing for database operations to maintain Flask context
            async for batch_num, batch_data in batch_generator:
                if self._shutdown_flag:
                    logger.info("Shutdown requested, stopping batch processing")
                    break
                
                # Process batch sequentially
                batch_result = self._process_batch(
                    batch_data,
                    batch_num,
                    processor,
                    validation_level,
                    dry_run
                )
                self._merge_batch_results(results, batch_result)
                
                # Update progress
                self.progress_tracker.update_progress(
                    operation_id,
                    results['total_processed']
                )
        
        return results
    
    def _process_batch(
        self,
        batch_data: List[Dict],
        batch_num: int,
        processor,
        validation_level: str,
        dry_run: bool
    ) -> Dict[str, Any]:
        """Process a single batch of data."""
        
        batch_results = {
            'batch_num': batch_num,
            'total_processed': 0,
            'successful_imports': 0,
            'failed_imports': 0,
            'validation_errors': [],
            'data_errors': [],
            'skipped_rows': 0
        }
        
        try:
            with self.performance_context(f"batch_{batch_num}_processing"):
                # Validate batch data
                validated_data = self.data_validator.validate_batch(
                    batch_data,
                    validation_level
                )
                
                batch_results['validation_errors'].extend(
                    validated_data.get('errors', [])
                )
                
                if not dry_run and validated_data['valid_records']:
                    # Transform and load data
                    transformed_data = processor.transform_batch(
                        validated_data['valid_records']
                    )
                    
                    load_results = self._load_batch_to_database(
                        transformed_data,
                        processor.model_class
                    )
                    
                    batch_results['successful_imports'] = load_results['success_count']
                    batch_results['failed_imports'] = load_results['error_count']
                    
                    # Handle upsert-specific metrics
                    if 'duplicate_count' in load_results:
                        batch_results['duplicate_count'] = load_results['duplicate_count']
                    if 'updated_count' in load_results:
                        batch_results['updated_count'] = load_results['updated_count']
                    
                    batch_results['data_errors'].extend(load_results['errors'])
                
                batch_results['total_processed'] = len(batch_data)
                batch_results['skipped_rows'] = (
                    len(batch_data) - len(validated_data.get('valid_records', []))
                )
                
        except Exception as e:
            logger.error(f"Batch {batch_num} processing failed: {e}")
            batch_results['failed_imports'] = len(batch_data)
            batch_results['data_errors'].append({
                'batch': batch_num,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })
        
        return batch_results
    
    def _load_batch_to_database(
        self,
        batch_data: List[Dict],
        model_class
    ) -> Dict[str, Any]:
        """Load batch data to database with error handling and upsert logic."""
        
        results = {
            'success_count': 0,
            'error_count': 0,
            'duplicate_count': 0,
            'updated_count': 0,
            'errors': []
        }
        
        try:
            # Import here to avoid circular imports and use current app context
            from flask import current_app
            from app import db
            from sqlalchemy.dialects.sqlite import insert as sqlite_insert
            from sqlalchemy.dialects.mysql import insert as mysql_insert
            
            # Use the current application context
            engine = db.engine
            dialect_name = engine.dialect.name
            
            with engine.begin() as conn:
                for record in batch_data:
                    try:
                        listing_id = record.get('listing_id')
                        
                        if dialect_name == 'sqlite':
                            # SQLite UPSERT using ON CONFLICT
                            stmt = sqlite_insert(model_class.__table__).values(**record)
                            stmt = stmt.on_conflict_do_update(
                                index_elements=['listing_id'],
                                set_={
                                    key: stmt.excluded[key] 
                                    for key in record.keys() 
                                    if key != 'listing_id' and key != 'created_at'
                                }
                            )
                            # Update the updated_at field
                            if 'updated_at' in record:
                                stmt.set_['updated_at'] = datetime.utcnow()
                                
                        elif dialect_name == 'mysql':
                            # MySQL UPSERT using ON DUPLICATE KEY UPDATE
                            stmt = mysql_insert(model_class.__table__).values(**record)
                            update_dict = {
                                key: stmt.inserted[key] 
                                for key in record.keys() 
                                if key != 'listing_id' and key != 'created_at'
                            }
                            if 'updated_at' in record:
                                update_dict['updated_at'] = datetime.utcnow()
                            stmt = stmt.on_duplicate_key_update(**update_dict)
                            
                        else:
                            # Fallback for other databases - check if exists first
                            existing = conn.execute(
                                text(f"SELECT listing_id FROM {model_class.__tablename__} WHERE listing_id = :listing_id"),
                                {'listing_id': listing_id}
                            ).fetchone()
                            
                            if existing:
                                # Update existing record
                                update_values = {k: v for k, v in record.items() if k != 'listing_id' and k != 'created_at'}
                                update_values['updated_at'] = datetime.utcnow()
                                
                                update_stmt = model_class.__table__.update().where(
                                    model_class.__table__.c.listing_id == listing_id
                                ).values(**update_values)
                                conn.execute(update_stmt)
                                results['updated_count'] += 1
                            else:
                                # Insert new record
                                stmt = model_class.__table__.insert().values(**record)
                                conn.execute(stmt)
                                results['success_count'] += 1
                            continue
                        
                        # Execute the upsert statement
                        result = conn.execute(stmt)
                        
                        # For SQLite and MySQL, we need to check if it was an insert or update
                        if dialect_name in ['sqlite', 'mysql']:
                            if hasattr(result, 'rowcount') and result.rowcount > 0:
                                # Check if this was an update (record already existed)
                                check_existing = conn.execute(
                                    text(f"SELECT created_at, updated_at FROM {model_class.__tablename__} WHERE listing_id = :listing_id"),
                                    {'listing_id': listing_id}
                                ).fetchone()
                                
                                if check_existing and check_existing[0] != check_existing[1]:
                                    # created_at != updated_at means it was updated
                                    results['updated_count'] += 1
                                else:
                                    # It was a new insert
                                    results['success_count'] += 1
                            else:
                                results['success_count'] += 1
                        
                    except IntegrityError as e:
                        # This shouldn't happen with upsert, but just in case
                        results['duplicate_count'] += 1
                        logger.warning(f"Unexpected integrity error for {listing_id}: {e}")
                        
                    except Exception as e:
                        results['error_count'] += 1
                        results['errors'].append({
                            'record': record.get('listing_id', 'unknown'),
                            'error': str(e),
                            'timestamp': datetime.utcnow().isoformat()
                        })
                        logger.error(f"Error processing record {listing_id}: {e}")
                        
        except Exception as e:
            logger.error(f"Batch database load failed: {e}")
            results['error_count'] = len(batch_data)
            results['errors'].append({
                'batch_error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })
        
        return results
    
    async def _create_batch_generator(
        self,
        file_path: str,
        resume_from: int = 0
    ) -> Iterator[Tuple[int, List[Dict]]]:
        """Create async generator for processing file in batches."""
        
        batch_num = resume_from // self.batch_size
        
        if file_path.endswith('.csv'):
            async for batch in self._csv_batch_generator(file_path, resume_from):
                yield batch_num, batch
                batch_num += 1
                
        elif file_path.endswith('.json'):
            async for batch in self._json_batch_generator(file_path, resume_from):
                yield batch_num, batch
                batch_num += 1
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
    
    async def _csv_batch_generator(
        self,
        file_path: str,
        resume_from: int
    ) -> Iterator[List[Dict]]:
        """Generate batches from CSV file."""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Skip to resume point
            for _ in range(resume_from):
                next(reader, None)
            
            batch = []
            for row in reader:
                if self._shutdown_flag:
                    break
                    
                batch.append(row)
                
                if len(batch) >= self.batch_size:
                    yield batch
                    batch = []
                    
                    # Allow other coroutines to run
                    await asyncio.sleep(0)
            
            # Yield remaining records
            if batch:
                yield batch
    
    async def _json_batch_generator(
        self,
        file_path: str,
        resume_from: int
    ) -> Iterator[List[Dict]]:
        """Generate batches from JSON file."""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            if isinstance(data, list):
                # Skip to resume point
                data = data[resume_from:]
                
                for i in range(0, len(data), self.batch_size):
                    if self._shutdown_flag:
                        break
                        
                    batch = data[i:i + self.batch_size]
                    yield batch
                    
                    # Allow other coroutines to run
                    await asyncio.sleep(0)
            else:
                # Single record
                if resume_from == 0:
                    yield [data]
    
    def _merge_batch_results(
        self,
        main_results: Dict[str, Any],
        batch_results: Dict[str, Any]
    ):
        """Merge batch results into main results."""
        
        main_results['total_processed'] += batch_results['total_processed']
        main_results['successful_imports'] += batch_results['successful_imports']
        main_results['failed_imports'] += batch_results['failed_imports']
        main_results['skipped_rows'] += batch_results['skipped_rows']
        
        # Handle upsert-specific metrics if they exist
        if 'duplicate_count' in batch_results:
            if 'duplicate_count' not in main_results:
                main_results['duplicate_count'] = 0
            main_results['duplicate_count'] += batch_results['duplicate_count']
        
        if 'updated_count' in batch_results:
            if 'updated_count' not in main_results:
                main_results['updated_count'] = 0
            main_results['updated_count'] += batch_results['updated_count']
        
        main_results['validation_errors'].extend(
            batch_results['validation_errors']
        )
        main_results['data_errors'].extend(
            batch_results['data_errors']
        )
    
    def _get_data_processor(self, data_type: str):
        """Get appropriate data processor for the data type."""
        
        processors = {
            'property': PropertyDataProcessor(),
            'agent': AgentDataProcessor(),
            'economic': EconomicDataProcessor()
        }
        
        if data_type not in processors:
            raise ValueError(f"Unsupported data type: {data_type}")
        
        return processors[data_type]
    
    def _generate_import_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive import summary."""
        
        end_time = datetime.utcnow()
        performance_stats = self.performance_monitor.get_summary()
        
        # Calculate total successful operations (inserts + updates)
        total_successful = results['successful_imports'] + results.get('updated_count', 0)
        
        summary = {
            'import_completed_at': end_time.isoformat(),
            'total_records_processed': results['total_processed'],
            'successful_imports': results['successful_imports'],
            'failed_imports': results['failed_imports'],
            'skipped_records': results['skipped_rows'],
            'validation_errors_count': len(results['validation_errors']),
            'data_errors_count': len(results['data_errors']),
            'success_rate': (
                total_successful / results['total_processed'] * 100
                if results['total_processed'] > 0 else 0
            ),
            'performance_metrics': performance_stats,
            'errors': {
                'validation_errors': results['validation_errors'][:100],  # Limit output
                'data_errors': results['data_errors'][:100]
            }
        }
        
        # Add upsert-specific metrics if they exist
        if 'updated_count' in results:
            summary['updated_records'] = results['updated_count']
        if 'duplicate_count' in results:
            summary['duplicate_records_handled'] = results['duplicate_count']
        
        return summary

    async def import_properties_csv(
        self,
        file_path: str,
        batch_size: int = None,
        validation_level: str = 'standard',
        resume_from: int = 0,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Import properties from CSV file with optimized batch processing.
        
        Args:
            file_path: Path to the CSV file
            batch_size: Number of records to process per batch
            validation_level: 'minimal', 'standard', or 'strict'
            resume_from: Row number to resume from (for interrupted imports)
            dry_run: If True, validate data without importing
        
        Returns:
            Dictionary with import statistics and results
        """
        if batch_size:
            self.batch_size = batch_size
            
        logger.info(f"Starting CSV import from {file_path}")
        
        # Verify file exists and is readable
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        
        try:
            # Use the existing import_large_dataset method with CSV-specific handling
            result = await self.import_large_dataset(
                file_path=file_path,
                data_type='property',
                resume_from=resume_from,
                validation_level=validation_level,
                dry_run=dry_run
            )
            
            # Add CSV-specific metadata
            result.update({
                'file_type': 'csv',
                'file_path': file_path,
                'batch_size_used': self.batch_size
            })
            
            logger.info(f"CSV import completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"CSV import failed: {str(e)}")
            raise
    
    def import_properties_csv_sync(
        self,
        file_path: str,
        batch_size: int = None,
        validation_level: str = 'standard'
    ) -> Dict[str, Any]:
        """
        Synchronous version of CSV import for CLI usage.
        
        Args:
            file_path: Path to the CSV file
            batch_size: Number of records to process per batch
            validation_level: 'minimal', 'standard', or 'strict'
        
        Returns:
            Dictionary with import statistics and results
        """
        if batch_size:
            self.batch_size = batch_size
            
        logger.info(f"Starting synchronous CSV import from {file_path}")
        
        # Verify file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        
        operation_id = "csv_import_sync"
        
        try:
            # Count rows for progress tracking
            total_rows = self._count_file_rows_sync(file_path)
            self.progress_tracker.start_operation(operation_id, total_rows, 0)
            
            # Get data processor
            processor = self._get_data_processor('property')
            
            # Process file synchronously
            results = self._process_csv_file_sync(
                file_path,
                processor,
                operation_id,
                validation_level
            )
            
            # Generate summary
            summary = self._generate_import_summary(results)
            summary.update({
                'file_type': 'csv',
                'file_path': file_path,
                'batch_size_used': self.batch_size
            })
            
            logger.info(f"Synchronous CSV import completed: {summary}")
            return summary
            
        except Exception as e:
            logger.error(f"Synchronous CSV import failed: {str(e)}")
            self.error_handler.handle_critical_error(e, "import_properties_csv_sync")
            raise
        finally:
            self.progress_tracker.end_operation(operation_id)
    
    def _count_file_rows_sync(self, file_path: str) -> int:
        """Count total rows in CSV file synchronously."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return sum(1 for _ in f) - 1  # Subtract header
        except Exception as e:
            logger.warning(f"Could not count rows in {file_path}: {e}")
            return 0
    
    def _process_csv_file_sync(
        self,
        file_path: str,
        processor,
        operation_id: str,
        validation_level: str
    ) -> Dict[str, Any]:
        """Process CSV file synchronously in batches."""
        
        results = {
            'total_processed': 0,
            'successful_imports': 0,
            'failed_imports': 0,
            'validation_errors': [],
            'data_errors': [],
            'skipped_rows': 0
        }
        
        try:
            import csv
            
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                batch_data = []
                
                for row_num, row in enumerate(reader):
                    batch_data.append(row)
                    
                    # Process batch when it reaches batch_size
                    if len(batch_data) >= self.batch_size:
                        batch_result = self._process_batch(
                            batch_data,
                            row_num // self.batch_size,
                            processor,
                            validation_level,
                            False  # Not dry run
                        )
                        self._merge_batch_results(results, batch_result)
                        
                        # Update progress
                        self.progress_tracker.update_progress(
                            operation_id,
                            results['total_processed']
                        )
                        
                        # Clear batch
                        batch_data = []
                
                # Process remaining records
                if batch_data:
                    batch_result = self._process_batch(
                        batch_data,
                        (row_num // self.batch_size) + 1,
                        processor,
                        validation_level,
                        False
                    )
                    self._merge_batch_results(results, batch_result)
                    
        except Exception as e:
            logger.error(f"Error processing CSV file: {str(e)}")
            self.error_handler.handle_critical_error(e, "process_csv_file_sync")
            raise
        
        return results

class ProgressTracker:
    """Track progress of long-running ETL operations."""
    
    def __init__(self):
        self.operations = {}
    
    def start_operation(self, operation_id: str, total_items: int, start_from: int = 0):
        """Start tracking a new operation."""
        self.operations[operation_id] = {
            'total_items': total_items,
            'processed_items': start_from,
            'start_time': datetime.utcnow(),
            'last_update': datetime.utcnow(),
            'errors': 0
        }
        logger.info(f"Started operation {operation_id}: {total_items} items")
    
    def update_progress(self, operation_id: str, processed_count: int, errors: int = 0):
        """Update progress for an operation."""
        if operation_id in self.operations:
            op = self.operations[operation_id]
            op['processed_items'] = processed_count
            op['last_update'] = datetime.utcnow()
            op['errors'] += errors
            
            # Log progress every 10% or 10,000 records
            progress_pct = (processed_count / op['total_items']) * 100
            if processed_count % 10000 == 0 or processed_count % (op['total_items'] // 10) == 0:
                logger.info(f"Operation {operation_id}: {progress_pct:.1f}% complete ({processed_count}/{op['total_items']})")
    
    def get_progress(self, operation_id: str) -> Dict[str, Any]:
        """Get current progress for an operation."""
        if operation_id not in self.operations:
            return {}
        
        op = self.operations[operation_id]
        elapsed = (datetime.utcnow() - op['start_time']).total_seconds()
        progress_pct = (op['processed_items'] / op['total_items']) * 100
        
        # Estimate remaining time
        if op['processed_items'] > 0:
            rate = op['processed_items'] / elapsed
            remaining_items = op['total_items'] - op['processed_items']
            eta_seconds = remaining_items / rate if rate > 0 else 0
        else:
            eta_seconds = 0
        
        return {
            'operation_id': operation_id,
            'total_items': op['total_items'],
            'processed_items': op['processed_items'],
            'progress_percentage': progress_pct,
            'elapsed_seconds': elapsed,
            'estimated_remaining_seconds': eta_seconds,
            'errors': op['errors'],
            'last_update': op['last_update'].isoformat()
        }
    
    def end_operation(self, operation_id: str):
        """End tracking for an operation."""
        if operation_id in self.operations:
            op = self.operations[operation_id]
            elapsed = (datetime.utcnow() - op['start_time']).total_seconds()
            logger.info(f"Completed operation {operation_id} in {elapsed:.2f} seconds")
            del self.operations[operation_id]


class PerformanceMonitor:
    """Monitor ETL performance metrics."""
    
    def __init__(self):
        self.operations = []
        self.memory_snapshots = []
    
    def record_operation(self, name: str, duration: float, memory_delta: float):
        """Record performance metrics for an operation."""
        self.operations.append({
            'name': name,
            'duration': duration,
            'memory_delta': memory_delta,
            'timestamp': datetime.utcnow()
        })
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        if not self.operations:
            return {}
        
        durations = [op['duration'] for op in self.operations]
        memory_deltas = [op['memory_delta'] for op in self.operations]
        
        return {
            'total_operations': len(self.operations),
            'avg_duration': np.mean(durations),
            'max_duration': np.max(durations),
            'min_duration': np.min(durations),
            'avg_memory_delta': np.mean(memory_deltas),
            'max_memory_delta': np.max(memory_deltas),
            'total_duration': np.sum(durations)
        }


class ETLErrorHandler:
    """Handle and log ETL errors."""
    
    def __init__(self):
        self.error_log = []
        self.critical_errors = []
    
    def handle_critical_error(self, error: Exception, context: str):
        """Handle critical errors that stop operations."""
        error_record = {
            'error': str(error),
            'context': context,
            'timestamp': datetime.utcnow(),
            'type': 'critical'
        }
        self.critical_errors.append(error_record)
        logger.critical(f"Critical error in {context}: {error}")
    
    def handle_record_error(self, error: Exception, record_id: str, context: str):
        """Handle individual record errors."""
        error_record = {
            'error': str(error),
            'record_id': record_id,
            'context': context,
            'timestamp': datetime.utcnow(),
            'type': 'record'
        }
        self.error_log.append(error_record)
        logger.warning(f"Record error for {record_id} in {context}: {error}")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of all errors."""
        return {
            'total_errors': len(self.error_log),
            'critical_errors': len(self.critical_errors),
            'recent_errors': self.error_log[-10:],  # Last 10 errors
            'critical_error_details': self.critical_errors
        }
