import spacy
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time
from geopy.extra.rate_limiter import RateLimiter

# Load English language model
nlp = spacy.load("en_core_web_sm")

def extract_locations(text):
    """Extract location names from text using spaCy."""
    doc = nlp(text)
    locations = set()

    for ent in doc.ents:
        # Include both location (LOC) and geopolitical (GPE) entities
        if ent.label_ in ["LOC", "GPE"]:
            locations.add(ent.text)

    return list(locations)

class LocationExtractor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.geolocator = Nominatim(user_agent="travel_location_detector")
        # Rate limiter to respect Nominatim's usage policy
        self.geocode = RateLimiter(self.geolocator.geocode, min_delay_seconds=1)

    def _split_location_name(self, location):
        """Split location name into parts and try different combinations."""
        words = location.split()
        combinations = []

        # Orijinal lokasyonu ekle
        combinations.append(location)

        # Tek kelimeler
        combinations.extend(words)

        # İkili kelime grupları
        if len(words) > 1:
            for i in range(len(words)-1):
                combinations.append(f"{words[i]} {words[i+1]}")

        return combinations

    def get_coordinates(self, locations, main_city=None):
        """
        Get coordinates for locations using Nominatim with improved accuracy.
        """
        coordinates = {}

        for location in locations:
            try:
                # Lokasyon adını parçalara ayır
                location_parts = self._split_location_name(location)
                found = False

                for part in location_parts:
                    # Ana şehir varsa, lokasyonu o şehirle birlikte ara
                    search_term = f"{part}, {main_city}" if main_city else part

                    # Try to get location data with better context
                    location_data = self.geocode(
                        search_term,
                        exactly_one=True,
                        language='tr'
                    )

                    if location_data:
                        coordinates[location] = {
                            'lat': location_data.latitude,
                            'lon': location_data.longitude,
                            'display_name': location_data.address,
                            'matched_term': part
                        }
                        found = True
                        break

                if not found:
                    print(f"No location found for: {location}")

            except GeocoderTimedOut:
                print(f"Timeout for location: {location}")
                continue
            except Exception as e:
                print(f"Error processing location {location}: {str(e)}")
                continue

        return coordinates