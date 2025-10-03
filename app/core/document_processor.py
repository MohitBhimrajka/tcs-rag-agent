# app/core/document_processor.py
import os
import pandas as pd
from typing import Tuple
import logging  # <-- ADD THIS

# LangChain Imports
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
# UPDATE THIS IMPORT
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_core.documents import Document

# Table parsing library
import camelot

# --- ADD THIS SECTION TO SUPPRESS PDFMINER WARNINGS ---
# pdfminer logs a lot of "warnings" that aren't actual problems for Camelot.
# This silences them to keep the output clean.
logging.getLogger("pdfminer").setLevel(logging.ERROR)
# --- END OF SECTION ---

class DocumentProcessor:
    """
    Handles the multi-modal loading, processing, and vectorization of a PDF document,
    creating separate stores for text and table data.
    """

    def __init__(self, pdf_path: str):
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"The specified PDF file does not exist: {pdf_path}")
        self.pdf_path = pdf_path
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )

    def _convert_tables_to_docs(self, tables) -> list[Document]:
        """Converts extracted tables into LangChain Document objects."""
        table_docs = []
        for i, table in enumerate(tables):
            # Clean the DataFrame
            table.df = table.df.replace(r'\n', ' ', regex=True)
            table.df = table.df.dropna(how='all', axis=1).dropna(how='all', axis=0)
            
            if table.df.empty:
                continue

            # Convert DataFrame to markdown string for better LLM readability
            markdown_table = table.df.to_markdown(index=False)
            
            # Create a Document object with rich metadata
            doc = Document(
                page_content=f"--- TABLE {i+1} FROM PAGE {table.page} ---\n\n{markdown_table}",
                metadata={
                    "source": os.path.basename(self.pdf_path), 
                    "page": table.page,
                    "type": "table"
                }
            )
            table_docs.append(doc)
        return table_docs

    def process_and_store(self, text_store_path: str, table_store_path: str = None):
        """
        Processes the PDF for both text and tables and saves them to separate FAISS vector stores.
        If table_store_path is None or empty, only processes text (backward compatibility).
        """
        # 1. Process and store TEXT chunks
        print(f"--- Processing Text from: {self.pdf_path} ---")
        loader = PyMuPDFLoader(self.pdf_path)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        text_chunks = text_splitter.split_documents(documents)
        
        print(f"Creating TEXT vector store at: {text_store_path}")
        text_vector_store = FAISS.from_documents(documents=text_chunks, embedding=self.embedding_model)
        text_vector_store.save_local(text_store_path)
        print("TEXT vector store saved successfully.")

        # 2. Process and store TABLE chunks (only if table_store_path is provided)
        if table_store_path:
            print(f"\n--- Processing Tables from: {self.pdf_path} ---")
            try:
                # Using 'stream' flavor for better layout detection in financial reports
                # This can be slow, as it analyzes the entire PDF for tables.
                tables = camelot.read_pdf(self.pdf_path, pages='all', flavor='stream', suppress_stdout=True)
                print(f"Found {len(tables)} potential table structures.")
                
                table_docs = self._convert_tables_to_docs(tables)
                
                if table_docs:
                    print(f"Creating TABLE vector store from {len(table_docs)} valid tables at: {table_store_path}")
                    table_vector_store = FAISS.from_documents(documents=table_docs, embedding=self.embedding_model)
                    table_vector_store.save_local(table_store_path)
                    print("TABLE vector store saved successfully.")
                else:
                    print("No valid tables were converted to documents, skipping table store creation.")

            except Exception as e:
                print(f"Could not process tables with Camelot: {e}. Skipping table processing.")

    @staticmethod
    def load_retriever(store_path: str, table_store_path: str = None) -> VectorStoreRetriever:
        """
        Backward compatibility method: Loads a single FAISS vector store from disk and returns a retriever instance.
        """
        if not os.path.exists(store_path):
            raise FileNotFoundError(f"Vector store not found at path: {store_path}")
        
        print(f"Loading retriever from: {store_path}")
        embedding_model = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        vector_store = FAISS.load_local(store_path, embedding_model, allow_dangerous_deserialization=True)
        return vector_store.as_retriever(search_kwargs={"k": 5})

    @staticmethod
    def load_retrievers(text_store_path: str, table_store_path: str) -> Tuple[VectorStoreRetriever, VectorStoreRetriever | None]:
        """
        Loads both text and table FAISS vector stores from disk and returns retriever instances.
        """
        embedding_model = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )

        # Load Text Retriever
        if not os.path.exists(text_store_path):
            raise FileNotFoundError(f"TEXT vector store not found at path: {text_store_path}")
        print(f"Loading TEXT retriever from: {text_store_path}")
        text_vector_store = FAISS.load_local(text_store_path, embedding_model, allow_dangerous_deserialization=True)
        text_retriever = text_vector_store.as_retriever(search_kwargs={"k": 5})

        # Load Table Retriever (it's okay if it doesn't exist)
        table_retriever = None
        if os.path.exists(table_store_path):
            print(f"Loading TABLE retriever from: {table_store_path}")
            table_vector_store = FAISS.load_local(table_store_path, embedding_model, allow_dangerous_deserialization=True)
            table_retriever = table_vector_store.as_retriever(search_kwargs={"k": 5})
        else:
            print("Table vector store not found. Proceeding without table retriever.")

        return text_retriever, table_retriever