#!/usr/bin/env python3
"""
Quick test script to verify PDF context retrieval is working.
Run this after starting the API to test if context is being passed.
"""

import requests
import sys

API_URL = "http://localhost:8000"

def test_pdf_chat(pdf_path, question):
    """Test uploading a PDF and asking a question."""
    
    print(f"📤 Uploading PDF: {pdf_path}")
    
    # Upload PDF
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': (pdf_path, f, 'application/pdf')}
            response = requests.post(f"{API_URL}/upload", files=files)
            response.raise_for_status()
            upload_data = response.json()
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return
    
    print(f"✅ Upload successful!")
    print(f"   Session ID: {upload_data['session_id']}")
    print(f"   Chunks: {upload_data['num_chunks']}")
    print()
    
    session_id = upload_data['session_id']
    
    # Check session details
    print(f"🔍 Checking extracted content...")
    try:
        response = requests.get(f"{API_URL}/sessions/{session_id}")
        response.raise_for_status()
        session_data = response.json()
        
        if 'sample_text' in session_data:
            sample = session_data['sample_text'][:200]
            print(f"   Sample text: {sample}...")
            print()
    except Exception as e:
        print(f"⚠️  Could not fetch session details: {e}")
        print()
    
    # Ask question
    print(f"❓ Question: {question}")
    try:
        payload = {
            "question": question,
            "session_id": session_id
        }
        response = requests.post(f"{API_URL}/ask", json=payload)
        response.raise_for_status()
        answer_data = response.json()
        
        print(f"💬 Answer: {answer_data['answer']}")
        print()
        
        # Check if answer looks like it has context
        answer = answer_data['answer'].lower()
        if "don't have access" in answer or "can't" in answer or "unable to" in answer:
            print("⚠️  WARNING: Answer suggests context might not be working")
        else:
            print("✅ Answer looks good - context seems to be working!")
            
    except Exception as e:
        print(f"❌ Question failed: {e}")
        return
    
    # Clean up
    print(f"\n🗑️  Cleaning up session...")
    try:
        requests.delete(f"{API_URL}/sessions/{session_id}")
        print("✅ Session deleted")
    except:
        pass


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_pdf_context.py <pdf_file> [question]")
        print("\nExample:")
        print("  python test_pdf_context.py sample.pdf 'What is this document about?'")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    question = sys.argv[2] if len(sys.argv) > 2 else "What is this document about?"
    
    print("=" * 60)
    print("PDF Context Retrieval Test")
    print("=" * 60)
    print()
    
    # Check health first
    try:
        response = requests.get(f"{API_URL}/health")
        health = response.json()
        if not health.get('api_configured'):
            print("⚠️  API not configured - check your .env file!")
            sys.exit(1)
    except:
        print("❌ API not running - start with: python api.py")
        sys.exit(1)
    
    test_pdf_chat(pdf_path, question)
