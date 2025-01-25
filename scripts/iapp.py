import streamlit as st
import torch
from PIL import Image
import google.generativeai as genai
from transformers import EfficientNetImageProcessor, EfficientNetForImageClassification

def detect_bird_species(image):
    """Detect bird species from an uploaded image"""
    try:
        preprocessor = EfficientNetImageProcessor.from_pretrained("dennisjooo/Birds-Classifier-EfficientNetB2")
        model = EfficientNetForImageClassification.from_pretrained("dennisjooo/Birds-Classifier-EfficientNetB2")
        
        inputs = preprocessor(image, return_tensors="pt")
        
        with torch.no_grad():
            logits = model(**inputs).logits
        
        predicted_label = logits.argmax(-1).item()
        species_name = model.config.id2label[predicted_label]
        
        return species_name
    
    except Exception as e:
        st.error(f"Bird detection error: {e}")
        return None

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
    st.title("🐦 Bird Image Species Analyzer")

    # API Configuration
    try:
        genai.configure(api_key=st.secrets.get('GEMINI_API_KEY', ''))
    except Exception as e:
        st.error("Gemini API configuration failed.")
        return

    # Image Upload
    uploaded_image = st.file_uploader("Upload Bird Image", type=["jpg", "jpeg", "png"])

    if uploaded_image is not None:
        with st.spinner("Processing Image..."):
            try:
                # Open image
                image = Image.open(uploaded_image)
                st.image(image, caption="Uploaded Image", use_container_width=True)

                # Detect Species
                species_name = detect_bird_species(image)

                if species_name:
                    # Get Species Image
                    species_image_url = get_species_image(species_name)

                    # Generate Ecological Report
                    prompt = (
                        f"Create a concise ecological report for {species_name} "
                        f"in India. Cover habitat, distribution, "
                        f"behavior, ecological significance, conservation status."
                    )
                    
                    model = genai.GenerativeModel('gemini-pro')
                    response = model.generate_content(prompt)

                    # Display Results
                    st.markdown("## Species Detection Results")
                    
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        if species_image_url:
                            st.image(species_image_url, caption=species_name, use_container_width=True)
                    
                    with col2:
                        st.markdown(f"**Species:** {species_name}")
                    
                    st.markdown("### Ecological Insights")
                    st.write(response.text)

                else:
                    st.warning("Bird species could not be detected.")

            except Exception as e:
                st.error(f"Analysis failed: {e}")

if __name__ == "__main__":
    main()