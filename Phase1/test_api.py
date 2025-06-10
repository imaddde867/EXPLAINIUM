#!/usr/bin/env python3
"""
EXPLAINIUM PH-1 API Testing Script

This script tests all API endpoints to ensure they're working correctly.
"""

import requests
import json
import os
import time
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
TEST_DATA_DIR = Path("test_data")

def test_health_check():
    """Test if the API is running"""
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ API is running and accessible")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Is the server running?")
        return False

def test_document_upload():
    """Test document upload endpoint"""
    print("\n📄 Testing Document Upload...")
    
    # Test with a simple text file
    test_content = "This is a test document for EXPLAINIUM PH-1 validation."
    
    # Create a temporary test file
    test_file_path = "temp_test.txt"
    with open(test_file_path, "w") as f:
        f.write(test_content)
    
    try:
        with open(test_file_path, "rb") as f:
            files = {"file": ("test.txt", f, "text/plain")}
            response = requests.post(f"{BASE_URL}/api/v1/documents/upload", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Document upload successful: ID {data['id']}")
            print(f"   Filename: {data['filename']}")
            print(f"   Content length: {data['content_length']}")
            return data['id']
        else:
            print(f"❌ Document upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Document upload error: {e}")
        return None
    finally:
        # Clean up temporary file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_document_status(doc_id):
    """Test document status endpoint"""
    if not doc_id:
        return False
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/documents/{doc_id}/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Document status check successful: {data['status']}")
            return True
        else:
            print(f"❌ Document status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Document status error: {e}")
        return False

def test_document_content(doc_id):
    """Test document content retrieval"""
    if not doc_id:
        return False
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/documents/{doc_id}/content")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Document content retrieval successful")
            print(f"   Content preview: {data['content'][:100]}...")
            return True
        else:
            print(f"❌ Document content retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Document content error: {e}")
        return False

def test_image_upload():
    """Test image upload with OCR"""
    print("\n🖼️ Testing Image Upload...")
    
    # Look for test images
    image_files = list(TEST_DATA_DIR.glob("*.jpg")) + list(TEST_DATA_DIR.glob("*.png"))
    
    if not image_files:
        print("⚠️ No test images found in test_data directory")
        return False
    
    test_image = image_files[0]
    
    try:
        with open(test_image, "rb") as f:
            files = {"file": (test_image.name, f, "image/jpeg")}
            response = requests.post(f"{BASE_URL}/api/v1/images/upload", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Image upload successful: ID {data['id']}")
            print(f"   OCR text preview: {data['ocr_text'][:100]}...")
            return True
        else:
            print(f"❌ Image upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Image upload error: {e}")
        return False

def test_video_upload():
    """Test video upload with frame extraction"""
    print("\n🎥 Testing Video Upload...")
    
    # Look for test videos
    video_files = list(TEST_DATA_DIR.glob("*.mp4"))
    
    if not video_files:
        print("⚠️ No test videos found in test_data directory")
        return False
    
    test_video = video_files[0]
    
    try:
        with open(test_video, "rb") as f:
            files = {"file": (test_video.name, f, "video/mp4")}
            response = requests.post(f"{BASE_URL}/api/v1/videos/upload", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Video upload successful: ID {data['id']}")
            print(f"   Frames extracted: {data['frames_extracted']}")
            print(f"   Preview frames: {len(data['preview_frames'])}")
            return data['id']
        else:
            print(f"❌ Video upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Video upload error: {e}")
        return False

def test_video_frame_retrieval(video_id):
    """Test video frame retrieval"""
    if not video_id:
        return False
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/videos/{video_id}/frame/0")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Video frame retrieval successful")
            print(f"   Frame index: {data['frame_index']}")
            print(f"   Image data length: {len(data['image_base64'])}")
            return True
        else:
            print(f"❌ Video frame retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Video frame retrieval error: {e}")
        return False

def main():
    """Main testing function"""
    print("🧪 EXPLAINIUM PH-1 API Testing")
    print("=" * 50)
    
    # Test 1: Health check
    if not test_health_check():
        print("\n💡 Make sure the API server is running:")
        print("   uvicorn app.main:app --reload")
        return False
    
    # Test 2: Document processing
    doc_id = test_document_upload()
    if doc_id:
        test_document_status(doc_id)
        test_document_content(doc_id)
    
    # Test 3: Image processing
    test_image_upload()
    
    # Test 4: Video processing
    video_id = test_video_upload()
    if video_id:
        test_video_frame_retrieval(video_id)
    
    print("\n🎉 API testing completed!")
    print("\nNext steps:")
    print("1. Check the web interface: http://localhost:8000")
    print("2. View API documentation: http://localhost:8000/docs")
    print("3. Upload your own files for testing")

if __name__ == "__main__":
    main()
