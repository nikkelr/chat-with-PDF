# Context Retrieval Fix

## Problem Identified

The LLM was responding with "I don't have access to the PDF" even though:
- ✅ PDF was uploaded successfully
- ✅ Text was extracted
- ✅ Embeddings were created
- ✅ Chunks were stored in FAISS

**Root Cause:** The `ConversationalRetrievalChain` wasn't properly configured to pass retrieved context to the OpenRouter LLM.

## Solution Applied

Replaced `ConversationalRetrievalChain` with `RetrievalQA` + explicit prompt template.

### What Changed

**File:** `utils/chat_handler.py`

**Before:**
- Used `ConversationalRetrievalChain` (complex, designed for OpenAI)
- Relied on default prompting
- Context wasn't reliably passed to OpenRouter

**After:**
- Uses `RetrievalQA` with `chain_type="stuff"` (simpler, more reliable)
- **Explicit prompt template** that instructs LLM to use context
- Retrieves 4 most similar chunks (increased from 3)
- Maps `result` → `answer` for API consistency

### New Prompt Template

```
Use the following pieces of context from the document to answer the question at the end. 
If you don't know the answer based on the context, just say that you don't have enough 
information in the document to answer this question.

Context from the document:
{context}

Question: {question}

Answer based on the document:
```

This explicitly tells the LLM:
1. Use the provided context
2. Context comes from the document
3. Only answer based on what's in the document

## Testing

### Method 1: Test Script

```bash
python test_pdf_context.py yourfile.pdf "What is this document about?"
```

This will:
1. Upload your PDF
2. Show extracted sample text
3. Ask your question
4. Show if context is working
5. Clean up session

### Method 2: Manual Test

```bash
# 1. Restart API (IMPORTANT!)
python api.py

# 2. Upload PDF
curl -X POST http://localhost:8000/upload -F "file=@test.pdf"

# 3. Copy session_id from response, then ask
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Summarize this document",
    "session_id": "YOUR_SESSION_ID"
  }'
```

## Expected Results

### ✅ Good Response (Context Working)
- Answers based on actual PDF content
- Mentions specific details from the document
- Provides relevant information

### ❌ Bad Response (Context Not Working)
- "I don't have access"
- "I can't view PDF documents"
- Generic responses not based on content

## Trade-offs

**Lost:**
- ❌ Conversation memory (no follow-up context between questions)

**Gained:**
- ✅ Reliable context retrieval
- ✅ Works with OpenRouter
- ✅ Simpler chain = fewer failure points
- ✅ Explicit prompting = better control

## Adding Memory Back (Optional)

If you need conversation history, you can:

1. Store chat history in session (already done in API)
2. Manually include previous Q&A in the question
3. Use a custom chain that combines QA + memory

For most use cases, single-question QA is sufficient.

## Verification Checklist

- [ ] Restarted API after changes
- [ ] Uploaded a new PDF (old sessions won't work)
- [ ] Asked about content actually in the PDF
- [ ] Checked response mentions specific details
- [ ] Verified sample_text shows correct extraction

## Still Having Issues?

1. **Check sample_text** in session details - is it correct?
2. **Verify num_chunks > 0** - was text extracted?
3. **Ask specific questions** - not just "summarize"
4. **Try different PDF** - ensure it's actual text, not scanned images
5. **Check OpenRouter API** - is the key working?

Run the test script for automatic verification:
```bash
python test_pdf_context.py your.pdf
```
