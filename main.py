import streamlit as st
import pandas as pd
from langchain_community.llms import LlamaCpp
from langchain_community.llms import HuggingFaceHub
from create_database import main as update_database
from embedding_function import get_embedding_function
from streamlit_option_menu import option_menu
from generation_post import generate_recruitment_post
from analyse_cv import  query_profiles, upload_and_save_pdf
from scraping_linkdln import login_and_save_cookies, load_cookies_and_get_driver, get_linkedin_profiles

MODEL_PATH = "C:/Users/chatt/Desktop/Nouveau dossier/Stage enova/models/mistral-7b-instruct-v0.1.Q5_K_M.gguf"

@st.cache_resource
def initialize_llm():
    return LlamaCpp(
        streaming=False,  
        model_path=MODEL_PATH,
        temperature=0.75,  
        top_p=0.9,  
        verbose=True,  
        n_ctx=4096 , 


    )
HUGGINGFACEHUB_API_TOKEN="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"
def initialize_llmsmall():

    repo_id="facebook/opt-125m"
    llm = HuggingFaceHub(
        huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN,
        repo_id=repo_id,
        model_kwargs={"temperature": 0.7, "max_length": 150}  
    )
    return llm



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
            font-weight: bold;
        }
        .centered-table {
            display: flex;
            justify-content: center;
            margin: auto;
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
        ["Generate Recruitment Post", "Analyze CVs", "Profile LinkedIn"],
        icons=["bi bi-pencil-square", "file-earmark-text", "bi bi-linkedin"],
        default_index=0,
        orientation="horizontal"
    )

    if action == "Generate Recruitment Post":
        st.markdown('<p class="subheader-center">Generate Recruitment Post 💻</p>', unsafe_allow_html=True)
        poste = st.text_input("🧑‍💻 Job Title:")
        type_contrat = st.selectbox("📑 Contract Type:", ["Permanent", "Temporary", "Internship"])
        salaire = None
        duree_stage = None

        if type_contrat == "Internship":
            duree_stage = st.text_input("Internship Duration (e.g., 6 months):")
        else:
            salaire = st.text_input("💰 Salary Range (e.g., 20,000 to 30,000 Dinars annually):")

        submit_button = st.button("Generate Recruitment Post 📝")
        if submit_button and poste and type_contrat and (salaire or duree_stage):
            with st.spinner('Generating the recruitment post...'):
                recruitment_post = generate_recruitment_post(llm, poste, type_contrat, salaire, duree_stage)
            st.success("Recruitment post generated successfully!")
            st.text_area("Recruitment Post", recruitment_post, height=300)

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

        poste = st.text_input("Enter the job title for the CV search:")
        submit_button = st.button("Search CVs 🔍")
        if submit_button and poste:
            with st.spinner('Searching compatible profiles...'):
                results, response_text = query_profiles(poste, embedding_function, llm)
                st.success("Search completed!")
                st.text_area("Search Results", response_text, height=400)

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
            job_title = st.text_input("Titre du poste recherché")
            if st.button("Chercher"):
                if job_title:
                    driver = load_cookies_and_get_driver()
                    profiles = get_linkedin_profiles(driver, job_title)
                    driver.quit()
                    links = [profile['link'] for profile in profiles]
                    print(links)
                    st.session_state.profiles = profiles

            if "profiles" in st.session_state:
                profiles = st.session_state.profiles
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
            else:
                st.write("Veuillez remplir le champ du titre de poste.")

if __name__ == "__main__":
    main()
