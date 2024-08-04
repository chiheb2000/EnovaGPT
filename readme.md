## Note
Le code est complet dans la branche `test`.

# Développement d'un Large Language Model (LLM)
![LLM](https://github.com/user-attachments/assets/b675ad40-9ccc-4b87-8630-4e2f337cea75)


Ce projet vise à développer un modèle de langage large (LLM) capable de générer des annonces de recrutement et d'analyser des CVs. De plus, il inclut une fonctionnalité de scraping pour rechercher des profils compatibles sur LinkedIn en utilisant beautifulsoup.

## Fonctionnalités

- Génération de postes de recrutement en utilisant le modèle Mistral-7B-Instruct v0.1 GGUF et intégration de techniques de Prompt Engineering

![Prompt Engineering](https://github.com/user-attachments/assets/faf8be23-d9f1-4629-9f11-8b0531a2b08b)
> ***Interface :*** 
![exp](https://github.com/user-attachments/assets/06ede6ae-49c5-4c11-9824-928ed8d28fd3)
![exp1](https://github.com/user-attachments/assets/4d494459-8d27-4882-803a-cddd5c9ff337)

- Analyse de CVs pour extraire des informations pertinentes en intégration de techniques de Retrieval-Augmented Generation (RAG)
![RAG](https://github.com/user-attachments/assets/5e4bfc84-9b94-42cf-bdf8-66b27a7347ab)
> ***Interface :*** 
![image (2)](https://github.com/user-attachments/assets/fd821588-148e-4856-9a29-213a3bb7d0d2)
![image (4)](https://github.com/user-attachments/assets/60771950-939e-47b7-97a8-c26dfd58f226)
- Recherche de profils LinkedIn compatibles avec les postes via scraping
> ***Interface :*** 
![image (5)](https://github.com/user-attachments/assets/0694b872-4cd9-4226-98ca-772a7a4fc21a)
![image (6)](https://github.com/user-attachments/assets/5a85a318-1296-4e2b-a6cd-13979679acd2)

## Video Démo

https://github.com/user-attachments/assets/c81b2c3e-bc6d-4815-bbb0-65e1ccf37ffd

## Installation

Installez les dépendances à partir du fichier requirement.txt 

 
    pip install -r requirement.txt
   

## Modèle Utilisé

Le modèle utilisé dans ce projet est le [Mistral-7B-Instruct v0.1 GGUF](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/blob/main/mistral-7b-instruct-v0.1.Q5_K_M.gguf).

## Contact
Pour toute question, veuillez contacter  à [chattichiheb35@gmail.com].




