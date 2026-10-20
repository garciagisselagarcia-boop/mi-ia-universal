import os
import tempfile
import unicodedata
import streamlit as st
from google import genai

st.set_page_config(page_title="Mi IA Universal", page_icon="🤖")

st.title("🤖 Mon Assistant IA Universel")
st.write("Bienvenue ! Téléchargez n'importe quel fichier (PDF, image, audio) ou posez-moi une question.")

# Obtener la API Key
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ La clé API 'GEMINI_API_KEY' n'est pas configurée dans les Secrets de Streamlit.")
    st.stop()

# Inicializar cliente
client = genai.Client(api_key=api_key)

# Selector de modelo corregido con un modelo totalmente estable y actual
modelo_seleccionado = st.selectbox(
    "Choisissez le modèle d'IA :",
    ["gemini-2.5-flash", "gemini-2.0-flash"]
)

# Carga de archivos y textos
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
                    # Limpiar caracteres especiales del archivo (como la Ñ)
                    nom_nettoye = unicodedata.normalize('NFKD', fichier_charge.name).encode('ascii', 'ignore').decode('ascii')
                    if not nom_nettoye:
                        nom_nettoye = "document.pdf"
                        
                    with tempfile.NamedTemporaryFile(delete=False, suffix="_" + nom_nettoye) as tmp:
                        tmp.write(fichier_charge.getvalue())
                        tmp_path = tmp.name
                    
                    archivo_subido = client.files.upload(file=tmp_path)
                    contenido.append(archivo_subido)
                
                if pregunta:
                    contenido.append(pregunta)
                else:
                    contenido.append("Analyse ce fichier en détail s'il te plaît.")

                # Llamada limpia a la API
                response = client.models.generate_content(
                    model=modelo_seleccionado,
                    contents=contenido
                )
                
                st.subheader("Réponse :")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"Une erreur s'est produite : {e}")
                
