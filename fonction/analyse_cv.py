
import os
from langchain_community.vectorstores import Chroma
from langchain.schema import Document

CHROMA_PATH = "C:/Users/chatt/Desktop/Nouveau dossier/Stage enova/chroma"
DATA_PATH = "C:/Users/chatt/Desktop/Nouveau dossier/Stage enova/Data"

# Templates for LLM prompts
PROMPT_TEMPLATE = """
Given the following job description, find the most relevant resumes from the database and summarize why they are a good fit.

Job Description:
{job_description}

Relevant Resumes:
{relevant_resumes}

Summary:
"""
DETAILS_TEMPLATE = """
You are an assistant that extracts specific details from resumes. Given the resume content below, extract the following information:

1. Name
2. Contact Information
3. Skills
4. Experience
5. Education

Resume Content:
{resume_content}

Extracted Details:
"""
def query_profiles(post_description: str, embedding_function, llm):
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    # Rechercher les chunks similaires
    results = db.similarity_search_with_score(post_description)

    # Grouper les chunks par CV
    grouped_results = {}
    for doc, score in results:
        source = doc.metadata.get("source")
        if source not in grouped_results:
            grouped_results[source] = []
        grouped_results[source].append((doc, score))

    # Calculer un score moyen pour chaque CV
    averaged_results = []
    for source, docs in grouped_results.items():
        total_score = sum(score for _, score in docs)
        average_score = total_score / len(docs)
        combined_doc_content = "\n\n".join([doc.page_content for doc, _ in docs])
        combined_doc = Document(page_content=combined_doc_content, metadata={"source": source})
        averaged_results.append((combined_doc, average_score))

    # Trier les résultats par score moyen
    averaged_results.sort(key=lambda x: x[1], reverse=False)

    # Préparer les résumés pertinents pour le prompt
    relevant_resumes = "\n\n".join([f"Resume {i+1} (Score: {score}):\n{doc.page_content[:500]}..." for i, (doc, score) in enumerate(averaged_results[:3])])
    prompt = PROMPT_TEMPLATE.format(job_description=post_description, relevant_resumes=relevant_resumes)
    response_text = llm.invoke(prompt)
    sources = [doc.metadata.get("source", None) for doc, _score in averaged_results[:3]]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    return averaged_results, formatted_response

def extract_candidate_details(llm, resume_content):
    prompt = DETAILS_TEMPLATE.format(resume_content=resume_content)
    details = llm.invoke(prompt)
    return details

def upload_and_save_pdf(uploaded_file):
    if uploaded_file is not None:
        file_path = os.path.join(DATA_PATH, uploaded_file.name)
        if os.path.exists(file_path):
            return False, "File already exists."
        else:
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            return True, "PDF uploaded successfully."
    return False, "No file uploaded."