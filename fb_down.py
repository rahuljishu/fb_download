# app.py
import streamlit as st
import requests
import re
from bs4 import BeautifulSoup
import json
import urllib.request
from pathlib import Path
import os

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
        # Send request with mobile user agent to get mobile version
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15'
        }
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find video data in the page
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
        
        # Extract available qualities
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

def download_video(url, output_path):
    """Download video from URL."""
    try:
        urllib.request.urlretrieve(url, output_path)
        return True
    except Exception as e:
        st.error(f"Error downloading video: {str(e)}")
        return False

# Streamlit UI
st.title("Facebook Video Downloader")
st.write("Enter a Facebook video URL to download it in your preferred quality.")

# Input for video URL
video_url = st.text_input("Enter Facebook Video URL")

if video_url:
    # Create downloads directory if it doesn't exist
    downloads_dir = Path("downloads")
    downloads_dir.mkdir(exist_ok=True)
    
    # Get video information
    qualities = get_video_info(video_url)
    
    if qualities:
        # Create quality selection dropdown
        quality_labels = [q['label'] for q in qualities]
        selected_quality = st.selectbox("Select Video Quality", quality_labels)
        
        # Download button
        if st.button("Download Video"):
            selected_url = next(q['url'] for q in qualities if q['label'] == selected_quality)
            
            # Generate output filename
            video_id = extract_video_id(video_url) or 'video'
            output_path = downloads_dir / f"facebook_{video_id}_{selected_quality}.mp4"
            
            with st.spinner("Downloading video..."):
                if download_video(selected_url, str(output_path)):
                    st.success(f"Video downloaded successfully! Saved as: {output_path.name}")
                    
                    # Add download link
                    with open(output_path, 'rb') as f:
                        st.download_button(
                            label="Click to save to your device",
                            data=f,
                            file_name=output_path.name,
                            mime="video/mp4"
                        )
    else:
        st.error("Could not retrieve video information. Please check the URL and try again.")
