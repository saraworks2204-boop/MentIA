import os
import re
import uuid
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

# EL MODELO APROBADO POR TU API KEY
MODELO_ACTIVO = "openai/gpt-oss-120b"

def generar_keywords_pubmed(query):
    """Traduce y extrae palabras clave para PubMed con un sistema de respaldo robusto."""
    try:
        llm = ChatGroq(model_name=MODELO_ACTIVO, temperature=0)
        prompt = f"Translate to English and return ONLY 3 medical keywords separated by spaces. NO sentences. Query: {query}"
        respuesta = llm.invoke(prompt)
        
        # Limpieza: deja solo letras y espacios
        texto_limpio = "".join(c for c in respuesta.content if c.isalpha() or c.isspace())
        
        # Filtra palabras comunes y vacías
        palabras = [p for p in texto_limpio.split() if p.lower() not in ["here", "are", "keywords", "the", "is", "and", "for", "to"]]
        
        # Si la lista queda vacía, aplicamos respaldo directo usando la query del usuario
        if not palabras:
            palabras = [p for p in query.split() if p.isalpha()][:3]
            
        resultado = " ".join(palabras[:3])
        
        # Respaldo final de seguridad si todo lo anterior fallara
        return resultado if resultado.strip() else "mental health clinical study"

    except Exception as e:
        print(f"[ERROR GENERANDO KEYWORDS] {e}")
        palabras_emergencia = [p for p in query.split() if p.isalpha()][:3]
        return " ".join(palabras_emergencia) if palabras_emergencia else "mental health"

def procesar_documentos_y_crear_vectorstore(articulos_pubmed):
    """Convierte los artículos en fragmentos y los guarda en ChromaDB con una colección única."""
    if not articulos_pubmed:
        return None
        
    documentos = [
        Document(
            page_content=art["abstract"], 
            metadata={"title": art["title"], "source": art["source"], "year": art["year"]}
        )
        for art in articulos_pubmed
    ]
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documentos)
    
    embeddings_gratuitos = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # CORRECCIÓN: Asignar un identificador único por consulta para evitar compartir memoria
    vectorstore = Chroma.from_documents(
        documents=splits, 
        embedding=embeddings_gratuitos,
        collection_name="c_" + uuid.uuid4().hex
    )
    return vectorstore

def generar_respuesta(query, vectorstore, perfil):
    """Genera la respuesta final respetando el idioma y filtrando consultas fuera de dominio."""
    if not vectorstore:
        return "No se encontró literatura clínica suficiente en PubMed para esta consulta."

    llm = ChatGroq(model_name=MODELO_ACTIVO, temperature=0)

    # Memoria ampliada a 6 fragmentos densos
    retriever = vectorstore.as_retriever(search_kwargs={"k": 6})
    documentos_relevantes = retriever.invoke(query)
    
    contexto = "\n\n".join([f"Fuente: {doc.metadata['source']} | Título: {doc.metadata['title']}\nContenido: {doc.page_content}" for doc in documentos_relevantes])

    # Instrucciones avanzadas con barrera de dominio estricto
    instruccion_base = """
    REGLA DE SEGURIDAD Y FILTRADO: Analiza si la consulta del usuario pertenece estrictamente al ámbito de la salud mental, psiquiatría, psicología o neurociencias. 
    Si la consulta es ajena a la salud mental (por ejemplo, recetas de cocina, deportes, finanzas, mecánica o enfermedades ficticias sin sustento real), DEBES rechazarla amablemente indicando que MentIA es un sistema especializado exclusivamente en salud mental y que no puedes responder a esa temática. NO inventes datos ni intentes forzar la evidencia.
    """

    if perfil == "psiquiatra":
        instrucciones = instruccion_base + """
        Eres MentIA, un sistema de soporte a la decisión clínica de nivel experto. 
        DEBES estructurar tu respuesta utilizando terminología médica avanzada, mecanismos de acción farmacológica (farmacocinética/farmacodinamia) y referenciar criterios exactos del DSM-5-TR o CIE-11. 
        Incluye obligatoriamente al final la sección 'Referencias' utilizando los identificadores PMID provistos en el contexto. No uses lenguaje coloquial.
        """
    elif perfil == "estudiante":
        instrucciones = instruccion_base + """
        Eres MentIA, un tutor clínico en formación. Explica fisiopatología paso a paso, guía el razonamiento diagnóstico y mantén un rigor pedagógico claro. 
        Incluye al final la sección 'Referencias' con las fuentes de PubMed utilizadas.
        """
    else: 
        instrucciones = instruccion_base + """
        Eres MentIA, un asistente empático y educativo para pacientes y usuarios. Usa lenguaje muy accesible, claro y humano. 
        NUNCA des diagnósticos definitivos y recuerda siempre los límites del apoyo clínico. No satures con tecnicismos.
        """

    prompt_template = PromptTemplate(
        input_variables=["instrucciones", "contexto", "query"],
        template="""{instrucciones}
        
        REGLA DE ORO: DEBES RESPONDER EXACTAMENTE EN EL MISMO IDIOMA EN EL QUE ESTÁ ESCRITA LA CONSULTA DEL USUARIO.
        
        Basándote ÚNICAMENTE en la siguiente evidencia médica recuperada:
        {contexto}
        
        Consulta del usuario: {query}
        """
    )

    cadena = prompt_template | llm
    respuesta = cadena.invoke({"instrucciones": instrucciones, "contexto": contexto, "query": query})
    
    return respuesta.content