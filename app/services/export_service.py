"""
Enhanced export service for NextProperty Real Estate Platform.
Supports multiple formats, filtering, and large dataset exports.
"""
import pandas as pd
import numpy as np
import json
import csv
import xlsxwriter
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
import asyncio
import aiofiles
from concurrent.futures import ThreadPoolExecutor
import logging
import tempfile
import zipfile
from sqlalchemy import text, and_, or_
from sqlalchemy.orm import Query

from app.models.property import Property
from app.models.agent import Agent
from app.models.economic_data import EconomicIndicator
from app.extensions import db
from app.services.etl_service import PerformanceMonitor

logger = logging.getLogger(__name__)


class EnhancedExportService:
    """
    Enhanced export service with support for:
    - Multiple formats (CSV, JSON, Excel, XML)
    - Large dataset streaming
    - Advanced filtering and querying
    - Data aggregation and reporting
    - Compressed exports
    """
    
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        self.supported_formats = ['csv', 'json', 'excel', 'xml', 'parquet']
        self.batch_size = 10000  # For large exports
    
    async def export_properties(
        self,
        format_type: str = 'csv',
        filters: Optional[Dict[str, Any]] = None,
        fields: Optional[List[str]] = None,
        output_path: Optional[str] = None,
        compress: bool = False,
        include_analytics: bool = False
    ) -> Dict[str, Any]:
        """
        Export property data with advanced filtering and format options.
        
        Args:
            format_type: Export format ('csv', 'json', 'excel', 'xml', 'parquet')
            filters: Dictionary of filters to apply
            fields: List of specific fields to export
            output_path: Custom output path
            compress: Whether to compress the output
            include_analytics: Include additional analytics data
        
        Returns:
            Dictionary with export results and file paths
        """
        logger.info(f"Starting property export: format={format_type}, filters={filters}")
        
        with self.performance_monitor.performance_context("property_export"):
            try:
                # Build query with filters
                query = self._build_property_query(filters)
                
                # Get total count for progress tracking
                total_count = query.count()
                logger.info(f"Exporting {total_count} properties")
                
                # Generate output filename
                if not output_path:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    output_path = f"/Users/efeobukohwo/Desktop/Nextproperty Real Estate/data/exports/properties_{timestamp}"
                
                # Export based on format
                format_type_safe = format_type.lower() if format_type else 'csv'
                if format_type_safe == 'csv':
                    result = await self._export_to_csv(query, output_path, fields, total_count)
                elif format_type_safe == 'json':
                    result = await self._export_to_json(query, output_path, fields, total_count)
                elif format_type_safe == 'excel':
                    result = await self._export_to_excel(query, output_path, fields, include_analytics)
                elif format_type_safe == 'xml':
                    result = await self._export_to_xml(query, output_path, fields, total_count)
                elif format_type_safe == 'parquet':
                    result = await self._export_to_parquet(query, output_path, fields, total_count)
                else:
                    raise ValueError(f"Unsupported export format: {format_type}")
                
                # Compress if requested
                if compress:
                    result = await self._compress_export(result)
                
                # Add metadata
                result.update({
                    'export_completed_at': datetime.utcnow().isoformat(),
                    'total_records': total_count,
                    'filters_applied': filters,
                    'fields_exported': fields,
                    'format': format_type,
                    'compressed': compress
                })
                
                logger.info(f"Export completed: {result['file_path']}")
                return result
                
            except Exception as e:
                logger.error(f"Export failed: {str(e)}")
                raise
    
    def _build_property_query(self, filters: Optional[Dict[str, Any]] = None) -> Query:
        """Build SQLAlchemy query with filters."""
        query = db.session.query(Property)
        
        if not filters:
            return query
        
        # Apply filters
        if 'city' in filters:
            if isinstance(filters['city'], list):
                query = query.filter(Property.city.in_(filters['city']))
            else:
                query = query.filter(Property.city.ilike(f"%{filters['city']}%"))
        
        if 'province' in filters:
            if isinstance(filters['province'], list):
                query = query.filter(Property.province.in_(filters['province']))
            else:
                query = query.filter(Property.province == filters['province'])
        
        if 'property_type' in filters:
            if isinstance(filters['property_type'], list):
                query = query.filter(Property.property_type.in_(filters['property_type']))
            else:
                query = query.filter(Property.property_type == filters['property_type'])
        
        if 'price_min' in filters:
            query = query.filter(Property.sold_price >= filters['price_min'])
        
        if 'price_max' in filters:
            query = query.filter(Property.sold_price <= filters['price_max'])
        
        if 'bedrooms_min' in filters:
            query = query.filter(Property.bedrooms >= filters['bedrooms_min'])
        
        if 'bedrooms_max' in filters:
            query = query.filter(Property.bedrooms <= filters['bedrooms_max'])
        
        if 'sqft_min' in filters:
            query = query.filter(Property.sqft >= filters['sqft_min'])
        
        if 'sqft_max' in filters:
            query = query.filter(Property.sqft <= filters['sqft_max'])
        
        if 'sold_date_start' in filters:
            query = query.filter(Property.sold_date >= filters['sold_date_start'])
        
        if 'sold_date_end' in filters:
            query = query.filter(Property.sold_date <= filters['sold_date_end'])
        
        if 'has_coordinates' in filters and filters['has_coordinates']:
            query = query.filter(
                and_(Property.latitude.isnot(None), Property.longitude.isnot(None))
            )
        
        # Add sorting
        sort_by = filters.get('sort_by', 'sold_date')
        sort_order = filters.get('sort_order', 'desc')
        
        if hasattr(Property, sort_by):
            column = getattr(Property, sort_by)
            sort_order_safe = sort_order.lower() if sort_order else 'desc'
            if sort_order_safe == 'desc':
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())
        
        return query
    
    async def _export_to_csv(
        self,
        query: Query,
        output_path: str,
        fields: Optional[List[str]],
        total_count: int
    ) -> Dict[str, Any]:
        """Export to CSV with streaming for large datasets."""
        
        file_path = f"{output_path}.csv"
        
        # Determine fields to export
        if fields:
            selected_fields = [f for f in fields if hasattr(Property, f)]
        else:
            selected_fields = [
                'listing_id', 'mls', 'property_type', 'address', 'city', 'province',
                'postal_code', 'latitude', 'longitude', 'sold_price', 'bedrooms',
                'bathrooms', 'sqft', 'lot_size', 'sold_date', 'dom', 'taxes',
                'maintenance_fee', 'ai_valuation', 'investment_score', 'risk_assessment'
            ]
        
        processed_count = 0
        
        async with aiofiles.open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            await f.write(','.join(selected_fields) + '\n')
            
            # Process in batches
            offset = 0
            while offset < total_count:
                batch = query.offset(offset).limit(self.batch_size).all()
                
                if not batch:
                    break
                
                for property_obj in batch:
                    row_data = []
                    for field in selected_fields:
                        value = getattr(property_obj, field, None)
                        # Convert to string and handle None values
                        if value is None:
                            row_data.append('')
                        elif isinstance(value, (date, datetime)):
                            row_data.append(value.isoformat())
                        else:
                            row_data.append(str(value))
                    
                    # Write row
                    await f.write(','.join(f'"{val}"' for val in row_data) + '\n')
                    processed_count += 1
                
                offset += self.batch_size
                
                # Log progress
                if processed_count % 10000 == 0:
                    logger.info(f"Exported {processed_count}/{total_count} records to CSV")
        
        return {
            'file_path': file_path,
            'format': 'csv',
            'records_exported': processed_count,
            'file_size_mb': Path(file_path).stat().st_size / (1024 * 1024)
        }
    
    async def _export_to_json(
        self,
        query: Query,
        output_path: str,
        fields: Optional[List[str]],
        total_count: int
    ) -> Dict[str, Any]:
        """Export to JSON with streaming."""
        
        file_path = f"{output_path}.json"
        
        processed_count = 0
        
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write('[\n')
            
            offset = 0
            first_record = True
            
            while offset < total_count:
                batch = query.offset(offset).limit(self.batch_size).all()
                
                if not batch:
                    break
                
                for property_obj in batch:
                    # Convert to dictionary
                    if fields:
                        record_dict = {
                            field: self._serialize_value(getattr(property_obj, field, None))
                            for field in fields if hasattr(property_obj, field)
                        }
                    else:
                        record_dict = self._property_to_dict(property_obj)
                    
                    # Write record
                    if not first_record:
                        await f.write(',\n')
                    
                    json_str = json.dumps(record_dict, indent=2, default=str)
                    await f.write(json_str)
                    
                    first_record = False
                    processed_count += 1
                
                offset += self.batch_size
                
                # Log progress
                if processed_count % 10000 == 0:
                    logger.info(f"Exported {processed_count}/{total_count} records to JSON")
            
            await f.write('\n]')
        
        return {
            'file_path': file_path,
            'format': 'json',
            'records_exported': processed_count,
            'file_size_mb': Path(file_path).stat().st_size / (1024 * 1024)
        }
    
    async def _export_to_excel(
        self,
        query: Query,
        output_path: str,
        fields: Optional[List[str]],
        include_analytics: bool = False
    ) -> Dict[str, Any]:
        """Export to Excel with multiple sheets."""
        
        file_path = f"{output_path}.xlsx"
        
        # Use ThreadPoolExecutor for CPU-bound Excel operations
        with ThreadPoolExecutor(max_workers=1) as executor:
            result = await asyncio.get_event_loop().run_in_executor(
                executor,
                self._create_excel_file,
                query, file_path, fields, include_analytics
            )
        
        return result
    
    def _create_excel_file(
        self,
        query: Query,
        file_path: str,
        fields: Optional[List[str]],
        include_analytics: bool
    ) -> Dict[str, Any]:
        """Create Excel file with multiple sheets."""
        
        workbook = xlsxwriter.Workbook(file_path)
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D7E4BC',
            'border': 1
        })
        
        currency_format = workbook.add_format({'num_format': '$#,##0.00'})
        date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})
        
        # Main data sheet
        worksheet = workbook.add_worksheet('Property Data')
        
        # Determine fields
        if fields:
            selected_fields = [f for f in fields if hasattr(Property, f)]
        else:
            selected_fields = [
                'listing_id', 'mls', 'property_type', 'address', 'city', 'province',
                'postal_code', 'latitude', 'longitude', 'sold_price', 'bedrooms',
                'bathrooms', 'sqft', 'lot_size', 'sold_date', 'dom', 'taxes',
                'maintenance_fee', 'ai_valuation', 'investment_score', 'risk_assessment'
            ]
        
        # Write headers
        for col, field in enumerate(selected_fields):
            worksheet.write(0, col, field.replace('_', ' ').title(), header_format)
        
        # Write data
        row = 1
        processed_count = 0
        offset = 0
        
        while True:
            batch = query.offset(offset).limit(self.batch_size).all()
            
            if not batch:
                break
            
            for property_obj in batch:
                for col, field in enumerate(selected_fields):
                    value = getattr(property_obj, field, None)
                    
                    if value is None:
                        worksheet.write(row, col, '')
                    elif field in ['sold_price', 'ai_valuation', 'taxes', 'maintenance_fee']:
                        worksheet.write(row, col, float(value) if value else 0, currency_format)
                    elif field == 'sold_date':
                        if value:
                            worksheet.write(row, col, value, date_format)
                        else:
                            worksheet.write(row, col, '')
                    else:
                        worksheet.write(row, col, str(value))
                
                row += 1
                processed_count += 1
            
            offset += self.batch_size
        
        # Auto-adjust column widths
        for col, field in enumerate(selected_fields):
            worksheet.set_column(col, col, max(len(field) + 2, 12))
        
        # Add analytics sheet if requested
        if include_analytics:
            self._add_analytics_sheet(workbook, query)
        
        # Add summary sheet
        self._add_summary_sheet(workbook, query, processed_count)
        
        workbook.close()
        
        return {
            'file_path': file_path,
            'format': 'excel',
            'records_exported': processed_count,
            'file_size_mb': Path(file_path).stat().st_size / (1024 * 1024),
            'sheets': ['Property Data', 'Summary'] + (['Analytics'] if include_analytics else [])
        }
    
    def _add_analytics_sheet(self, workbook, query: Query):
        """Add analytics sheet to Excel workbook."""
        worksheet = workbook.add_worksheet('Analytics')
        
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC'})
        
        # Price analytics
        worksheet.write(0, 0, 'Price Analytics', header_format)
        
        # Calculate statistics
        price_stats = db.session.query(
            db.func.avg(Property.sold_price).label('avg_price'),
            db.func.min(Property.sold_price).label('min_price'),
            db.func.max(Property.sold_price).label('max_price'),
            db.func.count(Property.listing_id).label('total_count')
        ).filter(Property.sold_price.isnot(None)).first()
        
        if price_stats:
            worksheet.write(1, 0, 'Average Price:')
            worksheet.write(1, 1, float(price_stats.avg_price or 0))
            worksheet.write(2, 0, 'Minimum Price:')
            worksheet.write(2, 1, float(price_stats.min_price or 0))
            worksheet.write(3, 0, 'Maximum Price:')
            worksheet.write(3, 1, float(price_stats.max_price or 0))
            worksheet.write(4, 0, 'Total Properties:')
            worksheet.write(4, 1, price_stats.total_count or 0)
        
        # Property type distribution
        worksheet.write(6, 0, 'Property Type Distribution', header_format)
        
        type_stats = db.session.query(
            Property.property_type,
            db.func.count(Property.listing_id).label('count'),
            db.func.avg(Property.sold_price).label('avg_price')
        ).group_by(Property.property_type).all()
        
        worksheet.write(7, 0, 'Property Type')
        worksheet.write(7, 1, 'Count')
        worksheet.write(7, 2, 'Average Price')
        
        for i, stat in enumerate(type_stats, 8):
            worksheet.write(i, 0, stat.property_type or 'Unknown')
            worksheet.write(i, 1, stat.count)
            worksheet.write(i, 2, float(stat.avg_price or 0))
    
    def _add_summary_sheet(self, workbook, query: Query, record_count: int):
        """Add summary sheet to Excel workbook."""
        worksheet = workbook.add_worksheet('Summary')
        
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC'})
        
        worksheet.write(0, 0, 'Export Summary', header_format)
        worksheet.write(1, 0, 'Export Date:')
        worksheet.write(1, 1, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        worksheet.write(2, 0, 'Total Records:')
        worksheet.write(2, 1, record_count)
        
        # Add filter information if applicable
        worksheet.write(4, 0, 'Data Source: NextProperty Real Estate Platform')
        worksheet.write(5, 0, 'Generated by: Enhanced Export Service')
    
    async def _export_to_xml(
        self,
        query: Query,
        output_path: str,
        fields: Optional[List[str]],
        total_count: int
    ) -> Dict[str, Any]:
        """Export to XML format."""
        
        file_path = f"{output_path}.xml"
        
        processed_count = 0
        
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            await f.write('<properties>\n')
            
            offset = 0
            while offset < total_count:
                batch = query.offset(offset).limit(self.batch_size).all()
                
                if not batch:
                    break
                
                for property_obj in batch:
                    await f.write('  <property>\n')
                    
                    # Write fields
                    export_fields = fields or [
                        'listing_id', 'property_type', 'address', 'city', 'province',
                        'sold_price', 'bedrooms', 'bathrooms', 'sqft'
                    ]
                    
                    for field in export_fields:
                        if hasattr(property_obj, field):
                            value = getattr(property_obj, field)
                            if value is not None:
                                # Escape XML special characters
                                value_str = str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                                await f.write(f'    <{field}>{value_str}</{field}>\n')
                    
                    await f.write('  </property>\n')
                    processed_count += 1
                
                offset += self.batch_size
                
                if processed_count % 10000 == 0:
                    logger.info(f"Exported {processed_count}/{total_count} records to XML")
            
            await f.write('</properties>\n')
        
        return {
            'file_path': file_path,
            'format': 'xml',
            'records_exported': processed_count,
            'file_size_mb': Path(file_path).stat().st_size / (1024 * 1024)
        }
    
    async def _export_to_parquet(
        self,
        query: Query,
        output_path: str,
        fields: Optional[List[str]],
        total_count: int
    ) -> Dict[str, Any]:
        """Export to Parquet format for analytics."""
        
        file_path = f"{output_path}.parquet"
        
        # Convert to pandas DataFrame and save as Parquet
        with ThreadPoolExecutor(max_workers=1) as executor:
            result = await asyncio.get_event_loop().run_in_executor(
                executor,
                self._create_parquet_file,
                query, file_path, fields
            )
        
        return result
    
    def _create_parquet_file(
        self,
        query: Query,
        file_path: str,
        fields: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Create Parquet file using pandas."""
        
        # Read data in chunks and build DataFrame
        all_data = []
        offset = 0
        
        while True:
            batch = query.offset(offset).limit(self.batch_size).all()
            
            if not batch:
                break
            
            batch_data = []
            for property_obj in batch:
                if fields:
                    record_dict = {
                        field: self._serialize_value(getattr(property_obj, field, None))
                        for field in fields if hasattr(property_obj, field)
                    }
                else:
                    record_dict = self._property_to_dict(property_obj)
                
                batch_data.append(record_dict)
            
            all_data.extend(batch_data)
            offset += self.batch_size
        
        # Create DataFrame and save as Parquet
        df = pd.DataFrame(all_data)
        df.to_parquet(file_path, compression='snappy')
        
        return {
            'file_path': file_path,
            'format': 'parquet',
            'records_exported': len(all_data),
            'file_size_mb': Path(file_path).stat().st_size / (1024 * 1024)
        }
    
    async def _compress_export(self, export_result: Dict[str, Any]) -> Dict[str, Any]:
        """Compress the exported file."""
        
        original_path = export_result['file_path']
        zip_path = f"{original_path}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(original_path, Path(original_path).name)
        
        # Remove original file
        Path(original_path).unlink()
        
        export_result.update({
            'file_path': zip_path,
            'compressed': True,
            'original_size_mb': export_result['file_size_mb'],
            'compressed_size_mb': Path(zip_path).stat().st_size / (1024 * 1024)
        })
        
        return export_result
    
    def _property_to_dict(self, property_obj: Property) -> Dict[str, Any]:
        """Convert Property object to dictionary."""
        return {
            'listing_id': property_obj.listing_id,
            'mls': property_obj.mls,
            'property_type': property_obj.property_type,
            'address': property_obj.address,
            'city': property_obj.city,
            'province': property_obj.province,
            'postal_code': property_obj.postal_code,
            'latitude': self._serialize_value(property_obj.latitude),
            'longitude': self._serialize_value(property_obj.longitude),
            'sold_price': self._serialize_value(property_obj.sold_price),
            'bedrooms': property_obj.bedrooms,
            'bathrooms': self._serialize_value(property_obj.bathrooms),
            'sqft': property_obj.sqft,
            'lot_size': self._serialize_value(property_obj.lot_size),
            'sold_date': property_obj.sold_date.isoformat() if property_obj.sold_date else None,
            'dom': property_obj.dom,
            'taxes': self._serialize_value(property_obj.taxes),
            'maintenance_fee': self._serialize_value(property_obj.maintenance_fee),
            'features': property_obj.features,
            'community_features': property_obj.community_features,
            'remarks': property_obj.remarks,
            'ai_valuation': self._serialize_value(property_obj.ai_valuation),
            'investment_score': self._serialize_value(property_obj.investment_score),
            'risk_assessment': property_obj.risk_assessment,
            'market_trend': property_obj.market_trend,
            'created_at': property_obj.created_at.isoformat() if property_obj.created_at else None,
            'updated_at': property_obj.updated_at.isoformat() if property_obj.updated_at else None
        }
    
    def _serialize_value(self, value: Any) -> Any:
        """Serialize value for JSON/export compatibility."""
        if value is None:
            return None
        elif isinstance(value, (date, datetime)):
            return value.isoformat()
        elif hasattr(value, '__float__'):  # Decimal types
            return float(value)
        else:
            return value
    
    async def export_market_report(
        self,
        city: Optional[str] = None,
        province: Optional[str] = None,
        date_range: Optional[Tuple[date, date]] = None,
        output_format: str = 'excel'
    ) -> Dict[str, Any]:
        """Generate comprehensive market report."""
        
        logger.info(f"Generating market report for {city or 'All Cities'}, {province or 'All Provinces'}")
        
        # Build base query
        query = db.session.query(Property)
        
        if city:
            query = query.filter(Property.city.ilike(f"%{city}%"))
        if province:
            query = query.filter(Property.province == province)
        if date_range:
            query = query.filter(
                and_(
                    Property.sold_date >= date_range[0],
                    Property.sold_date <= date_range[1]
                )
            )
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        location_suffix = f"_{city}_{province}" if city or province else "_all_markets"
        output_path = f"/Users/efeobukohwo/Desktop/Nextproperty Real Estate/data/exports/market_report{location_suffix}_{timestamp}"
        
        output_format = output_format or 'excel'  # Default to excel if None
        if output_format.lower() == 'excel':
            return await self._generate_excel_market_report(query, output_path, city, province)
        else:
            # Fall back to regular export
            return await self.export_properties(
                format_type=output_format,
                filters={'city': city, 'province': province} if city or province else None,
                output_path=output_path,
                include_analytics=True
            )
    
    async def _generate_excel_market_report(
        self,
        query: Query,
        output_path: str,
        city: Optional[str],
        province: Optional[str]
    ) -> Dict[str, Any]:
        """Generate comprehensive Excel market report."""
        
        file_path = f"{output_path}.xlsx"
        
        with ThreadPoolExecutor(max_workers=1) as executor:
            result = await asyncio.get_event_loop().run_in_executor(
                executor,
                self._create_market_report_excel,
                query, file_path, city, province
            )
        
        return result
    
    def _create_market_report_excel(
        self,
        query: Query,
        file_path: str,
        city: Optional[str],
        province: Optional[str]
    ) -> Dict[str, Any]:
        """Create comprehensive Excel market report."""
        
        workbook = xlsxwriter.Workbook(file_path)
        
        # Define formats
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'bg_color': '#1F4E79',
            'font_color': 'white',
            'align': 'center'
        })
        
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D7E4BC',
            'border': 1,
            'align': 'center'
        })
        
        currency_format = workbook.add_format({'num_format': '$#,##0'})
        percent_format = workbook.add_format({'num_format': '0.0%'})
        
        # Summary sheet
        summary_ws = workbook.add_worksheet('Executive Summary')
        
        # Title
        summary_ws.merge_range(0, 0, 0, 5, 'NextProperty Market Report', title_format)
        
        # Report details
        summary_ws.write(2, 0, 'Report Generated:', header_format)
        summary_ws.write(2, 1, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        if city:
            summary_ws.write(3, 0, 'City:', header_format)
            summary_ws.write(3, 1, city)
        
        if province:
            summary_ws.write(4, 0, 'Province:', header_format)
            summary_ws.write(4, 1, province)
        
        # Market statistics
        total_properties = query.count()
        avg_price = query.with_entities(db.func.avg(Property.sold_price)).scalar() or 0
        
        summary_ws.write(6, 0, 'Total Properties:', header_format)
        summary_ws.write(6, 1, total_properties)
        summary_ws.write(7, 0, 'Average Price:', header_format)
        summary_ws.write(7, 1, float(avg_price), currency_format)
        
        # Property type breakdown
        self._add_property_type_sheet(workbook, query)
        
        # Price trends
        self._add_price_trends_sheet(workbook, query)
        
        # Geographic analysis
        self._add_geographic_sheet(workbook, query)
        
        workbook.close()
        
        return {
            'file_path': file_path,
            'format': 'excel_report',
            'report_type': 'market_analysis',
            'total_properties_analyzed': total_properties,
            'file_size_mb': Path(file_path).stat().st_size / (1024 * 1024),
            'sheets': ['Executive Summary', 'Property Types', 'Price Trends', 'Geographic Analysis']
        }
    
    def _add_property_type_sheet(self, workbook, query: Query):
        """Add property type analysis sheet."""
        worksheet = workbook.add_worksheet('Property Types')
        
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC'})
        currency_format = workbook.add_format({'num_format': '$#,##0'})
        
        # Headers
        headers = ['Property Type', 'Count', 'Percentage', 'Avg Price', 'Min Price', 'Max Price']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Data
        type_stats = db.session.query(
            Property.property_type,
            db.func.count(Property.listing_id).label('count'),
            db.func.avg(Property.sold_price).label('avg_price'),
            db.func.min(Property.sold_price).label('min_price'),
            db.func.max(Property.sold_price).label('max_price')
        ).filter(Property.sold_price.isnot(None)).group_by(Property.property_type).all()
        
        total_count = sum(stat.count for stat in type_stats)
        
        for row, stat in enumerate(type_stats, 1):
            worksheet.write(row, 0, stat.property_type or 'Unknown')
            worksheet.write(row, 1, stat.count)
            worksheet.write(row, 2, stat.count / total_count if total_count > 0 else 0)
            worksheet.write(row, 3, float(stat.avg_price or 0), currency_format)
            worksheet.write(row, 4, float(stat.min_price or 0), currency_format)
            worksheet.write(row, 5, float(stat.max_price or 0), currency_format)
        
        # Auto-adjust columns
        for col in range(len(headers)):
            worksheet.set_column(col, col, 15)
    
    def _add_price_trends_sheet(self, workbook, query: Query):
        """Add price trends analysis sheet."""
        worksheet = workbook.add_worksheet('Price Trends')
        
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC'})
        
        worksheet.write(0, 0, 'Price trend analysis would be implemented here', header_format)
        worksheet.write(1, 0, 'This would include monthly/quarterly price movements')
        worksheet.write(2, 0, 'Year-over-year comparisons')
        worksheet.write(3, 0, 'Seasonal patterns')
    
    def _add_geographic_sheet(self, workbook, query: Query):
        """Add geographic analysis sheet."""
        worksheet = workbook.add_worksheet('Geographic Analysis')
        
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC'})
        currency_format = workbook.add_format({'num_format': '$#,##0'})
        
        # City-level analysis
        headers = ['City', 'Count', 'Avg Price', 'Price per SqFt']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        city_stats = db.session.query(
            Property.city,
            db.func.count(Property.listing_id).label('count'),
            db.func.avg(Property.sold_price).label('avg_price'),
            (db.func.avg(Property.sold_price) / db.func.avg(Property.sqft)).label('price_per_sqft')
        ).filter(
            and_(Property.sold_price.isnot(None), Property.sqft.isnot(None))
        ).group_by(Property.city).order_by(
            db.func.count(Property.listing_id).desc()
        ).limit(50).all()
        
        for row, stat in enumerate(city_stats, 1):
            worksheet.write(row, 0, stat.city or 'Unknown')
            worksheet.write(row, 1, stat.count)
            worksheet.write(row, 2, float(stat.avg_price or 0), currency_format)
            worksheet.write(row, 3, float(stat.price_per_sqft or 0), currency_format)
        
        # Auto-adjust columns
        for col in range(len(headers)):
            worksheet.set_column(col, col, 15)
