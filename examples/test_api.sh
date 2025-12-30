#!/bin/bash

# Simple bash script to test the Chat with PDF API using curl

API_URL="http://localhost:8000"

echo "================================"
echo "Chat with PDF API - Curl Example"
echo "================================"
echo

# 1. Check health
echo "1. Checking API health..."
curl -X GET "$API_URL/health" | json_pp
echo
echo

# 2. Upload PDF (replace with your PDF path)
echo "2. Upload a PDF file..."
echo "Enter PDF file path:"
read PDF_PATH

if [ -f "$PDF_PATH" ]; then
    UPLOAD_RESPONSE=$(curl -X POST "$API_URL/upload" \
        -F "file=@$PDF_PATH" \
        -H "accept: application/json")
    
    echo "$UPLOAD_RESPONSE" | json_pp
    
    # Extract session ID
    SESSION_ID=$(echo "$UPLOAD_RESPONSE" | grep -o '"session_id":"[^"]*' | cut -d'"' -f4)
    echo
    echo "Session ID: $SESSION_ID"
else
    echo "File not found: $PDF_PATH"
    exit 1
fi

echo
echo

# 3. Ask a question
echo "3. Ask a question..."
echo "Enter your question:"
read QUESTION

curl -X POST "$API_URL/ask" \
    -H "Content-Type: application/json" \
    -d "{\"question\": \"$QUESTION\", \"session_id\": \"$SESSION_ID\"}" | json_pp

echo
echo

# 4. List sessions
echo "4. List all sessions..."
curl -X GET "$API_URL/sessions" | json_pp

echo
echo

# 5. Get session details
echo "5. Get session details..."
curl -X GET "$API_URL/sessions/$SESSION_ID" | json_pp

echo
echo

# 6. Ask another question
echo "6. Ask another question (optional)..."
echo "Enter your question (or press Enter to skip):"
read QUESTION2

if [ ! -z "$QUESTION2" ]; then
    curl -X POST "$API_URL/ask" \
        -H "Content-Type: application/json" \
        -d "{\"question\": \"$QUESTION2\", \"session_id\": \"$SESSION_ID\"}" | json_pp
fi

echo
echo

# 7. Delete session (optional)
echo "7. Delete session? (y/n):"
read DELETE_CHOICE

if [ "$DELETE_CHOICE" = "y" ]; then
    curl -X DELETE "$API_URL/sessions/$SESSION_ID" | json_pp
    echo
    echo "Session deleted!"
fi

echo
echo "Done!"
