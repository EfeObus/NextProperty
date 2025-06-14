# ========================
# BANK OF CANADA API INTEGRATION
# ========================

import requests
import json
from datetime import datetime, timedelta
import time

print("\n" + "=" * 40)
print("BANK OF CANADA API INTEGRATION")
print("=" * 40)

class BankOfCanadaAPI:
    """
    Bank of Canada API client for fetching economic indicators
    API Documentation: https://www.bankofcanada.ca/valet/docs
    """

    def __init__(self):
        self.base_url = "https://www.bankofcanada.ca/valet"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Real-Estate-ML-Pipeline/1.0',
            'Accept': 'application/json'
        })

    def fetch_series(self, series_name, start_date=None, end_date=None, retry_count=3):
        """
        Fetch time series data from Bank of Canada

        Parameters:
        - series_name: BoC series code (e.g., 'V80691311' for policy rate)
        - start_date: Start date in YYYY-MM-DD format
        - end_date: End date in YYYY-MM-DD format
        """
        try:
            # Construct URL with proper format
            url = f"{self.base_url}/observations/{series_name}/json"

            # Add date parameters if provided
            params = {}
            if start_date:
                params['start_date'] = start_date
            if end_date:
                params['end_date'] = end_date

            print(f"   Requesting: {url} with params: {params}")

            for attempt in range(retry_count):
                try:
                    response = self.session.get(url, params=params, timeout=30)

                    # Log response details for debugging
                    print(f"   Response status: {response.status_code}")

                    if response.status_code == 404:
                        print(f"   ✗ Series {series_name} not found (404). This series may be discontinued or the code is incorrect.")
                        return pd.DataFrame()

                    response.raise_for_status()

                    data = response.json()

                    # Extract observations
                    if 'observations' in data:
                        observations = data['observations']
                        df = pd.DataFrame(observations)

                        if not df.empty:
                            df['date'] = pd.to_datetime(df['d'])

                            # Handle the nested value structure: series_name: {"v": "value"}
                            if series_name in df.columns:
                                # Extract the value from the nested structure
                                df['value'] = df[series_name].apply(lambda x: float(x.get('v', 0)) if isinstance(x, dict) and x.get('v') is not None else None)
                                df = df[['date', 'value']].dropna()
                                df = df.sort_values('date')
                                return df
                            else:
                                print(f"   ⚠ Series column {series_name} not found in response")
                                print(f"   Available columns: {list(df.columns)}")
                                return pd.DataFrame()
                        else:
                            print(f"   ⚠ No data returned for series {series_name}")
                            return pd.DataFrame()
                    else:
                        print(f"   ⚠ No observations found for series {series_name}")
                        print(f"   Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                        return pd.DataFrame()

                except requests.exceptions.RequestException as e:
                    if attempt < retry_count - 1:
                        print(f"   ⚠ Attempt {attempt + 1} failed for {series_name}, retrying...")
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    else:
                        print(f"   ✗ Failed to fetch {series_name} after {retry_count} attempts: {e}")
                        return pd.DataFrame()

        except Exception as e:
            print(f"   ✗ Error fetching series {series_name}: {e}")
            return pd.DataFrame()

    def get_latest_value(self, df):
        """Get the most recent value from a time series"""
        if df.empty:
            return None
        return df.iloc[-1]['value']

    def get_value_by_date(self, df, target_date):
        """Get value closest to target date"""
        if df.empty:
            return None

        df['date_diff'] = abs((df['date'] - pd.to_datetime(target_date)).dt.days)
        closest_idx = df['date_diff'].idxmin()
        return df.loc[closest_idx, 'value']

def fetch_economic_indicators():
    """
    Fetch key economic indicators from Bank of Canada
    Returns dictionary with current and historical values
    """

    boc = BankOfCanadaAPI()

    # Define key economic series with updated codes
    # Reference: https://www.bankofcanada.ca/rates/interest-rates/
    series_config = {
        'policy_rate': {
            'code': 'V39079',  # Target for the overnight rate
            'name': 'Bank of Canada Overnight Rate Target'
        },
        'prime_rate': {
            'code': 'V80691311',  # Prime rate
            'name': 'Prime Business Rate'
        },
        'mortgage_5yr': {
            'code': 'V80691335',  # 5-year conventional mortgage
            'name': '5-Year Conventional Mortgage Rate'
        },
        'govt_bond_3_5yr': {
            'code': 'V122485',  # Government of Canada marketable bonds - average yield - 3-5 year
            'name': '3-5 Year Government Bond Yield'
        },
        'exchange_rate_usd': {
            'code': 'FXUSDCAD',  # USD/CAD exchange rate (noon rate)
            'name': 'USD/CAD Exchange Rate'
        },
        'prime_rate_alt': {
            'code': 'V122495',  # Alternative Prime rate series
            'name': 'Prime Rate (Alternative Series)'
        }
    }

    # Calculate date range (last 5 years for trend analysis)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365*5)).strftime('%Y-%m-%d')

    economic_data = {}
    economic_trends = {}

    print(f"Fetching economic data from {start_date} to {end_date}...")

    for key, config in series_config.items():
        print(f"   Fetching {config['name']} ({config['code']})...")

        # Fetch time series data
        df = boc.fetch_series(config['code'], start_date, end_date)

        if not df.empty:
            # Current value
            current_value = boc.get_latest_value(df)
            economic_data[f'current_{key}'] = current_value

            # Calculate trends (6-month and 1-year changes)
            six_months_ago = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
            one_year_ago = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

            value_6m_ago = boc.get_value_by_date(df, six_months_ago)
            value_1y_ago = boc.get_value_by_date(df, one_year_ago)

            if value_6m_ago is not None:
                economic_data[f'{key}_6m_change'] = current_value - value_6m_ago
                economic_data[f'{key}_6m_change_pct'] = ((current_value - value_6m_ago) / value_6m_ago) * 100 if value_6m_ago != 0 else 0

            if value_1y_ago is not None:
                economic_data[f'{key}_1y_change'] = current_value - value_1y_ago
                economic_data[f'{key}_1y_change_pct'] = ((current_value - value_1y_ago) / value_1y_ago) * 100 if value_1y_ago != 0 else 0

            # Store full time series for later analysis
            economic_trends[key] = df

            print(f"   ✓ {config['name']}: Current = {current_value:.3f}%")
        else:
            print(f"   ✗ Failed to fetch data for {config['name']}")
            # Set default values
            economic_data[f'current_{key}'] = None

    return economic_data, economic_trends

# Fetch economic indicators
try:
    economic_indicators, economic_time_series = fetch_economic_indicators()
    print(f"\n✓ Successfully fetched {len([k for k, v in economic_indicators.items() if v is not None])} economic indicators")

    # Display summary
    print("\nEconomic Indicators Summary:")
    print("-" * 50)
    current_indicators = {k: v for k, v in economic_indicators.items() if k.startswith('current_') and v is not None}
    for key, value in current_indicators.items():
        indicator_name = key.replace('current_', '').replace('_', ' ').title()
        print(f"{indicator_name:<25}: {value:8.3f}%")

except Exception as e:
    print(f"\n✗ Error fetching economic indicators: {e}")
    # Create empty economic data as fallback
    economic_indicators = {}
    economic_time_series = {}
    
    
# ========================
# STATISTICS CANADA API INTEGRATION
# ========================

print("\n" + "=" * 40)
print("STATISTICS CANADA API INTEGRATION")
print("=" * 40)

class StatCanDataFetcher:
    """
    A class to fetch economic indicators from Statistics Canada API
    API Documentation: https://www.statcan.gc.ca/en/developers
    """

    def __init__(self):
        self.base_url = "https://www150.statcan.gc.ca/t1/wds/rest"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Real-Estate-ML-Pipeline/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

    def get_table_data(self, table_id, coordinate_filters=None, start_date=None, end_date=None, retry_count=3):
        """
        Fetch data from a StatCan table using the WDS REST API

        Args:
            table_id (str): StatCan table ID (e.g., '14-10-0287-01')
            coordinate_filters (dict): Filters to apply to the data
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format

        Returns:
            pandas.DataFrame: Processed data
        """
        url = f"{self.base_url}/getDataFromVectorsAndLatestNPeriods"

        # Default filters if none provided
        if coordinate_filters is None:
            coordinate_filters = {}

        # Build request payload
        payload = [
            {
                "productId": table_id.replace('-', ''),
                "coordinate": coordinate_filters,
                "latestN": 120  # Get last 120 periods (about 10 years monthly data)
            }
        ]

        for attempt in range(retry_count):
            try:
                print(f"   Fetching table {table_id} (attempt {attempt + 1}/{retry_count})...")
                response = self.session.post(url, json=payload, timeout=60)

                print(f"   Response status: {response.status_code}")

                if response.status_code == 406:
                    print(f"   ✗ 406 Error for table {table_id}. Trying alternative method...")
                    return self._get_table_data_alternative(table_id, start_date, end_date)

                response.raise_for_status()

                data = response.json()

                if not data or len(data) == 0:
                    print(f"   ⚠ No data returned for table {table_id}")
                    return None

                # Process the response data
                df = self._process_statcan_response(data[0] if isinstance(data, list) else data)

                if df is not None and not df.empty:
                    # Filter by date range if provided
                    if start_date or end_date:
                        df['REF_DATE'] = pd.to_datetime(df['REF_DATE'])
                        if start_date:
                            df = df[df['REF_DATE'] >= start_date]
                        if end_date:
                            df = df[df['REF_DATE'] <= end_date]

                    print(f"   ✓ Successfully fetched {len(df)} records from table {table_id}")
                    return df
                else:
                    print(f"   ⚠ No data processed for table {table_id}")
                    return None

            except requests.exceptions.RequestException as e:
                if attempt < retry_count - 1:
                    print(f"   ⚠ Attempt {attempt + 1} failed for table {table_id}, retrying...")
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    print(f"   ✗ Failed to fetch table {table_id} after {retry_count} attempts: {e}")
                    return None
            except Exception as e:
                print(f"   ✗ Error processing table {table_id}: {e}")
                return None

    def _get_table_data_alternative(self, table_id, start_date=None, end_date=None):
        """
        Alternative method using the getAllCubesListLite endpoint
        """
        try:
            # Try getting specific vectors/series instead of full table
            if table_id == "36-10-0104-01":
                # GDP data - use specific vector
                return self._get_gdp_by_vector()
            elif table_id == "14-10-0287-01":
                # Employment data - use specific vectors
                return self._get_employment_by_vector()
            elif table_id == "18-10-0004-01":
                # CPI data - use specific vector
                return self._get_cpi_by_vector()
            else:
                print(f"   ⚠ No alternative method available for table {table_id}")
                return None
        except Exception as e:
            print(f"   ✗ Alternative method failed for table {table_id}: {e}")
            return None

    def _get_gdp_by_vector(self):
        """Get GDP data using vector ID"""
        try:
            url = f"{self.base_url}/getDataFromVectorsAndLatestNPeriods"
            payload = [
                {
                    "vectorId": 65201210,  # GDP at market prices, chained 2017 dollars, seasonally adjusted
                    "latestN": 40  # About 10 years of quarterly data
                }
            ]

            response = self.session.post(url, json=payload, timeout=60)
            response.raise_for_status()

            data = response.json()
            if data and len(data) > 0:
                return self._process_vector_response(data[0], 'GDP_Billions_CAD')
            return None
        except Exception as e:
            print(f"   ✗ Error fetching GDP vector: {e}")
            return None

    def _get_employment_by_vector(self):
        """Get employment data using vector IDs"""
        try:
            url = f"{self.base_url}/getDataFromVectorsAndLatestNPeriods"
            payload = [
                {
                    "vectorId": 2135091,  # Employment rate (alternative series)
                    "latestN": 60  # 5 years of monthly data
                },
                {
                    "vectorId": 3579270,  # Unemployment rate, Canada, both sexes, 15 years and over
                    "latestN": 60
                }
            ]

            response = self.session.post(url, json=payload, timeout=60)
            response.raise_for_status()

            data = response.json()
            if data and len(data) >= 2:
                emp_df = self._process_vector_response(data[0], 'Employment_Rate')
                unemp_df = self._process_vector_response(data[1], 'Unemployment_Rate')

                if emp_df is not None and unemp_df is not None:
                    merged = pd.merge(emp_df, unemp_df, on='REF_DATE', how='outer')
                    return merged
                elif unemp_df is not None:
                    # If only unemployment data available, return that
                    return unemp_df
                elif emp_df is not None:
                    # If only employment data available, return that
                    return emp_df
            return None
        except Exception as e:
            print(f"   ✗ Error fetching employment vectors: {e}")
            return None

    def _get_cpi_by_vector(self):
        """Get CPI data using vector ID"""
        try:
            url = f"{self.base_url}/getDataFromVectorsAndLatestNPeriods"
            payload = [
                {
                    "vectorId": 41690973,  # Consumer Price Index, all-items, Canada
                    "latestN": 60  # 5 years of monthly data
                }
            ]

            response = self.session.post(url, json=payload, timeout=60)
            response.raise_for_status()

            data = response.json()
            if data and len(data) > 0:
                df = self._process_vector_response(data[0], 'CPI')
                if df is not None:
                    # Calculate inflation rate
                    df['Inflation_Rate'] = df['CPI'].pct_change(periods=12) * 100
                return df
            return None
        except Exception as e:
            print(f"   ✗ Error fetching CPI vector: {e}")
            return None

    def _process_vector_response(self, response_data, value_column_name):
        """Process vector response data"""
        try:
            if 'object' in response_data and 'vectorDataPoint' in response_data['object']:
                data_points = response_data['object']['vectorDataPoint']

                records = []
                for point in data_points:
                    records.append({
                        'REF_DATE': point.get('refPer'),
                        value_column_name: float(point.get('value', 0)) if point.get('value') is not None else None
                    })

                df = pd.DataFrame(records)
                df['REF_DATE'] = pd.to_datetime(df['REF_DATE'])
                df = df.dropna().sort_values('REF_DATE')
                return df
            return None
        except Exception as e:
            print(f"   ✗ Error processing vector response: {e}")
            return None

    def _process_statcan_response(self, response_data):
        """Process StatCan API response data"""
        try:
            # This would process the full table response
            # For now, return None to force use of vector method
            return None
        except Exception as e:
            print(f"   ✗ Error processing StatCan response: {e}")
            return None

    def get_gdp_data(self, start_date=None, end_date=None):
        """
        Get GDP data (quarterly, chained 2017 dollars)
        Using vector 65201210 for GDP at market prices
        """
        print("   Fetching GDP data...")
        return self._get_gdp_by_vector()

    def get_employment_data(self, start_date=None, end_date=None):
        """
        Get employment and unemployment rates
        Using vectors for Canada-wide employment data
        """
        print("   Fetching employment data...")
        return self._get_employment_by_vector()

    def get_cpi_data(self, start_date=None, end_date=None):
        """
        Get Consumer Price Index data
        Using vector 41690973 for all-items CPI, Canada
        """
        print("   Fetching CPI data...")
        return self._get_cpi_by_vector()

    def get_all_indicators(self, start_date=None, end_date=None):
        """
        Get all key economic indicators and merge them
        """
        print("Fetching all StatCan economic indicators...")

        # Fetch individual datasets
        gdp = self.get_gdp_data(start_date, end_date)
        time.sleep(1)  # Be respectful to the API

        employment = self.get_employment_data(start_date, end_date)
        time.sleep(1)

        cpi = self.get_cpi_data(start_date, end_date)
        time.sleep(1)

        # Start with the most frequent data (monthly employment)
        if employment is not None:
            combined = employment.copy()
            combined.rename(columns={'REF_DATE': 'Date'}, inplace=True, errors='ignore')

            # Add CPI data (monthly)
            if cpi is not None:
                cpi_renamed = cpi.copy()
                cpi_renamed.rename(columns={'REF_DATE': 'Date'}, inplace=True, errors='ignore')
                combined = pd.merge(combined, cpi_renamed[['Date', 'CPI', 'Inflation_Rate']], on='Date', how='outer')

            # Add GDP data (quarterly) - will create NaN for non-quarter months
            if gdp is not None:
                gdp_renamed = gdp.copy()
                gdp_renamed.rename(columns={'REF_DATE': 'Date'}, inplace=True, errors='ignore')
                combined = pd.merge(combined, gdp_renamed, on='Date', how='outer')

            combined = combined.sort_values('Date')
            print(f"✓ Combined economic data: {len(combined)} records")
            return combined
        elif cpi is not None:
            # If no employment data, start with CPI
            combined = cpi.copy()
            combined.rename(columns={'REF_DATE': 'Date'}, inplace=True, errors='ignore')

            if gdp is not None:
                gdp_renamed = gdp.copy()
                gdp_renamed.rename(columns={'REF_DATE': 'Date'}, inplace=True, errors='ignore')
                combined = pd.merge(combined, gdp_renamed, on='Date', how='outer')

            combined = combined.sort_values('Date')
            print(f"✓ Combined economic data: {len(combined)} records")
            return combined
        elif gdp is not None:
            # If only GDP data available
            combined = gdp.copy()
            combined.rename(columns={'REF_DATE': 'Date'}, inplace=True, errors='ignore')
            print(f"✓ GDP data only: {len(combined)} records")
            return combined

        print("✗ Failed to create combined economic dataset")
        return None

def fetch_statcan_indicators():
    """
    Fetch key economic indicators from Statistics Canada
    Returns current values and trends for integration with real estate model
    """

    fetcher = StatCanDataFetcher()

    # Get data for the last 5 years for trend analysis
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5*365)

    print(f"Fetching StatCan data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")

    # Get all indicators
    data = fetcher.get_all_indicators(
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )

    statcan_indicators = {}
    statcan_trends = {}

    if data is not None:
        # Get latest values
        latest_data = data.dropna().tail(1)

        if not latest_data.empty:
            latest_record = latest_data.iloc[-1]

            # Current values
            statcan_indicators['current_employment_rate'] = latest_record.get('Employment_Rate')
            statcan_indicators['current_unemployment_rate'] = latest_record.get('Unemployment_Rate')
            statcan_indicators['current_cpi'] = latest_record.get('CPI')
            statcan_indicators['current_inflation_rate'] = latest_record.get('Inflation_Rate')
            statcan_indicators['current_gdp'] = latest_record.get('GDP_Billions_CAD')

            # Calculate trends (6-month and 1-year changes)
            if len(data) > 12:  # Need at least 12 months for year-over-year
                data_12m_ago = data.iloc[-13] if len(data) >= 13 else data.iloc[0]
                data_6m_ago = data.iloc[-7] if len(data) >= 7 else data.iloc[0]

                # Employment rate trends
                if pd.notna(latest_record.get('Employment_Rate')) and pd.notna(data_6m_ago.get('Employment_Rate')):
                    statcan_indicators['employment_rate_6m_change'] = latest_record['Employment_Rate'] - data_6m_ago['Employment_Rate']

                if pd.notna(latest_record.get('Employment_Rate')) and pd.notna(data_12m_ago.get('Employment_Rate')):
                    statcan_indicators['employment_rate_1y_change'] = latest_record['Employment_Rate'] - data_12m_ago['Employment_Rate']

                # Unemployment rate trends
                if pd.notna(latest_record.get('Unemployment_Rate')) and pd.notna(data_6m_ago.get('Unemployment_Rate')):
                    statcan_indicators['unemployment_rate_6m_change'] = latest_record['Unemployment_Rate'] - data_6m_ago['Unemployment_Rate']

                if pd.notna(latest_record.get('Unemployment_Rate')) and pd.notna(data_12m_ago.get('Unemployment_Rate')):
                    statcan_indicators['unemployment_rate_1y_change'] = latest_record['Unemployment_Rate'] - data_12m_ago['Unemployment_Rate']

                # GDP trends (quarterly data will have more sparse points)
                if pd.notna(latest_record.get('GDP_Billions_CAD')) and pd.notna(data_12m_ago.get('GDP_Billions_CAD')):
                    gdp_change = latest_record['GDP_Billions_CAD'] - data_12m_ago['GDP_Billions_CAD']
                    gdp_change_pct = (gdp_change / data_12m_ago['GDP_Billions_CAD']) * 100 if data_12m_ago['GDP_Billions_CAD'] != 0 else 0
                    statcan_indicators['gdp_1y_change'] = gdp_change
                    statcan_indicators['gdp_1y_change_pct'] = gdp_change_pct

            # Store full time series for later analysis
            statcan_trends['combined_data'] = data

            print("\nStatCan Economic Indicators Summary:")
            print("-" * 50)
            for key, value in statcan_indicators.items():
                if value is not None and not pd.isna(value):
                    indicator_name = key.replace('current_', '').replace('_', ' ').title()
                    if 'rate' in key.lower() or 'inflation' in key.lower():
                        print(f"{indicator_name:<30}: {value:8.2f}%")
                    elif 'gdp' in key.lower() and 'pct' not in key.lower():
                        print(f"{indicator_name:<30}: {value:8.1f} Billion CAD")
                    elif 'change_pct' in key:
                        print(f"{indicator_name:<30}: {value:8.2f}%")
                    else:
                        print(f"{indicator_name:<30}: {value:8.2f}")
        else:
            print("⚠ No recent data available for current indicators")
    else:
        print("✗ Failed to fetch StatCan economic data")

    return statcan_indicators, statcan_trends

# Fetch Statistics Canada indicators
try:
    statcan_indicators, statcan_time_series = fetch_statcan_indicators()
    print(f"\n✓ Successfully fetched {len([k for k, v in statcan_indicators.items() if v is not None and not pd.isna(v)])} StatCan economic indicators")

except Exception as e:
    print(f"\n✗ Error fetching StatCan economic indicators: {e}")
    # Create empty StatCan data as fallback
    statcan_indicators = {}
    statcan_time_series = {}

# Combine all economic indicators
all_economic_indicators = {**economic_indicators, **statcan_indicators}
all_economic_time_series = {**economic_time_series, **statcan_time_series}

print(f"\n✓ Total economic indicators available: {len([k for k, v in all_economic_indicators.items() if v is not None and (not isinstance(v, float) or not pd.isna(v))])}")