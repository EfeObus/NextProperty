"""
Geospatial service for location-based features and spatial analysis.
Handles geocoding, distance calculations, and location-based queries.
"""
import requests
import math
from typing import Dict, List, Optional, Tuple
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from app.models.property import Property
from app import db, cache
import logging

logger = logging.getLogger(__name__)

class GeospatialService:
    """Service for geospatial operations and location analysis."""
    
    def __init__(self):
        self.geocoder = Nominatim(user_agent="nextproperty-ai")
        self.google_maps_api_key = None  # Would be set from environment
    
    @cache.memoize(timeout=86400)  # Cache for 24 hours
    def geocode_address(self, address: str) -> Optional[Dict]:
        """Geocode an address to get latitude and longitude."""
        try:
            location = self.geocoder.geocode(address, timeout=10)
            if location:
                return {
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                    'formatted_address': location.address,
                    'raw': location.raw
                }
            return None
            
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            logger.error(f"Geocoding error for address '{address}': {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error geocoding '{address}': {str(e)}")
            return None
    
    @cache.memoize(timeout=86400)
    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict]:
        """Reverse geocode coordinates to get address information."""
        try:
            location = self.geocoder.reverse(f"{latitude}, {longitude}", timeout=10)
            if location:
                return {
                    'address': location.address,
                    'raw': location.raw
                }
            return None
            
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            logger.error(f"Reverse geocoding error for {latitude}, {longitude}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error reverse geocoding {latitude}, {longitude}: {str(e)}")
            return None
    
    def calculate_distance(self, point1: Tuple[float, float], 
                          point2: Tuple[float, float], unit: str = 'km') -> float:
        """Calculate distance between two points."""
        try:
            distance = geodesic(point1, point2)
            unit_safe = unit.lower() if unit else 'km'
            if unit_safe == 'miles':
                return distance.miles
            elif unit_safe == 'km':
                return distance.kilometers
            else:
                return distance.meters
                
        except Exception as e:
            logger.error(f"Error calculating distance: {str(e)}")
            return 0.0
    
    def find_properties_within_radius(self, center_lat: float, center_lon: float, 
                                    radius_km: float, limit: int = 50) -> List[Dict]:
        """Find properties within a specified radius of a center point."""
        try:
            # Use Haversine formula for database query
            # This is an approximation - for more precise results, use PostGIS
            lat_range = radius_km / 111.0  # Rough conversion: 1 degree ≈ 111 km
            lon_range = radius_km / (111.0 * math.cos(math.radians(center_lat)))
            
            properties = db.session.query(Property).filter(
                Property.latitude.between(center_lat - lat_range, center_lat + lat_range),
                Property.longitude.between(center_lon - lon_range, center_lon + lon_range)
            ).limit(limit * 2).all()  # Get more than needed for filtering
            
            # Filter by actual distance
            nearby_properties = []
            for prop in properties:
                if prop.latitude and prop.longitude:
                    distance = self.calculate_distance(
                        (center_lat, center_lon),
                        (prop.latitude, prop.longitude)
                    )
                    if distance <= radius_km:
                        prop_dict = prop.to_dict()
                        prop_dict['distance_km'] = round(distance, 2)
                        nearby_properties.append(prop_dict)
            
            # Sort by distance and limit results
            nearby_properties.sort(key=lambda x: x['distance_km'])
            return nearby_properties[:limit]
            
        except Exception as e:
            logger.error(f"Error finding properties within radius: {str(e)}")
            return []
    
    def find_properties_by_polygon(self, polygon_points: List[Tuple[float, float]]) -> List[Dict]:
        """Find properties within a polygon defined by a list of points."""
        try:
            # Simple bounding box approach - for complex polygons, use PostGIS
            if len(polygon_points) < 3:
                return []
            
            lats = [point[0] for point in polygon_points]
            lons = [point[1] for point in polygon_points]
            
            min_lat, max_lat = min(lats), max(lats)
            min_lon, max_lon = min(lons), max(lons)
            
            properties = db.session.query(Property).filter(
                Property.latitude.between(min_lat, max_lat),
                Property.longitude.between(min_lon, max_lon)
            ).all()
            
            # For a more precise polygon check, implement point-in-polygon algorithm
            return [prop.to_dict() for prop in properties]
            
        except Exception as e:
            logger.error(f"Error finding properties by polygon: {str(e)}")
            return []
    
    @cache.memoize(timeout=3600)
    def get_nearby_amenities(self, latitude: float, longitude: float, 
                           amenity_type: str = None, radius_km: float = 2.0) -> List[Dict]:
        """Get nearby amenities using Overpass API (OpenStreetMap)."""
        try:
            # Overpass API query for amenities
            overpass_url = "http://overpass-api.de/api/interpreter"
            
            # Build query based on amenity type
            if amenity_type:
                amenity_filter = f'["amenity"="{amenity_type}"]'
            else:
                amenity_filter = '["amenity"]'
            
            # Calculate bounding box
            lat_range = radius_km / 111.0
            lon_range = radius_km / (111.0 * math.cos(math.radians(latitude)))
            
            south = latitude - lat_range
            west = longitude - lon_range
            north = latitude + lat_range
            east = longitude + lon_range
            
            query = f"""
            [out:json][timeout:25];
            (
              node{amenity_filter}({south},{west},{north},{east});
              way{amenity_filter}({south},{west},{north},{east});
            );
            out center;
            """
            
            response = requests.post(overpass_url, data=query, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            amenities = []
            
            for element in data.get('elements', []):
                if 'tags' in element and 'amenity' in element['tags']:
                    # Get coordinates
                    if element['type'] == 'node':
                        amenity_lat = element['lat']
                        amenity_lon = element['lon']
                    elif element['type'] == 'way' and 'center' in element:
                        amenity_lat = element['center']['lat']
                        amenity_lon = element['center']['lon']
                    else:
                        continue
                    
                    # Calculate distance
                    distance = self.calculate_distance(
                        (latitude, longitude),
                        (amenity_lat, amenity_lon)
                    )
                    
                    if distance <= radius_km:
                        amenity = {
                            'name': element['tags'].get('name', 'Unknown'),
                            'type': element['tags']['amenity'],
                            'latitude': amenity_lat,
                            'longitude': amenity_lon,
                            'distance_km': round(distance, 2),
                            'tags': element['tags']
                        }
                        amenities.append(amenity)
            
            # Sort by distance
            amenities.sort(key=lambda x: x['distance_km'])
            return amenities
            
        except Exception as e:
            logger.error(f"Error getting nearby amenities: {str(e)}")
            return []
    
    def get_transit_score(self, latitude: float, longitude: float) -> Dict:
        """Calculate transit accessibility score for a location."""
        try:
            # Get nearby transit amenities
            transit_types = ['bus_station', 'subway_entrance', 'train_station']
            all_transit = []
            
            for transit_type in transit_types:
                transit_points = self.get_nearby_amenities(
                    latitude, longitude, transit_type, radius_km=1.0
                )
                all_transit.extend(transit_points)
            
            # Calculate score based on proximity and number of options
            score = 0
            if all_transit:
                # Sort by distance
                all_transit.sort(key=lambda x: x['distance_km'])
                
                # Score based on closest transit
                closest_distance = all_transit[0]['distance_km']
                if closest_distance <= 0.2:  # Within 200m
                    score += 40
                elif closest_distance <= 0.5:  # Within 500m
                    score += 30
                elif closest_distance <= 1.0:  # Within 1km
                    score += 20
                else:
                    score += 10
                
                # Bonus points for multiple options
                score += min(len(all_transit) * 5, 30)
                
                # Bonus for different types of transit
                unique_types = len(set(t['type'] for t in all_transit))
                score += unique_types * 10
            
            return {
                'score': min(score, 100),  # Cap at 100
                'transit_options': len(all_transit),
                'closest_distance_km': all_transit[0]['distance_km'] if all_transit else None,
                'transit_points': all_transit[:5]  # Return top 5
            }
            
        except Exception as e:
            logger.error(f"Error calculating transit score: {str(e)}")
            return {'score': 0, 'transit_options': 0, 'transit_points': []}
    
    def get_walkability_score(self, latitude: float, longitude: float) -> Dict:
        """Calculate walkability score based on nearby amenities."""
        try:
            # Categories of amenities that contribute to walkability
            amenity_categories = {
                'retail': ['shop', 'marketplace', 'mall'],
                'food': ['restaurant', 'cafe', 'fast_food', 'bar'],
                'services': ['bank', 'pharmacy', 'hospital', 'clinic'],
                'education': ['school', 'university', 'library'],
                'recreation': ['park', 'gym', 'cinema', 'theatre']
            }
            
            category_scores = {}
            all_amenities = []
            
            for category, types in amenity_categories.items():
                category_amenities = []
                for amenity_type in types:
                    amenities = self.get_nearby_amenities(
                        latitude, longitude, amenity_type, radius_km=1.0
                    )
                    category_amenities.extend(amenities)
                
                # Score for this category
                if category_amenities:
                    closest = min(category_amenities, key=lambda x: x['distance_km'])
                    if closest['distance_km'] <= 0.5:
                        category_scores[category] = 20
                    elif closest['distance_km'] <= 1.0:
                        category_scores[category] = 15
                    else:
                        category_scores[category] = 10
                    
                    # Bonus for multiple options
                    category_scores[category] += min(len(category_amenities) * 2, 10)
                else:
                    category_scores[category] = 0
                
                all_amenities.extend(category_amenities[:3])  # Top 3 per category
            
            # Calculate overall score
            total_score = sum(category_scores.values())
            
            return {
                'score': min(total_score, 100),
                'category_scores': category_scores,
                'total_amenities': len(all_amenities),
                'nearby_amenities': all_amenities
            }
            
        except Exception as e:
            logger.error(f"Error calculating walkability score: {str(e)}")
            return {'score': 0, 'category_scores': {}, 'nearby_amenities': []}
    
    def get_location_insights(self, property_id: int) -> Dict:
        """Get comprehensive location insights for a property."""
        try:
            property_obj = Property.query.get(property_id)
            if not property_obj or not property_obj.latitude or not property_obj.longitude:
                return {}
            
            lat, lon = property_obj.latitude, property_obj.longitude
            
            insights = {
                'property_id': property_id,
                'coordinates': {'latitude': lat, 'longitude': lon},
                'transit_score': self.get_transit_score(lat, lon),
                'walkability_score': self.get_walkability_score(lat, lon),
                'nearby_properties': [],
                'location_summary': {}
            }
            
            # Find comparable properties nearby
            nearby_props = self.find_properties_within_radius(lat, lon, 2.0, 10)
            insights['nearby_properties'] = nearby_props
            
            # Calculate location summary
            insights['location_summary'] = {
                'total_score': (insights['transit_score']['score'] + 
                              insights['walkability_score']['score']) / 2,
                'strengths': [],
                'considerations': []
            }
            
            # Add strengths and considerations
            if insights['transit_score']['score'] > 70:
                insights['location_summary']['strengths'].append('Excellent transit access')
            if insights['walkability_score']['score'] > 70:
                insights['location_summary']['strengths'].append('Highly walkable area')
            if len(nearby_props) > 5:
                insights['location_summary']['strengths'].append('Active real estate market')
            
            if insights['transit_score']['score'] < 30:
                insights['location_summary']['considerations'].append('Limited transit options')
            if insights['walkability_score']['score'] < 30:
                insights['location_summary']['considerations'].append('Car-dependent location')
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting location insights: {str(e)}")
            return {}
    
    def update_property_coordinates(self, property_id: int) -> bool:
        """Update property coordinates by geocoding its address."""
        try:
            property_obj = Property.query.get(property_id)
            if not property_obj:
                return False
            
            # Build full address
            address_parts = [property_obj.address]
            if property_obj.city:
                address_parts.append(property_obj.city)
            if property_obj.province:
                address_parts.append(property_obj.province)
            if property_obj.postal_code:
                address_parts.append(property_obj.postal_code)
            
            full_address = ', '.join(filter(None, address_parts))
            
            # Geocode the address
            coordinates = self.geocode_address(full_address)
            if coordinates:
                property_obj.latitude = coordinates['latitude']
                property_obj.longitude = coordinates['longitude']
                db.session.commit()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating coordinates for property {property_id}: {str(e)}")
            return False
    
    def batch_update_coordinates(self, limit: int = 100) -> Dict:
        """Batch update coordinates for properties missing them."""
        try:
            # Find properties without coordinates
            properties = Property.query.filter(
                Property.latitude.is_(None) | Property.longitude.is_(None)
            ).limit(limit).all()
            
            results = {
                'processed': 0,
                'successful': 0,
                'failed': 0,
                'errors': []
            }
            
            for prop in properties:
                results['processed'] += 1
                try:
                    if self.update_property_coordinates(prop.id):
                        results['successful'] += 1
                    else:
                        results['failed'] += 1
                        results['errors'].append(f"Failed to geocode property {prop.id}")
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append(f"Error processing property {prop.id}: {str(e)}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in batch coordinate update: {str(e)}")
            return {'processed': 0, 'successful': 0, 'failed': 0, 'errors': [str(e)]}

# Create a global instance
geospatial_service = GeospatialService()
