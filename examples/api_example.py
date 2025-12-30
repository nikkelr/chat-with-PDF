"""Example script demonstrating how to use the Chat with PDF REST API."""

import requests
import json
import time

# API Base URL
API_URL = "http://localhost:8000"


def check_health():
    """Check if the API is healthy and configured."""
    print("🔍 Checking API health...")
    response = requests.get(f"{API_URL}/health")
    data = response.json()
    print(f"   Status: {data['status']}")
    print(f"   API Configured: {data['api_configured']}")
    print()
    return data['api_configured']


def upload_pdf(pdf_path):
    """Upload a PDF file and get session ID."""
    print(f"📤 Uploading PDF: {pdf_path}")
    
    with open(pdf_path, 'rb') as f:
        files = {'file': (pdf_path, f, 'application/pdf')}
        response = requests.post(f"{API_URL}/upload", files=files)
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Success!")
        print(f"   Session ID: {data['session_id']}")
        print(f"   PDF Name: {data['pdf_name']}")
        print(f"   Text Chunks: {data['num_chunks']}")
        print()
        return data['session_id']
    else:
        print(f"   ❌ Error: {response.status_code}")
        print(f"   {response.json()}")
        return None


def ask_question(session_id, question):
    """Ask a question about the uploaded PDF."""
    print(f"❓ Question: {question}")
    
    payload = {
        "question": question,
        "session_id": session_id
    }
    
    response = requests.post(
        f"{API_URL}/ask",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   💬 Answer: {data['answer']}")
        print(f"   ⏰ Timestamp: {data['timestamp']}")
        print()
        return data['answer']
    else:
        print(f"   ❌ Error: {response.status_code}")
        print(f"   {response.json()}")
        return None


def list_sessions():
    """List all active sessions."""
    print("📋 Listing all sessions...")
    response = requests.get(f"{API_URL}/sessions")
    
    if response.status_code == 200:
        sessions = response.json()
        print(f"   Found {len(sessions)} session(s):")
        for session in sessions:
            print(f"   - {session['session_id'][:8]}... | {session['pdf_name']} | {session['num_chunks']} chunks")
        print()
        return sessions
    else:
        print(f"   ❌ Error: {response.status_code}")
        return []


def get_session_details(session_id):
    """Get detailed information about a session."""
    print(f"📊 Getting session details for {session_id[:8]}...")
    response = requests.get(f"{API_URL}/sessions/{session_id}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   PDF: {data['pdf_name']}")
        print(f"   Created: {data['created_at']}")
        print(f"   Chat History: {len(data['chat_history'])} messages")
        print()
        return data
    else:
        print(f"   ❌ Error: {response.status_code}")
        return None


def delete_session(session_id):
    """Delete a session."""
    print(f"🗑️  Deleting session {session_id[:8]}...")
    response = requests.delete(f"{API_URL}/sessions/{session_id}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ {data['message']}")
        print()
        return True
    else:
        print(f"   ❌ Error: {response.status_code}")
        return False


def main():
    """Main example workflow."""
    print("=" * 60)
    print("Chat with PDF API - Example Usage")
    print("=" * 60)
    print()
    
    # Check health
    if not check_health():
        print("⚠️  API is not configured. Please set your OpenRouter API key in .env file")
        return
    
    # Example: Upload a PDF
    pdf_path = input("Enter path to PDF file (or press Enter to skip): ").strip()
    
    if not pdf_path:
        print("ℹ️  Skipping upload. Using example with existing session (if any)...")
        sessions = list_sessions()
        if sessions:
            session_id = sessions[0]['session_id']
        else:
            print("❌ No active sessions found. Please upload a PDF first.")
            return
    else:
        session_id = upload_pdf(pdf_path)
        if not session_id:
            return
    
    # Ask questions
    print("💡 You can now ask questions about the PDF")
    print("   (Type 'quit' to exit, 'sessions' to list sessions)")
    print()
    
    while True:
        question = input("Your question: ").strip()
        
        if question.lower() == 'quit':
            break
        elif question.lower() == 'sessions':
            list_sessions()
            continue
        elif question.lower() == 'details':
            get_session_details(session_id)
            continue
        elif not question:
            continue
        
        ask_question(session_id, question)
    
    # Clean up
    cleanup = input("\n🗑️  Delete session? (y/n): ").strip().lower()
    if cleanup == 'y':
        delete_session(session_id)
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
