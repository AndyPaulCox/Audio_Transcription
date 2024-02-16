from .assistant_backend import embed_documents
from .assistant_backend import create_faiss_index
from .assistant_backend import gpt_query_processing
from .assistant_backend import search_index
from .assistant_backend import save_faiss_index
from .assistant_backend import search_documents
from .assistant_backend import tokenize_and_save_chunks
from .assistant_backend import update_chat_history

# Package-level variable
__all__ = ['embed_documents','create_faiss_index','gpt_query_processing','search_documents','search_index','save_faiss_index','tokenize_and_save_chunks','load_documents','update_chat_history']

# Initialization code
print("Initializing project assistant...")

# You can also define any package-level functions or variables here
