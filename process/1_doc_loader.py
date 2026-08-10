import logging
from pathlib import Path
from typing import List

from common.logger import get_logger
from common.custom_exception import CustomException

from langchain_core.documents import Document
from langchain_community.document_loaders import (
    DirectoryLoader, 
    PyPDFLoader, 
    Docx2txtLoader
)

# 1. Configure Production Logging
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# )
# logger = logging.getLogger(__name__)

logger = get_logger(__name__)


def load_docs_from_folder(folder_name: str) -> List[Document]:
    """
    Loads PDF and Google Docs (exported as .docx) files from a specified folder.
    
    Args:
        folder_name (str): The path to the folder containing the documents.
        
    Returns:
        List[Document]: A list of LangChain Document objects containing parsed text and metadata.
    """
    folder_path = Path(folder_name)
    
    # Validate that the folder exists before attempting to load
    if not folder_path.exists() or not folder_path.is_dir():
        logger.error(f"The directory '{folder_name}' does not exist or is not a valid folder.")
        raise FileNotFoundError(f"Directory not found: {folder_name}")

    loaded_documents: List[Document] = []
    
    # 2. Define our loaders using a mapping strategy
    # We use glob patterns to include specific file types
    loaders_config = {
        "PDFs": {
            "glob": "**/*.pdf",
            "loader_cls": PyPDFLoader # Ideal for simple PDFs
        },
        "Google Docs / Word": {
            "glob": "**/*.docx",
            "loader_cls": Docx2txtLoader 
        }
    }

    # 3. Iterate over configurations and load documents
    for doc_type, config in loaders_config.items():
        logger.info(f"Initializing loader for {doc_type} in '{folder_name}'...")
        
        try:
            loader = DirectoryLoader(
                path=str(folder_path),
                glob=config["glob"],
                loader_cls=config["loader_cls"],
                show_progress=True,           # Helpful for monitoring logs
                use_multithreading=True,      # Enables parallel loading
                silent_errors=True            # Skips corrupted files without crashing the job
            )
            
            docs = loader.load()
            loaded_documents.extend(docs)
            logger.info(f"Successfully loaded {len(docs)} {doc_type} document(s).")
            
        except Exception as e:
            # Catch unexpected errors during the directory load process
            error_message = CustomException("Faialed to load files",e)
            logger.error(str(error_message))
            logger.error(f"Failed to load {doc_type} from '{folder_name}'. Error: {str(e)}")

    logger.info(f"Completed document ingestion. Total documents loaded: {len(loaded_documents)}")
    return loaded_documents

# ==========================================
# Example Usage
# ==========================================
if __name__ == "__main__":
    TARGET_FOLDER = "doc_dump"
    
    try:
        # Create the folder if it doesn't exist for testing purposes
        Path(TARGET_FOLDER).mkdir(exist_ok=True)
        
        # Execute the reusable function
        all_documents = load_docs_from_folder(TARGET_FOLDER)
        
        # Verify output
        if all_documents:
            print(f"Sample content from first document: {all_documents[0].page_content[:200]}...")
            print(f"Metadata from first document: {all_documents[0].metadata}")
            
    except Exception as e:
        logger.critical(f"Critical failure during document ingestion pipeline: {e}")