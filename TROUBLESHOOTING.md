# Troubleshooting PDF Questions

## Current Issue

You're getting a response that says the LLM doesn't have information about your PDF. This is actually **progress** - it means embeddings are working (the response says "based on the context provided"), but we need to verify the PDF content is being extracted correctly.

## Debug Steps

### 1. Check Session Details

After uploading a PDF, check what was extracted:

```bash
curl http://localhost:8000/sessions/YOUR_SESSION_ID
```

This will now show:
- `num_chunks`: How many text chunks were created
- `sample_text`: First 500 characters extracted from the PDF
- `chat_history`: All your questions and answers

### 2. Verify PDF Upload

When you upload, check the response:

```json
{
  "session_id": "...",
  "message": "PDF processed successfully",
  "pdf_name": "yourfile.pdf",
  "num_chunks": 42  // <-- Should be > 0
}
```

If `num_chunks` is 0 or very low, the PDF might be:
- Scanned images (not text)
- Protected/encrypted
- Corrupted

### 3. Test with a Simple PDF

Create a test PDF with known content:

```bash
# Create a simple text file
echo "This is a test document about Python programming. Python is a high-level programming language." > test.txt

# Convert to PDF (if you have tools)
# Or just use any simple PDF you have
```

Then upload and ask: "What is this document about?"

### 4. Ask Better Questions

Instead of vague questions like "describe the PDF", try:
- "What is the main topic of this document?"
- "Summarize the key points"
- "What does this document say about [specific topic]?"
- "List the main sections or headings"

### 5. Check the Actual PDF Content

You said the response mentioned "JavaScript concepts" - **what PDF did you upload?**
- If it's about JavaScript, the system is actually working!
- The LLM is saying there's no info about "PDF files" in your JavaScript document

## Example Test Workflow

```bash
# 1. Upload a PDF
UPLOAD_RESPONSE=$(curl -s -X POST http://localhost:8000/upload -F "file=@test.pdf")
echo $UPLOAD_RESPONSE

# Extract session ID
SESSION_ID=$(echo $UPLOAD_RESPONSE | grep -o '"session_id":"[^"]*' | cut -d'"' -f4)

# 2. Check session details (see what was extracted)
curl http://localhost:8000/sessions/$SESSION_ID | json_pp

# 3. Ask a specific question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d "{
    \"question\": \"What are the main topics covered in this document?\",
    \"session_id\": \"$SESSION_ID\"
  }" | json_pp
```

## Common Issues & Solutions

### Issue: "No information about X"
**Cause**: The PDF doesn't contain information about X, OR you're asking about the wrong thing
**Solution**: Ask about what's actually IN the PDF

### Issue: num_chunks = 0
**Cause**: PDF is images, not text
**Solution**: Use OCR to convert images to text first, or use a different PDF

### Issue: Generic answers
**Cause**: Question is too vague or broad
**Solution**: Ask specific questions about the content

### Issue: Wrong answers
**Cause**: Retrieval not finding relevant chunks, or chunk size too small/large
**Solution**: Adjust CHUNK_SIZE in config.py (try 500-2000)

## Need Help?

Please share:
1. What PDF are you uploading? (topic/content)
2. The upload response (especially `num_chunks`)
3. The session details output
4. The exact question you're asking

This will help diagnose the issue!
