from Scrapper import Scrapper

import os
from typing import Optional, List
from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

# Disable symlinks warning
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

DEFAULT_MODEL = "llama3-8b-8192"

class TranscriptRAG:
    def __init__(self, chunk_size: int = 5000, chunk_overlap: int = 500):
        load_dotenv()
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        
        if not self.groq_api_key:
            raise ValueError("Missing Groq API key in .env file")
        
        self.llm = ChatGroq(
            groq_api_key=self.groq_api_key,
            model_name=DEFAULT_MODEL
        )
        
        # Initialize HuggingFace Embeddings with updated configuration
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            cache_folder=os.path.join(os.getcwd(), 'models_cache'),
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Configure text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            add_start_index=True,
        )

        self.prompt = ChatPromptTemplate.from_template("""
            You are a helpful AI assistant that answers questions based on video transcripts.
            Use only the following context to answer the question. If you're unsure or the 
            information isn't in the context, say so.

            Context:
            {context}

            Question: {question}

            Answer: Let me help you with that based on the video transcript.
        """)
        
        self.vectorstore: Optional[FAISS] = None
        
        # Create cache directory if it doesn't exist
        os.makedirs(os.path.join(os.getcwd(), 'models_cache'), exist_ok=True)

    def get_transcript(self, youtube_url: str) -> str:
        s = Scrapper(youtube_url)
        return s.get_transcript()

    def create_vectorstore(self, transcript: str) -> FAISS:
        # Split text into chunks
        chunks = self.text_splitter.split_text(transcript)
        
        # Create documents
        documents = [Document(page_content=chunk) for chunk in chunks]
        
        # Create vector store
        vectorstore = FAISS.from_documents(documents, self.embeddings)
        
        # Save the vectorstore locally
        vectorstore.save_local("faiss_index")
        
        return vectorstore

    def process_transcript(self, youtube_url: str) -> None:
        transcript = self.get_transcript(youtube_url)
        self.vectorstore = self.create_vectorstore(transcript)
        print("Transcript processed successfully!")

    def query_transcript(self, question: str, k: int = 7) -> dict:
        if not self.vectorstore:
            # Try to load existing vectorstore
            if os.path.exists("faiss_index"):
                self.vectorstore = FAISS.load_local("faiss_index", self.embeddings)
            else:
                raise ValueError("No transcript has been processed yet")
        
        # Create retrieval chain
        retrieval_chain = (
            self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": k}
            )
        )
        
        # Get relevant documents
        relevant_docs = retrieval_chain.invoke(question)
        
        # Create and run the QA chain
        qa_chain = (
            self.prompt
            | self.llm
            | StrOutputParser()
        )
        
        # Get response
        response = qa_chain.invoke({
            "context": "\n".join(doc.page_content for doc in relevant_docs),
            "question": question
        })
        
        return {
            "answer": response,
            "relevant_chunks": [doc.page_content for doc in relevant_docs]
        }

def main():
    rag = TranscriptRAG()
    video_url = "https://www.youtube.com/watch?v=TOvPlPi1rSE"
    question = "Quelle sont les 5 points positif du film ?"
    
    try:
        rag.process_transcript(video_url)
        response = rag.query_transcript(question)
        
        print("\nAnswer:")
        print(response["answer"])
        
        print("\nRelevant chunks used:")
        for i, chunk in enumerate(response["relevant_chunks"], 1):
            print(f"\nChunk {i}:")
            print(chunk)
            print("-" * 50)
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()