
import os
from langchain_groq import ChatGroq
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS

from dotenv import load_dotenv

load_dotenv()

## load the GROQ And OpenAI API KEY 
os.environ['OPENAI_API_KEY']=os.getenv("OPENAI_API_KEY")
groq_api_key=os.getenv('GROQ_API_KEY')


llm=ChatGroq(groq_api_key=groq_api_key,
            model_name="Llama3-8b-8192")

prompt=ChatPromptTemplate.from_template(
"""
Answer the questions based on the provided context only.
Please provide the most accurate response based on the question
<context>
{context}
<context>
Questions:{input}

"""
)

yt_url = "https://www.youtube.com/watch?v=TOvPlPi1rSE"
user_prompt = "Quelle sont les 5 points positif du film ?"

vectors=None


def vector_embedding():
    if vectors != None:
        return vectors
    
    transcript = get_transcript(yt_url)
    embeddings = OpenAIEmbeddings()
    
    # Chunk Creation
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
    final_documents = text_splitter.split_text(transcript)
    
    # vector OpenAI embeddings
    vectors = FAISS.from_documents(final_documents,embeddings)
    
    return vectors

def get_transcript(yt_url):
    return "transcript"


def main(user_prompt, yt_url):
    vectors = vector_embedding(yt_url)

    document_chain=create_stuff_documents_chain(llm,prompt)
    retriever=vectors.as_retriever()
    retrieval_chain=create_retrieval_chain(retriever,document_chain)
    
    response=retrieval_chain.invoke({'input':user_prompt})

    # Find the relevant chunks
    for i, doc in enumerate(response["context"]):
        print(doc.page_content)
        print("--------------------------------")


main(user_prompt, yt_url)







#----------------------------------------------------------------------------------------------------------------------------


from Scrapper import Scrapper

import os
from typing import Optional, List
from langchain_groq import ChatGroq
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from dotenv import load_dotenv


class TranscriptRAG:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        load_dotenv()
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.openai_api_key or not self.groq_api_key:
            raise ValueError("Missing API keys in .env file")
        
        self.llm = ChatGroq(
            groq_api_key=self.groq_api_key,
            model_name="llama3-8b-8192"
        )
        self.embeddings = OpenAIEmbeddings()
        
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

    def get_transcript(self, youtube_url: str) -> str:
        s = Scrapper(youtube_url)
        return s.get_transcript()

    def create_vectorstore(self, transcript: str) -> FAISS:
        # Split text into chunks
        chunks = self.text_splitter.split_text(transcript)
        
        # Create documents
        documents = [Document(page_content=chunk) for chunk in chunks]
        
        # Create vector store
        return FAISS.from_documents(documents, self.embeddings)

    def process_transcript(self, youtube_url: str) -> None:
        transcript = self.get_transcript(youtube_url)
        self.vectorstore = self.create_vectorstore(transcript)

    def query_transcript(self, question: str, k: int = 4) -> dict:
        if not self.vectorstore:
            raise ValueError("No transcript has been processed yet")
        
        # Create retrieval chain
        retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )
        
        # Get relevant documents
        relevant_docs = retriever.get_relevant_documents(question)
        
        # Create and run the chain
        chain = (
            self.prompt
            | self.llm
            | StrOutputParser()
        )
        
        # Get response
        response = chain.invoke({
            "context": "\n".join(doc.page_content for doc in relevant_docs),
            "question": question
        })
        
        return {
            "answer": response,
            "relevant_chunks": [doc.page_content for doc in relevant_docs]
        }

def main():
    # Example usage
    rag = TranscriptRAG()
    
    # Process video transcript
    video_url = "https://www.youtube.com/watch?v=TOvPlPi1rSE"
    try:
        rag.process_transcript(video_url)
        print("Transcript processed successfully!")
        
        # Query the transcript
        question = "Quelle sont les 5 points positif du film ?"
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