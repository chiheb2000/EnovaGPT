import os
import shutil
from typing import List
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from fonction.embedding_function import get_embedding_function
from langchain_community.vectorstores import Chroma
CHROMA_PATH = "c:/Users/chatt/Desktop/Nouveau dossier/Stage enova/chroma"
DATA_PATH = "C:/Users/chatt/Desktop/Nouveau dossier/Stage enova/Data"

def main(reset=False):
    if reset:
        print("✨ Clearing Database")
        clear_database()

    documents = load_documents()
    chunks = split_documents(documents)
    add_to_chroma(chunks)
    
def load_documents():
    document_loader = PyPDFDirectoryLoader(DATA_PATH)
    return document_loader.load()

def split_documents(documents: List[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=750,
        chunk_overlap=100,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)

def add_to_chroma(chunks: List[Document]):
        # Obtenir la fonction d'embedding à utiliser pour la vectorisation.
    embedding_function = get_embedding_function()
    
        # Initialiser le stockage vectoriel Chroma.

    db = Chroma(
        persist_directory=CHROMA_PATH, embedding_function=embedding_function
    )
    
    # Attribuer des identifiants uniques aux fragments et vérifier les doublons dans la base de données.
    chunks_with_ids = calculate_chunk_ids(chunks)
    existing_items = db.get(include=[])
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")
    # Filtrer les fragments déjà présents dans la base de données.
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)
            
    # Ajouter les nouveaux fragments à la base de données et sauvegarder les changements.

    if len(new_chunks):
        print(f"👉 Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_texts(
            texts=[chunk.page_content for chunk in new_chunks],
            metadatas=[chunk.metadata for chunk in new_chunks],
            ids=new_chunk_ids
        )
        db.persist()
    else:
        print("✅ No new documents to add")

def calculate_chunk_ids(chunks: List[Document]):
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        chunk.metadata["id"] = chunk_id

    return chunks

def clear_database():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

if __name__ == "__main__":
    main()
