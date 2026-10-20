import os
import tempfile
import unicodedata
import streamlit as st
from google import genai
from openai import OpenAI

st.set_page_config(page_title="Mi IA Universal", page_icon="🤖")

st.title("🤖 Mon Assistant IA Universel")
st.write("Bienvenue ! Téléchargez n'importe quel fichier ou posez-moi une question.")

# Cargar claves de API
gemini_api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
openai_api_key = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")

# Selector de Proveedor y Modelo
proveedor_modelo = st.selectbox(
    "Choisissez le modèle d'IA :",
    [
        "Gemini (gemini-3.8-flash)", 
        "ChatGPT (gpt-4o-mini)", 
        "ChatGPT (gpt-4o)"
    ]
)

fichier_charge = st.file_uploader("Choisissez un fichier", type=["pdf", "png", "jpg", "jpeg", "mp3", "wav", "txt", "mp4"])
pregunta = st.text_input("Que voulez-vous savoir sur ce fichier ou poser comme question ?")

if st.button("Envoyer à l'IA"):
    if not pregunta and not fichier_charge:
        st.warning("Veuillez saisir une question ou télécharger un fichier.")
    else:
        with st.spinner("L'IA réfléchit..."):
            try:
                # --- RAMA DE GEMINI ---
                if "Gemini" in proveedor_modelo:
                    if not gemini_api_key:
                        st.error("⚠️ La clé API 'GEMINI_API_KEY' n'est pas configurée.")
                        st.stop()
                    
                    client_gemini = genai.Client(api_key=gemini_api_key)
                    contenido = []
                    
                    if fichier_charge is not None:
                        nom_nettoye = unicodedata.normalize('NFKD', fichier_charge.name).encode('ascii', 'ignore').decode('ascii')
                        if not nom_nettoye:
                            nom_nettoye = "document.pdf"
                            
                        with tempfile.NamedTemporaryFile(delete=False, suffix="_" + nom_nettoye) as tmp:
                            tmp.write(fichier_charge.getvalue())
                            tmp_path = tmp.name
                        
                        archivo_subido = client_gemini.files.upload(file=tmp_path)
                        contenido.append(archivo_subido)
                    
                    if pregunta:
                        contenido.append(pregunta)
                    else:
                        contenido.append("Analyse ce fichier en détail s'il te plaît.")

                    response = client_gemini.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=contenido
                    )
                    st.subheader("Réponse (Gemini) :")
                    st.write(response.text)

                # --- RAMA DE OPENAI (CHATGPT) ---
                elif "ChatGPT" in proveedor_modelo:
                    if not openai_api_key:
                        st.error("⚠️ La clé API 'OPENAI_API_KEY' n'est pas configurée dans les Secrets.")
                        st.stop()
                    
                    client_openai = OpenAI(api_key=openai_api_key)
                    modelo_openai = "gpt-4o-mini" if "gpt-4o-mini" in proveedor_modelo else "gpt-4o"
                    
                    # Nota: OpenAI requiere texto como prompt principal
                    prompt_texto = pregunta if pregunta else "Analyse ce fichier s'il te plaît."
                    
                    completion = client_openai.chat.completions.create(
                        model=modelo_openai,
                        messages=[{"role": "user", "content": prompt_texto}]
                    )
                    
                    st.subheader(f"Réponse ({modelo_openai}) :")
                    st.write(completion.choices[0].message.content)

            except Exception as e:
                st.error(f"Une erreur s'est produite : {e}")
