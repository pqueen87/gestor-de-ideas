import streamlit as st
import sqlite3
import os
import openai
from dotenv import load_dotenv

# --- CONFIGURACIÓN INICIAL ---
# Cargar las variables de entorno (nuestra API key)
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- FUNCIONES DE BASE DE DATOS (sin cambios) ---
def conectar_bd():
    """Crea una conexión a la base de datos."""
    return sqlite3.connect("ideas.db")

def crear_tabla_si_no_existe():
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ideas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                texto TEXT NOT NULL
            );
        """)
        conexion.commit()
    finally:
        if conexion:
            conexion.close()

# --- FUNCIÓN DE IA (sin cambios) ---
def potenciar_idea_con_ia(texto_idea):
    """Envía una idea a la IA y devuelve sugerencias."""
    try:
        prompt_para_ia = f"Eres un experto en marketing de contenidos. Dada la siguiente idea, genera 3 titulares llamativos para un artículo de blog y una breve descripción (2-3 líneas) para una publicación en redes sociales. IDEA: '{texto_idea}'"
        respuesta = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente de marketing creativo y útil."},
                {"role": "user", "content": prompt_para_ia}
            ]
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        st.error(f"Error al contactar a la IA: {e}")
        return None

# --- CONSTRUCCIÓN DE LA APLICACIÓN WEB ---

# Título de la aplicación que aparecerá en el navegador
st.title("Gestor de Ideas con IA ✨")

# Asegurarse de que la tabla exista al iniciar la app
crear_tabla_si_no_existe()

# --- SECCIÓN PARA AÑADIR NUEVAS IDEAS ---
st.header("Añade una Nueva Idea")
# st.text_input crea un campo de texto. El segundo argumento es el texto del botón.
idea_texto_input = st.text_input("Escribe tu nueva idea aquí:", key="input_idea")
# st.button crea un botón. El código dentro del 'if' solo se ejecuta si se hace clic.
if st.button("Guardar Idea"):
    if idea_texto_input: # Solo guarda si el texto no está vacío
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO ideas (texto) VALUES (?)", (idea_texto_input,))
            conexion.commit()
            # st.success muestra un mensaje de éxito.
            st.success("¡Idea guardada con éxito!")
        except sqlite3.Error as e:
            # st.error muestra un mensaje de error.
            st.error(f"Error al guardar la idea: {e}")
        finally:
            if conexion:
                conexion.close()
    else:
        # st.warning muestra una advertencia.
        st.warning("Por favor, escribe una idea antes de guardarla.")

# --- SECCIÓN PARA VER Y POTENCIAR IDEAS ---
st.header("Tus Ideas Guardadas")

try:
    conexion = conectar_bd()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, texto FROM ideas ORDER BY id DESC") # Ordenamos para ver las más nuevas primero
    todas_las_ideas = cursor.fetchall()

    if not todas_las_ideas:
        st.info("Todavía no tienes ideas guardadas. ¡Añade una arriba!")
    else:
        # Iteramos sobre cada idea para mostrarla con un botón
        for idea in todas_las_ideas:
            idea_id = idea[0]
            idea_texto = idea[1]
            
            # st.columns crea columnas para organizar elementos uno al lado del otro
            col1, col2 = st.columns([4, 1]) # La primera columna es 4 veces más ancha que la segunda
            
            with col1:
                st.write(f"{idea_id}. {idea_texto}")
            with col2:
                # Usamos el ID de la idea en la 'key' del botón para que cada botón sea único
                if st.button("Potenciar", key=f"potenciar_{idea_id}"):
                    # st.spinner muestra un mensaje de "cargando" mientras se ejecuta el código dentro.
                    with st.spinner("Contactando al genio de la IA..."):
                        respuesta_ia = potenciar_idea_con_ia(idea_texto)
                        if respuesta_ia:
                            # st.info muestra un cuadro de información con la respuesta.
                            st.info(f"Sugerencias para '{idea_texto}':\n\n{respuesta_ia}")
except sqlite3.Error as e:
    st.error(f"No se pudieron cargar las ideas: {e}")
finally:
    if conexion:
        conexion.close()