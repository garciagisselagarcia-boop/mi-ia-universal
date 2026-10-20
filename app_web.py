import streamlit as st
from google import genai

# Initialisation de l'IA avec votre clé
client = genai.Client()

st.title("🤖 Mon Assistant IA Universel")
st.write("Bienvenue ! Téléchargez n'importe quel fichier (PDF, image, audio) ou posez-moi une question.")

# Zone pour que l'utilisateur puisse glisser-déposer un fichier
fichier_charge = st.file_uploader("Choisissez un fichier", type=["pdf", "png", "jpg", "txt", "mp3", "mp4"])

# Zone de texte pour poser une question
question = st.text_input("Que voulez-vous savoir sur ce fichier ?")

# Bouton pour lancer l'analyse
if st.button("Lancer l'analyse"):
    if fichier_charge is not None:
        with st.spinner("L'IA analyse votre fichier..."):
            # Sauvegarde temporaire du fichier sur le serveur
            with open(fichier_charge.name, "wb") as f:
                f.write(fichier_charge.getbuffer())
            
            # Envoi du fichier à Gemini
            fichier_gemini = client.files.upload(file=fichier_charge.name)
            
            # Génération de la réponse
            prompt = question if question else "Analyse ce fichier en détail et donne-moi les points clés."
            reponse = client.models.generate_content(
                model="gemini-flash-latest",
                contents=[fichier_gemini, prompt]
            )
            
            st.success("Analyse terminée !")
            st.markdown(reponse.text)
    else:
        st.warning("Veuillez d'abord télécharger un fichier.")
