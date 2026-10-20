import os
import tempfile
import unicodedata
import streamlit as st
from google import genai

# Configuración de la página orientada a estudio
st.set_page_config(page_title="Mi Asistente de Estudios IA", page_icon="📚", layout="centered")

st.title("📚 Mi Asistente de Estudios IA")
st.write("Sube tus documentos de estudio (PDFs, apuntes, imágenes de esquemas, audios de clases) o hazme preguntas directas.")

# Obtener la clave API de forma segura
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ La clave API 'GEMINI_API_KEY' no está configurada en los Secrets de Streamlit.")
    st.stop()

# Inicializar cliente de Google GenAI
client = genai.Client(api_key=api_key)

# Opciones rápidas para estudiar
modo_estudio = st.selectbox(
    "¿Qué quieres hacer con tu material?",
    [
        "💬 Pregunta libre / Explicación general",
        "📝 Resumir documento clave por clave",
        "❓ Generar preguntas de examen (Quiz) para practicar",
        "🎯 Explicar como si tuviera 5 años (Simplificar conceptos difíciles)"
    ]
)

# Carga de archivos de estudio (PDF, imágenes de pizarrones, audios de explicaciones, etc.)
archivo_estudio = st.file_uploader(
    "Sube tu archivo de estudio (PDF, imagen, audio, texto)", 
    type=["pdf", "png", "jpg", "jpeg", "mp3", "wav", "txt"]
)

pregunta_usuario = st.text_area(
    "Escribe tu duda, pega un texto o indica qué parte del documento quieres trabajar:",
    placeholder="Ejemplo: Explícame los puntos principales de la página 3 o hazme un resumen de este tema..."
)

if st.button("Analizar y Estudiar 🚀"):
    if not pregunta_usuario and not archivo_estudio:
        st.warning("Por favor, sube un archivo o escribe una pregunta para empezar a estudiar.")
    else:
        with st.spinner("🧠 Tu asistente está procesando la información..."):
            try:
                contenido = []
                
                # Procesar archivo si el usuario subió uno
                if archivo_estudio is not None:
                    # Limpiar nombre del archivo para evitar errores de codificación
                    nombre_limpio = unicodedata.normalize('NFKD', archivo_estudio.name).encode('ascii', 'ignore').decode('ascii')
                    if not nombre_limpio:
                        nombre_limpio = "documento_estudio.pdf"
                        
                    with tempfile.NamedTemporaryFile(delete=False, suffix="_" + nombre_limpio) as tmp:
                        tmp.write(archivo_estudio.getvalue())
                        tmp_path = tmp.name
                    
                    archivo_subido = client.files.upload(file=tmp_path)
                    contenido.append(archivo_subido)
                
                # Construir el prompt guiado según el modo de estudio seleccionado
                instruccion_modo = ""
                if "Resumir" in modo_estudio:
                    instruccion_modo = "Por favor, genera un resumen estructurado, claro y con viñetas de los puntos clave de este material de estudio: "
                elif "Quiz" in modo_estudio:
                    instruccion_modo = "A partir de este material, genérame 5 preguntas tipo test o de repaso con sus respectivas respuestas correctas para poner a prueba mis conocimientos: "
                elif "Simplificar" in modo_estudio:
                    instruccion_modo = "Explícame los conceptos complejos de este contenido de forma muy sencilla, con analogías fáciles de entender: "
                else:
                    instruccion_modo = "Analiza detalladamente este material de estudio y responde a la siguiente consulta: "

                prompt_final = instruccion_modo + (pregunta_usuario if pregunta_usuario else "Explícame este documento en detalle para estudiar.")
                contenido.append(prompt_final)

                # Llamada oficial al modelo estable de Google
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=contenido
                )
                
                st.markdown("---")
                st.subheader("📖 Resultado de tu estudio:")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Ocurrió un error al procesar tu solicitud: {e}")
