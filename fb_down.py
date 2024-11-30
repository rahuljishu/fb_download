import streamlit as st
import requests
import re
from bs4 import BeautifulSoup
import json
from pathlib import Path

def extract_video_id(url):
    """Extract Facebook video ID from URL."""
    patterns = [
        r'facebook\.com/.*?/videos/(\d+)',
        r'fb\.watch/(\d+)',
        r'facebook\.com/watch/\?v=(\d+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_video_info(url):
    """Get video information including available qualities."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15'
        }
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        scripts = soup.find_all('script')
        video_data = None
        
        for script in scripts:
            if script.string and 'video_data' in script.string:
                data = re.search(r'video_data\s*:\s*(\[.*?\])', script.string)
                if data:
                    video_data = json.loads(data.group(1))[0]
                    break
        
        if not video_data:
            return None
        
        qualities = []
        if 'video_qualities' in video_data:
            for quality in video_data['video_qualities']:
                qualities.append({
                    'label': f"{quality['height']}p",
                    'url': quality['url']
                })
                
        return qualities
    
    except Exception as e:
        st.error(f"Error getting video info: {str(e)}")
        return None

# Streamlit UI
st.set_page_config(
    page_title="Facebook Video Downloader",
    page_icon="📹",
    layout="centered"
)

# Custom CSS
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
    }
    .main {
        padding: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📹 Facebook Video Downloader")
st.markdown("Enter a Facebook video URL to download it in your preferred quality.")

# Input for video URL
video_url = st.text_input("Enter Facebook Video URL", placeholder="https://www.facebook.com/watch?v=...")

if video_url:
    # Get video information
    with st.spinner("Fetching video information..."):
        qualities = get_video_info(video_url)
    
    if qualities:
        # Create quality selection dropdown
        quality_labels = [q['label'] for q in qualities]
        selected_quality = st.selectbox("Select Video Quality", quality_labels)
        
        # Get download URL
        download_url = next(q['url'] for q in qualities if q['label'] == selected_quality)
        
        # Create download link
        st.markdown(f"""
            <div style='text-align: center'>
                <a href='{download_url}' target='_blank' download>
                    <button style='padding: 10px 20px; background-color: #FF4B4B; color: white; border: none; border-radius: 5px; cursor: pointer;'>
                        Download Video ({selected_quality})
                    </button>
                </a>
            </div>
        """, unsafe_allow_html=True)
        
        st.info("⚠️ If the download doesn't start automatically, right-click the button and select 'Save link as...'")
    else:
        st.error("Could not retrieve video information. Please check the URL and try again.")

st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Made with ❤️ using Streamlit</p>
    <p style='font-size: 0.8rem; color: #888;'>Note: This tool is for personal use only. Please respect Facebook's terms of service.</p>
</div>
""", unsafe_allow_html=True)
