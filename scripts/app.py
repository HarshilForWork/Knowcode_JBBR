import streamlit as st
import os
import logging
import requests
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
import google.generativeai as genai

# Suppress warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
logging.getLogger('tensorflow').setLevel(logging.ERROR)
logging.getLogger('absl').setLevel(logging.ERROR)
os.environ['GRPC_VERBOSITY'] = 'ERROR'

def get_species_image(species_name):
    """Alternative image retrieval method"""
    try:
        import requests
        from bs4 import BeautifulSoup
        
        url = f"https://www.google.com/search?q={species_name}+bird&tbm=isch"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find first image link
        image_tags = soup.find_all('img')
        for img in image_tags:
            src = img.get('src')
            if src and src.startswith('http'):
                return src
        
        return None
    
    except Exception as e:
        st.error(f"Image retrieval error: {e}")
        return None

def main():
    st.set_page_config(page_title="Bird Species Identifier", layout="centered")
    st.title("🐦 Bird Species Analyzer")

    # API Configuration
    try:
        genai.configure(api_key=st.secrets.get('GEMINI_API_KEY', ''))
    except Exception as e:
        st.error("Gemini API configuration failed.")
        return

    # Audio File Upload
    uploaded_file = st.file_uploader("Upload Bird Audio (MP3)", type=["mp3"])

    if uploaded_file is not None:
        with st.spinner("Processing Audio..."):
            try:
                # Initialize Analyzer
                analyzer = Analyzer()

                # Save Temporary File
                temp_file_path = f"temp_{uploaded_file.name}"
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.read())

                # Analyze Recording
                recording = Recording(analyzer, temp_file_path, min_conf=0.25)
                recording.analyze()

                # Find Best Detection
                if recording.detections:
                    best_detection = max(recording.detections, key=lambda d: d["confidence"])
                    
                    species_name = best_detection["common_name"]
                    scientific_name = best_detection["scientific_name"]
                    confidence = best_detection["confidence"]

                    # Get Species Image
                    image_url = get_species_image(species_name)

                    # Generate Ecological Report
                    prompt = (
                        f"Create a concise ecological report for {species_name} "
                        f"({scientific_name}) in India. Cover habitat, distribution, "
                        f"behavior, ecological significance, conservation status. "
                        f"Detection confidence: {confidence:.2f}"
                    )
                    
                    model = genai.GenerativeModel('gemini-pro')
                    response = model.generate_content(prompt)

                    # Display Results
                    st.markdown("## Species Detection Results")
                    
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        if image_url:
                            st.image(image_url, caption=species_name, use_container_width=True)
                    
                    with col2:
                        st.markdown(f"**Species:** {species_name}")
                        st.markdown(f"**Scientific Name:** {scientific_name}")
                        st.markdown(f"**Confidence:** {confidence:.2%}")
                    
                    st.markdown("### Ecological Insights")
                    st.write(response.text)

                else:
                    st.warning("No bird sounds detected in the audio file.")

                # Clean up temporary file
                os.remove(temp_file_path)

            except Exception as e:
                st.error(f"Analysis failed: {e}")

if __name__ == "__main__":
    main()