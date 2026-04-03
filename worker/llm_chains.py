import os
import io
import logging
from PyPDF2 import PdfReader
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# Our highly strict schema
from schemas import InvoiceInformation

logger = logging.getLogger("NexusParse.Worker.LLaMA")

# Langchain currently has native support for Pydantic using "with_structured_output"
# We will use o1-preview or a fallback model
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "o1-preview")

def extract_text_from_pdf(local_pdf_path: str) -> str:
    """Uses PyPDF2 to extract raw text (in production, OCR might be needed for scanned PDFs)."""
    text = ""
    with open(local_pdf_path, "rb") as f:
        reader = PdfReader(f)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    return text

def run_extraction_chain(raw_text: str) -> dict:
    """
    Invokes the LLM to extract data based strictly on our Pydantic Schema.
    """
    # Note: o1-preview doesn't perfectly support temperature mapping in the same way, 
    # but langchain handles the model wrapping.
    llm = ChatOpenAI(
        model=OPENAI_MODEL, 
        temperature=0, 
        api_key=os.getenv("OPENAI_API_KEY", "dummy")
    )
    
    # We bind our schema. This enforces the LLM to output accurate JSON
    structured_llm = llm.with_structured_output(InvoiceInformation)
    
    prompt = f"""
    You are an expert AI Data Extraction assistant. 
    Analyze the following raw text extracted from a parsed PDF and extract all requested fields according to the schema.
    If a required field is missing, infer it safely or omit it if not possible (relying on validation to throw errors).
    Ensure all mathematical calculations are strictly accurate (e.g. quantity * unit_price = total_price).
    
    Raw Text:
    {raw_text}
    """
    
    logger.info("Invoking LLM for structured extraction...")
    result: InvoiceInformation = structured_llm.invoke(prompt)
    
    # Return as dict, safely validated
    return result.model_dump(mode="json")
