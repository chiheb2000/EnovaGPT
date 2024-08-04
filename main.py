import streamlit as st
import pandas as pd
import fitz  
from io import BytesIO
from langchain_community.llms import LlamaCpp, HuggingFaceHub
from fonction.create_database import main as update_database
from fonction.embedding_function import get_embedding_function
from streamlit_option_menu import option_menu
from fonction.generation_post import generate_recruitment_post
from fonction.analyse_cv import query_profiles, upload_and_save_pdf
from fonction.scraping_linkdln import login_and_save_cookies, load_cookies_and_get_driver, get_linkedin_profiles
import os
from database import create_tables, insert_generation_post, insert_analyze_cv, insert_linkedin_profile
import sqlite3
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Obtenir les valeurs des variables d'environnement
MODEL_PATH = os.getenv('MODEL_PATH')
DATA_PATH = os.getenv('DATA_PATH')
HUGGINGFACEHUB_API_TOKEN = os.getenv('HUGGINGFACEHUB_API_TOKEN')
DATABASE_PATH = os.getenv('DATABASE_PATH')

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
    
def load_data_from_db(query):
    conn = sqlite3.connect(DATABASE_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

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

# Main function
def main():
    st.set_page_config(page_title="Enova Robotics Recruitment and CV Analysis", layout="wide")
    logo_path = "logoEnovaRobotics-1.png"

    # Charger le fichier CSS
    with open("style.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    st.image(logo_path, width=200)
    st.markdown('<p class="title">🤖 Plateforme RH - EnovaGPT 🤖</p>', unsafe_allow_html=True)

    llm = initialize_llm()
    llm2 = initialize_llmsmall()
    embedding_function = get_embedding_function()
    create_tables()

    action = option_menu(
        None,
        ["Recruitment Post", "Analyze CVs", "Profile LinkedIn", "Results","Historical"],
        icons=["bi bi-pencil-square", "file-earmark-text", "bi bi-linkedin", "bi bi-check-circle", "bi bi-clock-history"],
        default_index=0,
        orientation="horizontal"
    )

    if action == "Recruitment Post":
        st.markdown('<p class="subheader-center">💻 Generate Recruitment Post 💻</p>', unsafe_allow_html=True)
        buff, col, buff2 = st.columns([2, 3, 2])
        with col:
            job_title = st.text_input("🧑‍💻 Job Title:", value=st.session_state.get('job_title', ''))

            type_contrat = st.selectbox("📑 Contract Type:", ["Permanent", "Temporary", "Internship"], index=["Permanent", "Temporary", "Internship"].index(st.session_state.get('type_contrat', 'Permanent')))
            salaire = None
            duree_stage = None

            if type_contrat == "Internship":
                duree_stage = st.text_input("Internship Duration (e.g., 6 months):",value=st.session_state.get('duree_stage', ''))
            else:
                salaire = st.text_input("💰 Salary Range (e.g., 20,000 to 30,000 Dinars annually):",value=st.session_state.get('salaire', ''))
            buff, col, buff2 = st.columns([1, 1, 1])
            with col:
                submit_button = st.button("Generate... 📝")
                
            if submit_button:
                if job_title and type_contrat and (salaire or duree_stage):
                    st.session_state['job_title'] = job_title  
                    with st.spinner('Generating the recruitment post...'):
                        recruitment_post = generate_recruitment_post(llm2, job_title, type_contrat, salaire, duree_stage)
                        st.session_state['type_contrat'] = type_contrat
                        if type_contrat == "Internship":
                            st.session_state['duree_stage'] = duree_stage
                        else:
                            st.session_state['salaire'] = salaire
                        st.session_state['recruitment_post'] = recruitment_post
                        insert_generation_post(job_title, type_contrat, salaire, duree_stage, recruitment_post)
                    st.success("Recruitment post generated successfully!")
                else:
                    st.error("Please fill in all the required fields!")
            if st.session_state.get("job_title") and st.session_state.get("recruitment_post"):
                st.text_area(f'🧑‍💻 Recruitment Post For: {job_title} 🧑‍💻', st.session_state['recruitment_post'], height=300, key="recruitment_post_area")

    elif action == "Analyze CVs":
        st.markdown('<p class="subheader-center">📑 Analyze CVs 📑</p>', unsafe_allow_html=True)
        buff, col, buff2 = st.columns([2, 3, 2])
        with col:
 
            uploaded_file = st.file_uploader("Upload a PDF resume", type=['pdf'])
            if uploaded_file is not None:
                success, message = upload_and_save_pdf(uploaded_file)
                if success:
                    st.success(message)
                    update_database(reset=False)
                else:
                    st.error(message)
                    
            buff, col, buff2 = st.columns([1, 1, 1])
            with col:
                if st.button("Reset Database 🔄"):
                    with st.spinner('Resetting the database...'):
                        update_database(reset=True)
                    st.success("Database has been reset!")

            if 'job_title' in st.session_state:
                use_generated_title = st.checkbox("Use job title from Recruitment Post", value=False)
                if use_generated_title:
                    poste = st.session_state['job_title']
                else:
                    poste = st.text_input("Enter the job title for the CV search:", value=st.session_state.get('job_titlecv', ''))
            else:
                poste = st.text_input("Enter the job title for the CV search:", value=st.session_state.get('job_titlecv', ''))
        
            st.session_state['job_titlecv'] = poste
            buff, col, buff2 = st.columns([1, 1, 1])
            with col:
                submit_button = st.button("Search CVs... 🔍")

            if submit_button:
                if  poste:
                    with st.spinner('Searching compatible profiles...'):
                        results, response_text = query_profiles(poste, embedding_function, llm2)
                        st.session_state['cv_results'] = results
                        st.session_state['cv_response_text'] = response_text
                        # Insérer les résultats dans la base de données
                        for doc, score in results:
                            pdf_path = os.path.join(DATA_PATH, doc.metadata.get('source'))
                            insert_analyze_cv(poste, score, pdf_path)                        
                        st.success("Search completed!")
                else:
                    st.error("Please fill in all the required fields!")
        
            if st.session_state.get("cv_results") and st.session_state.get("cv_response_text"):
                st.text_area(f'🧑‍💻 Job title for CV search: {poste} 🧑‍💻', st.session_state['cv_response_text'], height=400, key="cv_search_results_area")
                display_search_results(st.session_state['cv_results'])

    elif action == "Profile LinkedIn":
        st.markdown('<p class="subheader-center">🔗 Profile LinkedIn 🔗</p>', unsafe_allow_html=True)
        buff, col, buff2 = st.columns([1, 3, 1])
        with col:
            st.markdown('<p class="subheader-center2">Use this form to search LinkedIn profiles based on job title.</p>', unsafe_allow_html=True)

            if "authenticated" not in st.session_state:
                st.session_state.authenticated = False

            if not st.session_state.authenticated:
                buff, col, buff2 = st.columns([2, 1, 2])
                with col:
                    Connect =st.button("Se connecter🔐")
                if Connect:
                    login_and_save_cookies()
                    st.session_state.authenticated = True
                    st.success("Connecté à LinkedIn avec succès!")

            if st.session_state.authenticated:
                if 'job_title' in st.session_state:
                    use_generated_title = st.checkbox("Use job title from Recruitment Post", value=False)
                    if use_generated_title:
                        job_title_link = st.session_state['job_title']
                    else:
                        job_title_link = st.text_input("Enter the job title for the LinkedIn search profiles:", value=st.session_state.get('job_titlelink', ''))
                else:
                    job_title_link = st.text_input("Enter the job title for the LinkedIn search profiles:", value=st.session_state.get('job_titlelink', ''))
                
                st.session_state['job_titlelink'] = job_title_link
                buff, col, buff2 = st.columns([2, 1, 2])
                with col:
                    Search =st.button("Search... 🔍")
                if Search :
                    if  job_title_link:
                        with st.spinner('Searching compatible profiles...'):
                            driver = load_cookies_and_get_driver()
                            profiles = get_linkedin_profiles(driver, job_title_link)
                            driver.quit()
                            st.session_state['linkedin_profiles'] = profiles
                            for profile in profiles:
                                insert_linkedin_profile(job_title_link, profile['link'], profile['name'])
                    else:
                        st.error("Please fill in all the required fields!")

                if "linkedin_profiles" in st.session_state:
                    profiles = st.session_state['linkedin_profiles']
                    if profiles:
                        st.write(f"Trouvé {len(profiles)} profils:")
                        profiles_df = pd.DataFrame(profiles)

                        def create_button(link, label):
                            return f'<a href="{link}" target="_blank">{label}</a>'

                        profiles_df['link'] = profiles_df['link'].apply(lambda x: create_button(x, 'Link Profil'))

                        st.markdown(
                            f'<div class="centered-table">{profiles_df.to_html(escape=False, index=False)}</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.write("Aucun profil trouvé.")

    elif action == "Results":
        st.markdown('<p class="subheader-center">📊 Results 📊</p>', unsafe_allow_html=True)
        job1 = st.session_state.get('job_titlelink', '').strip()
        job2 = st.session_state.get('job_titlecv', '').strip()
        buff, col, buff2 = st.columns([2, 3, 2])
        with col:
            if (job1 and job2) and (job1 == job2) :
                st.markdown(f'<p class="subheader-center1"> Results for Job Title: {job1}</p>', unsafe_allow_html=True)
                
                if 'cv_results' in st.session_state:
                    st.markdown('<p class="subheader-center2">📑 CV Analysis Results 📑</p>', unsafe_allow_html=True)
                    
                    display_search_results(st.session_state['cv_results'])
                    if 'linkedin_profiles' in st.session_state:
                        st.markdown('<p class="subheader-center2"> 🔗  LinkedIn Profile Results  🔗 </p>', unsafe_allow_html=True)
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
                st.markdown('<p class="subheader-center1">⚠️The job titles for CV search and LinkedIn search do not match.⚠️</p>', unsafe_allow_html=True)
            
    elif action == "Historical":
        st.markdown('<p class="subheader-center">📅 Historical Data 📅</p>', unsafe_allow_html=True)
        buff, col, buff2 = st.columns([1, 1, 1])
        with col:
            selected_date = st.date_input("Select a date to filter records:")
            
            selected_date_str = selected_date.strftime('%Y-%m-%d')
            
            posts_query = f"SELECT * FROM generation_posts WHERE date(timestamp) = '{selected_date_str}'"
            cvs_query = f"SELECT * FROM analyze_cvs WHERE date(timestamp) = '{selected_date_str}'"
            profiles_query = f"SELECT * FROM linkedin_profiles WHERE date(timestamp) = '{selected_date_str}'"
            
            posts_df = load_data_from_db(posts_query)
            cvs_df = load_data_from_db(cvs_query)
            profiles_df = load_data_from_db(profiles_query)
        buff, col, buff2 = st.columns([1, 4, 1])
        with col:            
                st.markdown('<p class="subheader-center2">🧑‍💻 Generated Recruitment Posts 🧑‍💻</p>', unsafe_allow_html=True)
                st.dataframe(posts_df)
                
                st.markdown('<p class="subheader-center2">📑 Analyzed CVs 📑</p>', unsafe_allow_html=True)
                st.dataframe(cvs_df)
                
                st.markdown('<p class="subheader-center2"> 🔗  LinkedIn Profiles  🔗 </p>', unsafe_allow_html=True)
                st.dataframe(profiles_df)
            
if __name__ == "__main__":
    main()
