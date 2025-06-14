"""
Database optimization for large dataset operations.
Provides optimizations for handling 50GB+ datasets efficiently.
"""
import logging
from typing import Dict, List, Any, Optional
from sqlalchemy import text, Index, event
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
import time

from app.models.property import Property
from app.models.agent import Agent

logger = logging.getLogger(__name__)


class DatabaseOptimizer:
    """
    Database optimization service for large-scale operations.
    Provides performance tuning, indexing, and configuration optimization.
    """
    
    def __init__(self):
        self.connection_pool_settings = {
            'pool_size': 20,
            'max_overflow': 30,
            'pool_timeout': 30,
            'pool_recycle': 3600,
            'pool_pre_ping': True
        }
    
    def _get_db(self):
        """Get database instance from current Flask app context."""
        from app import db
        return db
    
    def optimize_for_bulk_operations(self) -> Dict[str, Any]:
        """
        Optimize database settings for bulk import/export operations.
        
        Returns:
            Dictionary with optimization results
        """
        logger.info("Starting database optimization for bulk operations")
        
        results = {
            'optimizations_applied': [],
            'performance_improvements': {},
            'recommendations': []
        }
        
        try:
            # MySQL specific optimizations
            if self._is_mysql():
                results.update(self._optimize_mysql_bulk_operations())
            
            # PostgreSQL specific optimizations
            elif self._is_postgresql():
                results.update(self._optimize_postgresql_bulk_operations())
            
            # Create/optimize indexes
            index_results = self._optimize_indexes()
            results['index_optimizations'] = index_results
            
            # Configure connection pooling
            pool_results = self._optimize_connection_pool()
            results['connection_pool'] = pool_results
            
            # Set query optimization hints
            query_results = self._set_query_optimizations()
            results['query_optimizations'] = query_results
            
            logger.info("Database optimization completed successfully")
            
        except Exception as e:
            logger.error(f"Database optimization failed: {str(e)}")
            results['error'] = str(e)
        
        return results
    
    def _is_mysql(self) -> bool:
        """Check if database is MySQL."""
        db = self._get_db()
        return db.engine.dialect.name == 'mysql'
    
    def _is_postgresql(self) -> bool:
        """Check if database is PostgreSQL."""
        db = self._get_db()
        return db.engine.dialect.name == 'postgresql'
    
    def _optimize_mysql_bulk_operations(self) -> Dict[str, Any]:
        """Apply MySQL-specific optimizations for bulk operations."""
        
        optimizations = []
        db = self._get_db()
        
        try:
            # Increase bulk insert buffer
            db.session.execute(text("SET GLOBAL innodb_buffer_pool_size = 2147483648"))  # 2GB
            optimizations.append("Increased InnoDB buffer pool size")
            
            # Optimize for bulk inserts
            db.session.execute(text("SET GLOBAL innodb_log_file_size = 512M"))
            optimizations.append("Increased InnoDB log file size")
            
            # Disable foreign key checks for bulk operations (temporarily)
            db.session.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            optimizations.append("Disabled foreign key checks")
            
            # Set bulk insert optimizations
            db.session.execute(text("SET GLOBAL bulk_insert_buffer_size = 256M"))
            optimizations.append("Increased bulk insert buffer size")
            
            # Optimize autocommit for bulk operations
            db.session.execute(text("SET autocommit = 0"))
            optimizations.append("Disabled autocommit for bulk operations")
            
            # Set innodb flush log at transaction commit
            db.session.execute(text("SET GLOBAL innodb_flush_log_at_trx_commit = 2"))
            optimizations.append("Optimized InnoDB transaction flushing")
            
            db.session.commit()
            
        except Exception as e:
            logger.warning(f"Some MySQL optimizations failed: {e}")
            db.session.rollback()
        
        return {
            'mysql_optimizations': optimizations,
            'recommendations': [
                "Consider increasing innodb_buffer_pool_size to 70-80% of available RAM",
                "Set innodb_log_file_size to 25% of innodb_buffer_pool_size",
                "Use innodb_flush_method = O_DIRECT for better I/O performance"
            ]
        }
    
    def _optimize_postgresql_bulk_operations(self) -> Dict[str, Any]:
        """Apply PostgreSQL-specific optimizations for bulk operations."""
        
        optimizations = []
        db = self._get_db()
        
        try:
            # Increase work memory for sorting operations
            db.session.execute(text("SET work_mem = '256MB'"))
            optimizations.append("Increased work memory for bulk operations")
            
            # Increase maintenance work memory
            db.session.execute(text("SET maintenance_work_mem = '512MB'"))
            optimizations.append("Increased maintenance work memory")
            
            # Optimize checkpoint settings
            db.session.execute(text("SET checkpoint_completion_target = 0.9"))
            optimizations.append("Optimized checkpoint completion target")
            
            # Set synchronous commit for bulk operations
            db.session.execute(text("SET synchronous_commit = off"))
            optimizations.append("Disabled synchronous commit for bulk operations")
            
            db.session.commit()
            
        except Exception as e:
            logger.warning(f"Some PostgreSQL optimizations failed: {e}")
            db.session.rollback()
        
        return {
            'postgresql_optimizations': optimizations,
            'recommendations': [
                "Consider increasing shared_buffers to 25% of available RAM",
                "Set effective_cache_size to 75% of available RAM",
                "Increase max_wal_size for large bulk operations"
            ]
        }
    
    def _optimize_indexes(self) -> Dict[str, Any]:
        """Create and optimize database indexes for better performance."""
        
        index_results = {
            'created_indexes': [],
            'optimized_indexes': [],
            'recommendations': []
        }
        
        try:
            # Property table indexes
            property_indexes = [
                {
                    'name': 'idx_property_search_optimized',
                    'table': 'properties',
                    'columns': ['city', 'province', 'property_type', 'sold_price'],
                    'description': 'Optimized index for property search queries'
                },
                {
                    'name': 'idx_property_location_optimized',
                    'table': 'properties',
                    'columns': ['latitude', 'longitude'],
                    'description': 'Spatial index for location-based queries'
                },
                {
                    'name': 'idx_property_price_range',
                    'table': 'properties',
                    'columns': ['sold_price', 'sqft'],
                    'description': 'Index for price and square footage filtering'
                },
                {
                    'name': 'idx_property_features',
                    'table': 'properties',
                    'columns': ['bedrooms', 'bathrooms', 'property_type'],
                    'description': 'Index for property feature filtering'
                },
                {
                    'name': 'idx_property_dates',
                    'table': 'properties',
                    'columns': ['sold_date', 'created_at'],
                    'description': 'Index for date-based queries'
                }
            ]
            
            # Create indexes if they don't exist
            for index_info in property_indexes:
                try:
                    # Check if index exists
                    index_check_sql = f"""
                    SELECT COUNT(*) as count 
                    FROM information_schema.statistics 
                    WHERE table_schema = DATABASE() 
                    AND table_name = '{index_info['table']}' 
                    AND index_name = '{index_info['name']}'
                    """
                    
                    result = db.session.execute(text(index_check_sql)).fetchone()
                    
                    if result.count == 0:
                        # Create index
                        columns_str = ', '.join(index_info['columns'])
                        create_index_sql = f"""
                        CREATE INDEX {index_info['name']} 
                        ON {index_info['table']} ({columns_str})
                        """
                        
                        db.session.execute(text(create_index_sql))
                        index_results['created_indexes'].append(index_info)
                        logger.info(f"Created index: {index_info['name']}")
                    else:
                        index_results['optimized_indexes'].append(index_info)
                
                except Exception as e:
                    logger.warning(f"Failed to create index {index_info['name']}: {e}")
            
            # Analyze tables after index creation
            if self._is_mysql():
                db.session.execute(text("ANALYZE TABLE properties"))
                db.session.execute(text("ANALYZE TABLE agents"))
            elif self._is_postgresql():
                db.session.execute(text("ANALYZE properties"))
                db.session.execute(text("ANALYZE agents"))
            
            db.session.commit()
            
            # Add recommendations
            index_results['recommendations'] = [
                "Consider partitioning large tables by date or region",
                "Monitor slow query log to identify additional indexing opportunities",
                "Use covering indexes for frequently accessed column combinations",
                "Consider composite indexes for multi-column WHERE clauses"
            ]
            
        except Exception as e:
            logger.error(f"Index optimization failed: {e}")
            db.session.rollback()
            index_results['error'] = str(e)
        
        return index_results
    
    def _optimize_connection_pool(self) -> Dict[str, Any]:
        """Optimize database connection pooling for high-throughput operations."""
        
        pool_results = {
            'current_settings': {},
            'optimized_settings': {},
            'recommendations': []
        }
        
        try:
            # Get current pool settings
            pool = db.engine.pool
            
            pool_results['current_settings'] = {
                'pool_size': getattr(pool, 'size', 'unknown'),
                'checked_out': getattr(pool, 'checkedout', 'unknown'),
                'overflow': getattr(pool, 'overflow', 'unknown'),
                'checked_in': getattr(pool, 'checkedin', 'unknown')
            }
            
            # Recommendations for pool optimization
            pool_results['recommendations'] = [
                f"Current pool size: {pool_results['current_settings']['pool_size']}",
                "For bulk operations, consider pool_size=20-50",
                "Set max_overflow=20-30 for peak load handling",
                "Use pool_pre_ping=True for connection health checks",
                "Set pool_recycle=3600 to prevent stale connections"
            ]
            
            pool_results['optimized_settings'] = self.connection_pool_settings
            
        except Exception as e:
            logger.warning(f"Connection pool optimization failed: {e}")
            pool_results['error'] = str(e)
        
        return pool_results
    
    def _set_query_optimizations(self) -> Dict[str, Any]:
        """Set database-specific query optimizations."""
        
        query_results = {
            'optimizations_applied': [],
            'recommendations': []
        }
        
        try:
            if self._is_mysql():
                # MySQL query optimizations
                optimizations = [
                    "SET SESSION query_cache_type = OFF",  # Disable query cache for bulk ops
                    "SET SESSION sql_mode = 'NO_AUTO_VALUE_ON_ZERO'",
                    "SET SESSION unique_checks = 0",  # Disable unique checks for bulk inserts
                ]
                
                for opt in optimizations:
                    try:
                        db.session.execute(text(opt))
                        query_results['optimizations_applied'].append(opt)
                    except Exception as e:
                        logger.warning(f"Failed to apply optimization {opt}: {e}")
            
            elif self._is_postgresql():
                # PostgreSQL query optimizations
                optimizations = [
                    "SET enable_seqscan = off",  # Force index usage where possible
                    "SET random_page_cost = 1.1",  # Optimize for SSD storage
                    "SET seq_page_cost = 1.0",
                ]
                
                for opt in optimizations:
                    try:
                        db.session.execute(text(opt))
                        query_results['optimizations_applied'].append(opt)
                    except Exception as e:
                        logger.warning(f"Failed to apply optimization {opt}: {e}")
            
            db.session.commit()
            
            query_results['recommendations'] = [
                "Use EXPLAIN ANALYZE to identify slow queries",
                "Consider query rewriting for better performance",
                "Use batch operations instead of individual INSERTs",
                "Implement query result caching for repeated operations"
            ]
            
        except Exception as e:
            logger.error(f"Query optimization failed: {e}")
            db.session.rollback()
            query_results['error'] = str(e)
        
        return query_results
    
    def restore_normal_operations(self) -> Dict[str, Any]:
        """
        Restore database settings to normal operation mode after bulk operations.
        
        Returns:
            Dictionary with restoration results
        """
        logger.info("Restoring database settings to normal operation mode")
        
        results = {
            'restored_settings': [],
            'warnings': []
        }
        
        try:
            if self._is_mysql():
                # Restore MySQL settings
                restore_commands = [
                    "SET FOREIGN_KEY_CHECKS = 1",
                    "SET autocommit = 1",
                    "SET GLOBAL innodb_flush_log_at_trx_commit = 1",
                    "SET SESSION unique_checks = 1"
                ]
                
                for cmd in restore_commands:
                    try:
                        db.session.execute(text(cmd))
                        results['restored_settings'].append(cmd)
                    except Exception as e:
                        results['warnings'].append(f"Failed to restore: {cmd} - {e}")
            
            elif self._is_postgresql():
                # Restore PostgreSQL settings
                restore_commands = [
                    "SET synchronous_commit = on",
                    "SET work_mem = '4MB'",
                    "SET maintenance_work_mem = '64MB'"
                ]
                
                for cmd in restore_commands:
                    try:
                        db.session.execute(text(cmd))
                        results['restored_settings'].append(cmd)
                    except Exception as e:
                        results['warnings'].append(f"Failed to restore: {cmd} - {e}")
            
            db.session.commit()
            logger.info("Database settings restored to normal operation mode")
            
        except Exception as e:
            logger.error(f"Failed to restore database settings: {e}")
            db.session.rollback()
            results['error'] = str(e)
        
        return results
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current database performance metrics."""
        
        metrics = {
            'connection_info': {},
            'table_statistics': {},
            'index_statistics': {},
            'performance_schema': {}
        }
        
        try:
            # Connection information
            if self._is_mysql():
                # MySQL performance metrics
                connection_info = db.session.execute(text("""
                    SHOW STATUS WHERE Variable_name IN (
                        'Connections', 'Threads_connected', 'Threads_running',
                        'Innodb_buffer_pool_read_requests', 'Innodb_buffer_pool_reads'
                    )
                """)).fetchall()
                
                metrics['connection_info'] = {row[0]: row[1] for row in connection_info}
                
                # Table statistics
                table_stats = db.session.execute(text("""
                    SELECT table_name, table_rows, data_length, index_length
                    FROM information_schema.tables
                    WHERE table_schema = DATABASE()
                    AND table_name IN ('properties', 'agents')
                """)).fetchall()
                
                metrics['table_statistics'] = [
                    {
                        'table': row[0],
                        'rows': row[1],
                        'data_size_mb': (row[2] or 0) / 1024 / 1024,
                        'index_size_mb': (row[3] or 0) / 1024 / 1024
                    }
                    for row in table_stats
                ]
            
            elif self._is_postgresql():
                # PostgreSQL performance metrics
                connection_info = db.session.execute(text("""
                    SELECT state, count(*) as count
                    FROM pg_stat_activity
                    WHERE datname = current_database()
                    GROUP BY state
                """)).fetchall()
                
                metrics['connection_info'] = {row[0]: row[1] for row in connection_info}
                
                # Table statistics
                table_stats = db.session.execute(text("""
                    SELECT schemaname, tablename, n_tup_ins, n_tup_upd, n_tup_del
                    FROM pg_stat_user_tables
                    WHERE tablename IN ('properties', 'agents')
                """)).fetchall()
                
                metrics['table_statistics'] = [
                    {
                        'schema': row[0],
                        'table': row[1],
                        'inserts': row[2],
                        'updates': row[3],
                        'deletes': row[4]
                    }
                    for row in table_stats
                ]
            
        except Exception as e:
            logger.warning(f"Failed to get performance metrics: {e}")
            metrics['error'] = str(e)
        
        return metrics
    
    def create_partitioning_strategy(self, table_name: str, partition_column: str) -> Dict[str, Any]:
        """
        Create partitioning strategy for large tables.
        
        Args:
            table_name: Name of the table to partition
            partition_column: Column to partition by (usually date)
        
        Returns:
            Dictionary with partitioning strategy
        """
        
        strategy = {
            'table_name': table_name,
            'partition_column': partition_column,
            'partition_type': 'RANGE',
            'partitions': [],
            'benefits': []
        }
        
        if table_name == 'properties' and partition_column == 'sold_date':
            # Create monthly partitions for the last 2 years and future
            import datetime
            
            current_date = datetime.date.today()
            start_date = current_date.replace(year=current_date.year - 2, month=1, day=1)
            
            # Generate monthly partitions
            partition_date = start_date
            while partition_date <= datetime.date(current_date.year + 1, 12, 31):
                next_month = partition_date.replace(day=28) + datetime.timedelta(days=4)
                next_month = next_month - datetime.timedelta(days=next_month.day-1)
                
                strategy['partitions'].append({
                    'name': f"{table_name}_p{partition_date.strftime('%Y%m')}",
                    'start_date': partition_date.strftime('%Y-%m-%d'),
                    'end_date': next_month.strftime('%Y-%m-%d')
                })
                
                partition_date = next_month
            
            strategy['benefits'] = [
                "Improved query performance for date range queries",
                "Faster data purging of old records",
                "Parallel processing of partitions",
                "Reduced index maintenance overhead"
            ]
        
        return strategy


# Event listeners for query logging and optimization
@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log slow queries for optimization analysis."""
    context._query_start_time = time.time()


@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log query execution time."""
    total = time.time() - context._query_start_time
    
    # Log queries that take longer than 1 second
    if total > 1.0:
        logger.warning(f"Slow query detected ({total:.2f}s): {statement[:200]}...")


class BulkOperationManager:
    """
    Context manager for bulk database operations.
    Automatically applies optimizations and restores settings.
    """
    
    def __init__(self):
        self.optimizer = DatabaseOptimizer()
        self.original_settings = None
    
    def __enter__(self):
        """Apply bulk operation optimizations."""
        logger.info("Starting bulk operation mode")
        self.optimizer.optimize_for_bulk_operations()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore normal operation settings."""
        logger.info("Exiting bulk operation mode")
        self.optimizer.restore_normal_operations()
        
        if exc_type:
            logger.error(f"Bulk operation failed: {exc_val}")
        
        return False  # Don't suppress exceptions
