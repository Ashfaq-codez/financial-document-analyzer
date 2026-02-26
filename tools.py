import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from crewai.tools import BaseTool

# Load environment variables (like OPENAI_API_KEY)
load_dotenv()

class ReadFinancialDocumentTool(BaseTool):
    # Define the tool name and description clearly so the AI knows exactly when and how to use it
    name: str = "read_financial_document"
    description: str = "Reads and extracts text from a financial PDF document. Requires the file path as input."

    def _run(self, path: str) -> str:
        """Core logic to locate, read, and clean the text from the PDF."""
        
        # 1. Verify the file actually exists before trying to read it
        if not os.path.exists(path):
            return f"Error: File not found at {path}"

        try:
            # 2. Load the document
            loader = PyPDFLoader(path)
            docs = loader.load()

            # 3. Extract and format the text
            full_text = ""
            for page in docs:
                content = page.page_content.strip()
                
                # Clean up extra blank lines to make the text highly readable for the LLM
                while "\n\n" in content:
                    content = content.replace("\n\n", "\n")
                    
                full_text += content + "\n"

            # 4. Safety limit to prevent exceeding token limits on massive documents
            MAX_CHARS = 15000
            if len(full_text) > MAX_CHARS:
                return full_text[:MAX_CHARS] + "\n...[Text truncated due to length]..."
                
            return full_text
            
        except Exception as e:
            return f"Error reading PDF: {str(e)}"

# Instantiate the tool so it can be imported cleanly into tasks.py and agents.py
read_data_tool = ReadFinancialDocumentTool()