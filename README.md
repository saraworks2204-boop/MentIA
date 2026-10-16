# MentIA 🧠

MentIA es un prototipo RAG (Retrieval-Augmented Generation) enfocado en la búsqueda, síntesis y recuperación de literatura clínica en PubMed, adaptado con múltiples roles de comunicación (psiquiatra, estudiante y paciente) y validaciones de seguridad para restringir consultas fuera del dominio de la salud mental.

## Arquitectura del Proyecto

- **`pubmed_fetcher.py`**: Búsqueda real en PubMed mediante Biopython/Entrez, con manejo de errores y mecanismos de fallback.
- **`pipeline.py`**: Pipeline RAG completo que genera palabras clave con **Groq**, indexa abstracts en **ChromaDB** (con colecciones aisladas por consulta) y procesa respuestas con prompts diferenciados y filtros de seguridad.
- **`ui/app.py`**: Interfaz interactiva desarrollada en **Streamlit** con selector de roles, historial de conversación y registro de estados de ejecución en vivo.

---

## Requisitos Previos

- Python 3.10 o superior.
- Una cuenta en NCBI (para obtener credenciales de PubMed).
- Una API Key de [Groq](https://console.groq.com/).

---

## Configuración del Entorno

1. Clona el repositorio y entra a la carpeta del proyecto.
2. Crea un archivo `.env` basado en la plantilla `.env.example`:
   ```bash
   cp .env.example .env
