import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
from io import BytesIO
from langchain_community.llms import LlamaCpp, HuggingFaceHub
from fonction.create_database import main as update_database
from fonction.embedding_function import get_embedding_function
from streamlit_option_menu import option_menu
from fonction.generation_post import generate_recruitment_post
from fonction.analyse_cv import query_profiles, upload_and_save_pdf
from fonction.scraping_linkdln import login_and_save_cookies, load_cookies_and_get_driver, get_linkedin_profiles
import os

# Paths and Constants
MODEL_PATH = "C:/Users/chatt/Desktop/Nouveau dossier/Stage enova/models/mistral-7b-instruct-v0.1.Q5_K_M.gguf"
DATA_PATH = "C:/Users/chatt/Desktop/Nouveau dossier/Stage enova/Data"
HUGGINGFACEHUB_API_TOKEN = "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"

# Function to initialize the LlamaCpp model
@st.cache_resource
def initialize_llm():
    return LlamaCpp(
        streaming=False,
        model_path=MODEL_PATH,
        temperature=0.75,
        top_p=0.9,
        verbose=True,
        n_ctx=4096,
    )

# Function to initialize the HuggingFaceHub model
@st.cache_resource
def initialize_llmsmall():
    repo_id = "facebook/opt-125m"
    return HuggingFaceHub(
        huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN,
        repo_id=repo_id,
        model_kwargs={"temperature": 0.7, "max_length": 150}
    )

# Function to display a PDF file
def display_pdf(file_path):
    with fitz.open(file_path) as pdf:
        num_pages = pdf.page_count
        for page_num in range(num_pages):
            page = pdf.load_page(page_num)
            pix = page.get_pixmap()
            image_bytes = pix.tobytes("png")
            st.image(BytesIO(image_bytes))

# Function to display search results
def display_search_results(results):
    if results:  # Ensure results is not None
        for i, (doc, score) in enumerate(results[:3]):
            pdf_path = os.path.join(DATA_PATH, doc.metadata.get('source'))
            if os.path.exists(pdf_path):
                with st.expander(f"CV {i+1} (Score: {score})"):
                    display_pdf(pdf_path)
            else:
                st.write(f"File {pdf_path} not found.")
    else:
        st.write("No results to display.")

# Function to reset session state when job title changes
def reset_state_if_job_title_changed(new_job_title):
    if 'previous_job_title' not in st.session_state:
        st.session_state['previous_job_title'] = new_job_title

    if new_job_title != st.session_state['previous_job_title']:
        st.session_state['cv_results'] = None
        st.session_state['cv_response_text'] = None
        st.session_state['linkedin_profiles'] = None
        st.session_state['previous_job_title'] = new_job_title

# Main function
def main():
    st.set_page_config(page_title="Enova Robotics Recruitment and CV Analysis", layout="wide")
    logo_path = "logoEnovaRobotics-1.png"

    st.markdown(
        """
        <style>
        .title {
            text-align: center;
            color: #0047ab;
            font-size: 42px;
            font-weight: bold;
        }
        .subheader-center {
            text-align: center;
            font-size: 32px;
            font-weight: bold.
        }
        .centered-table {
            display: flex;
            justify-content: center;
            margin: auto.
        }
        .centered-cv {
            display: flex.
            justify-content: center.
            align-items: center.
            flex-direction: column.
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.image(logo_path, width=200)
    st.markdown('<p class="title">Plateforme RH - EnovaGPT 🤖</p>', unsafe_allow_html=True)

    llm = initialize_llm()
    llm2 = initialize_llmsmall()
    embedding_function = get_embedding_function()

    action = option_menu(
        None,
        ["Generate Recruitment Post", "Analyze CVs", "Profile LinkedIn", "Results"],
        icons=["bi bi-pencil-square", "file-earmark-text", "bi bi-linkedin", "bi bi-check-circle"],
        default_index=0,
        orientation="horizontal"
    )

    if action == "Generate Recruitment Post":
        st.markdown('<p class="subheader-center">Generate Recruitment Post 💻</p>', unsafe_allow_html=True)
        job_title = st.text_input("🧑‍💻 Job Title:", value=st.session_state.get('job_title', ''))
        
        reset_state_if_job_title_changed(job_title)

        if not job_title:
            st.session_state['job_title'] = ''
        type_contrat = st.selectbox("📑 Contract Type:", ["Permanent", "Temporary", "Internship"])
        salaire = None
        duree_stage = None

        if type_contrat == "Internship":
            duree_stage = st.text_input("Internship Duration (e.g., 6 months):")
        else:
            salaire = st.text_input("💰 Salary Range (e.g., 20,000 to 30,000 Dinars annually):")

        submit_button = st.button("Generate Recruitment Post 📝")
        if submit_button and job_title and type_contrat and (salaire or duree_stage):
            st.session_state['job_title'] = job_title  # Set global job title
            with st.spinner('Generating the recruitment post...'):
                recruitment_post = generate_recruitment_post(llm2, job_title, type_contrat, salaire, duree_stage)
            st.success("Recruitment post generated successfully!")
            st.text_area("Recruitment Post", recruitment_post, height=300, key="recruitment_post_area")

    elif action == "Analyze CVs":
        st.markdown('<p class="subheader-center">Analyze CVs 🪪</p>', unsafe_allow_html=True)

        uploaded_file = st.file_uploader("Upload a PDF resume", type=['pdf'])
        if uploaded_file is not None:
            success, message = upload_and_save_pdf(uploaded_file)
            if success:
                st.success(message)
                update_database(reset=False)
            else:
                st.error(message)

        if st.button("Reset Database 🔄"):
            with st.spinner('Resetting the database...'):
                update_database(reset=True)
            st.success("Database has been reset!")

        poste = st.session_state.get('job_title', '')
        if not poste:
            poste = st.text_input("Enter the job title for the CV search:", value=st.session_state.get('job_titlecv', ''))
            st.session_state['job_titlecv'] = poste 
        st.write(f"Job title for CV search: {poste}")
        submit_button = st.button("Search CVs 🔍")
        if submit_button and poste:
            with st.spinner('Searching compatible profiles...'):
                results, response_text = query_profiles(poste, embedding_function, llm2)
                st.session_state['cv_results'] = results
                st.session_state['cv_response_text'] = response_text
                st.success("Search completed!")
       
        if st.session_state.get("cv_results") and st.session_state.get("cv_response_text"):
            st.text_area("Search Results", st.session_state['cv_response_text'], height=400, key="cv_search_results_area")
            display_search_results(st.session_state['cv_results'])

    elif action == "Profile LinkedIn":
        st.markdown('<p class="subheader-center">Profile LinkedIn 🔗</p>', unsafe_allow_html=True)
        st.write("Utilisez ce formulaire pour chercher des profils LinkedIn en fonction du titre de poste.")

        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False

        if not st.session_state.authenticated:
            if st.button("Se connecter à LinkedIn"):
                login_and_save_cookies()
                st.session_state.authenticated = True
                st.success("Connecté à LinkedIn avec succès!")

        if st.session_state.authenticated:
            job_title_link = st.session_state.get('job_title', '')
            if not job_title_link:
                job_title_link = st.text_input("Titre du poste recherché", value=st.session_state.get('job_titlelink', ''))
                st.session_state['job_titlelink'] = job_title_link 
            st.write(f"Job title for LinkedIn search: {job_title_link}")

            if st.button("Chercher"):
                driver = load_cookies_and_get_driver()
                profiles = get_linkedin_profiles(driver, job_title_link)
                driver.quit()
                st.session_state['linkedin_profiles'] = profiles

            if "linkedin_profiles" in st.session_state:
                profiles = st.session_state['linkedin_profiles']
                if profiles:
                    st.write(f"Trouvé {len(profiles)} profils:")
                    profiles_df = pd.DataFrame(profiles)

                    def create_button(link, label):
                        return f'<a href="{link}" target="_blank"><button>{label}</button></a>'

                    profiles_df['link'] = profiles_df['link'].apply(lambda x: create_button(x, 'Voir Profil LinkedIn'))

                    st.markdown(
                        f'<div class="centered-table">{profiles_df.to_html(escape=False, index=False)}</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.write("Aucun profil trouvé.")

    elif action == "Results":
        st.markdown('<p class="subheader-center">Results 📊</p>', unsafe_allow_html=True)

        job_title_cv = st.session_state.get('job_titlecv', '')
        job_title_link = st.session_state.get('job_titlelink', '')
        job_title_global = st.session_state.get('job_title', '')

        if job_title_global:
            st.markdown(f"### Results for Job Title: {job_title_global}")

            if 'cv_results' in st.session_state:
                st.markdown("### CV Analysis Results")
                display_search_results(st.session_state['cv_results'])

            if 'linkedin_profiles' in st.session_state:
                st.markdown("### LinkedIn Profile Results")
                profiles = st.session_state['linkedin_profiles']
                if profiles:
                    st.write(f"Found {len(profiles)} profiles:")
                    profiles_df = pd.DataFrame(profiles)

                    def create_button(link, label):
                        return f'<a href="{link}" target="_blank"><button>{label}</button></a>'

                    profiles_df['link'] = profiles_df['link'].apply(lambda x: create_button(x, 'Voir Profil LinkedIn'))

                    st.markdown(
                        f'<div class="centered-table">{profiles_df.to_html(escape=False, index=False)}</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.write("No profiles found.")
        else:
            st.write("Please set a job title in the 'Generate Recruitment Post' section first.")
            
        if job_title_cv and job_title_link:
            st.markdown(f"### Results for Job Title: {job_title_cv} ")
            if job_title_cv == job_title_link:
                if 'cv_results' in st.session_state:
                    st.markdown("### CV Analysis Results")
                    display_search_results(st.session_state['cv_results'])

                if 'linkedin_profiles' in st.session_state:
                    st.markdown("### LinkedIn Profile Results")
                    profiles = st.session_state['linkedin_profiles']
                    if profiles:
                        st.write(f"Found {len(profiles)} profiles:")
                        profiles_df = pd.DataFrame(profiles)

                        def create_button(link, label):
                            return f'<a href="{link}" target="_blank"><button>{label}</button></a>'

                        profiles_df['link'] = profiles_df['link'].apply(lambda x: create_button(x, 'Voir Profil LinkedIn'))

                        st.markdown(
                            f'<div class="centered-table">{profiles_df.to_html(escape=False, index=False)}</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.write("No profiles found.")
            else:
                st.write("The job titles for CV search and LinkedIn search do not match.")

if __name__ == "__main__":
    main()
