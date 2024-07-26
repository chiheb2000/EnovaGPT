from langchain_huggingface import HuggingFaceEmbeddings
def get_embedding_function():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", 
                                       model_kwargs={'device': 'cpu'})
    return embeddings
