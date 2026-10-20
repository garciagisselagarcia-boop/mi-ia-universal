import os
import tempfile
import streamlit as st
from google import genai

st.set_page_config(page_title="Mi IA Universal", page_icon="🤖")

st.title("🤖 Mon Assistant IA Universel")
st.write("Bienvenue ! Téléchargez n'importe quel fichier (PDF, image, audio) ou posez-moi une question.")

api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ La clé API 'GEMINI_API_KEY' n'est pas configurée dans les Secrets de Streamlit.")
    st.stop()

client = genai.Client(api_key=api_key)

modelo_seleccionado = st.selectbox(
    "Choisissez le modèle d'IA :",
    ["gemini-3.8-flash", "gemini-1.5-pro"]
)

fichier_charge = st.file_uploader("Choisissez un fichier", type=["pdf", "png", "jpg", "jpeg", "mp3", "wav", "txt", "mp4"])
pregunta = st.text_input("Que voulez-vous savoir sur ce fichier ou poser comme question ?")

if st.button("Envoyer à l'IA"):
    if not pregunta and not fichier_charge:
        st.warning("Veuillez saisir une question ou télécharger un fichier.")
    else:
        with st.spinner("L'IA réfléchit..."):
            try:
                contenido = []
                if fichier_charge is not None:
                    with tempfile.NamedTemporaryFile(delete=False, suffix="_" + fichier_charge.name) as tmp:
                        tmp.write(fichier_charge.getvalue())
                        tmp_path = tmp.name
                    archivo_subido = client.files.upload(file=tmp_path)
                    contenido.append(archivo_subido)
                
                if pregunta:
                    contenido.append(pregunta)
                else:
                    contenido.append("Analyse ce fichier en détail s'il te plaît.")

                response = client.models.generate_content(
                    model=modelo_seleccionado,
                    contents=contenido
                )
                
                st.subheader("Réponse :")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"Une erreur s'est produite : {e}")
