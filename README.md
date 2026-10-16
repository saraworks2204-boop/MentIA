# MentIA — Plataforma de Soporte a la Decisión Clínica en Psiquiatría

Prototipo de tesis de pregrado (Ingeniería Mecatrónica, Institución Universitaria EAM) que
implementa un sistema RAG (Retrieval-Augmented Generation) especializado en psiquiatría
(depresión, ansiedad, esquizofrenia y trastorno del espectro autista), con respuestas
diferenciadas según el perfil del usuario: psiquiatra, estudiante o paciente.

## ¿Cómo funciona?

1. El usuario escribe una consulta clínica en lenguaje natural.
2. El sistema genera palabras clave en inglés y busca literatura relevante en PubMed.
3. Los artículos recuperados se indexan en una base vectorial (ChromaDB).
4. Se genera una respuesta fundamentada en la evidencia recuperada, adaptada al perfil
   seleccionado (psiquiatra / estudiante / paciente).

## Requisitos

- Python 3.11+
- Una cuenta de NCBI (para `NCBI_API_KEY`, opcional pero recomendada)
- Una API key de [Groq](https://console.groq.com/) (para `GROQ_API_KEY`)

## Instalación

```bash
git clone https://github.com/saraworks2204-boop/MentIA.git
cd MentIA
pip install -r requirements.txt
```

Copia `.env.example` a `.env` y completa tus claves reales:

```bash
cp .env.example .env
```

## Ejecución

```bash
streamlit run ui/app.py
```

La aplicación abrirá en `http://localhost:8501`.

## Aviso

Este es un prototipo de investigación académica. No sustituye el criterio médico
profesional ni genera diagnósticos clínicos vinculantes.
