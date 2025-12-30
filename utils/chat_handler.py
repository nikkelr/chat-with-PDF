"""Chat handler for managing conversations and LLM interactions."""

from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import config


def create_conversation_chain(vector_store):
    """
    Create a retrieval QA chain with OpenRouter LLM.
    
    Args:
        vector_store: FAISS vector store with document embeddings
        
    Returns:
        RetrievalQA: Chat chain with retrieval
    """
    # Initialize ChatOpenAI with OpenRouter configuration
    llm = ChatOpenAI(
        openai_api_key=config.OPENROUTER_API_KEY,
        openai_api_base=config.OPENROUTER_API_BASE,
        model_name=config.OPENROUTER_MODEL,
        temperature=config.TEMPERATURE,
        max_tokens=config.MAX_TOKENS,
        model_kwargs={
            "extra_headers": {
                "HTTP-Referer": config.OPENROUTER_APP_URL,
                "X-Title": config.OPENROUTER_APP_NAME,
            }
        }
    )
    
    # Create a custom prompt template to ensure context is used
    prompt_template = """Use the following pieces of context from the document to answer the question at the end. 
If you don't know the answer based on the context, just say that you don't have enough information in the document to answer this question.

Context from the document:
{context}

Question: {question}

Answer based on the document:"""
    
    PROMPT = PromptTemplate(
        template=prompt_template, 
        input_variables=["context", "question"]
    )
    
    # Create retrieval QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 4}
        ),
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )
    
    return qa_chain


def get_response(qa_chain, user_question):
    """
    Get response from the QA chain.
    
    Args:
        qa_chain: Retrieval QA chain
        user_question (str): User's question
        
    Returns:
        dict: Response containing answer and source documents
    """
    # Use 'query' instead of 'question' for RetrievalQA
    response = qa_chain({"query": user_question})
    
    # Rename 'result' to 'answer' for consistency with API
    if 'result' in response:
        response['answer'] = response.pop('result')
    
    return response
