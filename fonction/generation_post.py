from langchain.prompts import PromptTemplate




def generate_recruitment_post(llm, poste, type_contrat, salaire=None, duree_stage=None):
    # Description de la tâche pour générer la liste de compétences
    competences_template = PromptTemplate(
        input_variables=["poste"],
        template="Votre tâche est de lister les compétences nécessaires pour un {poste} ayant de l'expérience. \n\nListe de compétences requises :"
    )
    # Description de la tâche pour générer la liste des avantages
    avantages_template = PromptTemplate(
        input_variables=["type_contrat", "poste"],
        template="Votre tâche est de lister les avantages offerts pour un {type_contrat} comme {poste}. \n\nAvantages offerts :"
    )

    # Crée les chaînes de génération des compétences et avantages
    competences_chain = competences_template | llm
    avantages_chain = avantages_template | llm


    # Invoque les chaînes pour obtenir les compétences et avantages
    competences = competences_chain.invoke({"poste": poste})
    avantages = avantages_chain.invoke({"type_contrat": type_contrat, "poste": poste})
    
    # Génère le message selon le type de contrat
    if type_contrat == "Internship":
        prompt = (
            f"🚀 Enova Robotics offers an exciting internship opportunity!\n\n"
            f"🔍 Internship Position: {poste}\n"
            f"📝 Contract Type: {type_contrat}\n"
            f"⏳ Duration: {duree_stage}\n"
            f"🛠️ Key Skills: {competences}\n"
            f"🎉 Benefits: {avantages}\n\n"
            f"🔗 Apply here: stages@enovarobotics.com\n"
            f"Don't miss this chance to be part of our innovative and dynamic family! 🌟"
        )
    else:
        prompt = (
            f"🚀 We are looking to expand our team! Join us at Enova Robotics!\n\n"
            f"🔍 Position: {poste}\n"
            f"📝 Contract Type: {type_contrat}\n"
            f"💰 Salary Range: {salaire}\n"
            f"🛠️ Key Skills: {competences}\n"
            f"🎉 Benefits: {avantages}\n\n"
            f"🔗 Apply here: recrutement@enovarobotics.com\n"
            f"Don't miss this opportunity to be part of our innovative and dynamic family! 🌟"
        )
    return prompt

