import streamlit as st
import folium
from streamlit_folium import folium_static
from utils import get_video_id, get_video_transcript
from location_extractor import LocationExtractor
from text_analyzer import analyze_transcript, analyze_video_title
import time

# Page config
st.set_page_config(
    page_title="Seyahat Lokasyonu Tespit",
    page_icon="🗺️",
    layout="wide"
)

# Title and description
st.title("🌍 YouTube Seyahat Lokasyonu Tespit")
st.markdown("""
Bu uygulama YouTube videolarından seyahat lokasyonlarını tespit eder ve harita üzerinde gösterir.
Özellikle turistik mekanları ve önemli noktaları tanımlar.
""")

# YouTube URL input
youtube_url = st.text_input("YouTube Video URL'si", placeholder="https://www.youtube.com/watch?v=...")

if youtube_url:
    try:
        # Show loading spinner
        with st.spinner('Video işleniyor...'):
            # Get video ID and transcript
            video_id = get_video_id(youtube_url)
            transcript = get_video_transcript(video_id)

            if transcript:
                # Extract locations using Gemini API
                with st.spinner('Lokasyonlar tespit ediliyor...'):
                    locations = analyze_transcript(transcript)

                    # Get video title context
                    video_title = analyze_video_title(transcript[:100])  # İlk 100 karakter

                    if locations:
                        # Initialize location extractor
                        extractor = LocationExtractor()

                        # Get coordinates with context
                        coordinates = extractor.get_coordinates(locations, main_city=video_title)

                        # Filter out locations that couldn't be found
                        found_locations = [loc for loc, coord in coordinates.items() if coord]

                        if found_locations:
                            # Create map centered on the main city if available
                            if video_title and video_title in coordinates:
                                center_lat = coordinates[video_title]['lat']
                                center_lon = coordinates[video_title]['lon']
                            else:
                                # Use the first found location as center
                                first_loc = found_locations[0]
                                center_lat = coordinates[first_loc]['lat']
                                center_lon = coordinates[first_loc]['lon']

                            # Harita görünümü
                            st.subheader("📍 Harita Görünümü")
                            m = folium.Map(location=[center_lat, center_lon], zoom_start=13)

                            # Add markers only for found locations
                            for loc in found_locations:
                                coord = coordinates[loc]
                                folium.Marker(
                                    location=[coord['lat'], coord['lon']],
                                    popup=f"<b>{loc}</b><br>{coord.get('display_name', '')}",
                                    icon=folium.Icon(color='red', icon='info-sign')
                                ).add_to(m)

                            # Display map
                            folium_static(m)

                            # Lokasyon listesi
                            st.subheader("📝 Tespit Edilen Lokasyonlar")

                            # Show found locations first
                            if found_locations:
                                st.markdown("**✅ Bulunan Lokasyonlar:**")
                                for loc in found_locations:
                                    matched_term = coordinates[loc].get('matched_term', '')
                                    if matched_term and matched_term != loc:
                                        st.markdown(f"- **{loc}** _(eşleşen: {matched_term})_\n  _{coordinates[loc].get('display_name', '')}_")
                                    else:
                                        st.markdown(f"- **{loc}**\n  _{coordinates[loc].get('display_name', '')}_")

                            # Show not found locations separately
                            not_found = [loc for loc in locations if loc not in found_locations]
                            if not_found:
                                st.markdown("**❌ Bulunamayan Lokasyonlar:**")
                                for loc in not_found:
                                    st.markdown(f"- {loc}")
                        else:
                            st.warning("Tespit edilen lokasyonların koordinatları bulunamadı.")
                    else:
                        st.warning("Videoda herhangi bir lokasyon tespit edilemedi.")
            else:
                st.error("Video alt yazısı bulunamadı.")

    except Exception as e:
        st.error(f"Bir hata oluştu: {str(e)}")

# Footer
st.markdown("""
---
📌 Not: Bu uygulama YouTube videolarının alt yazılarını kullanarak lokasyon tespiti yapar.
Özellikle turistik mekanlar ve önemli noktalar için optimize edilmiştir.
""")