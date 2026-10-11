import os
from Bio import Entrez
from dotenv import load_dotenv

load_dotenv()

Entrez.email = os.getenv(
    "NCBI_EMAIL",
    "tu_correo@eam.edu.co"
).strip()

Entrez.tool = "MentIA_Thesis_Project"

api_key = os.getenv("NCBI_API_KEY", "").strip()
Entrez.api_key = api_key if len(api_key) > 5 else None


def _ejecutar_busqueda(terminos, max_results):
    """Ejecuta una búsqueda en PubMed y devuelve los PMID."""

    handle = None

    try:
        handle = Entrez.esearch(
            db="pubmed",
            term=terminos,
            retmax=max_results
        )
        record = Entrez.read(handle)
        return record.get("IdList", [])

    except Exception as e:
        print(
            f"[ERROR PUBMED] Consulta: {terminos!r} | "
            f"Tipo: {type(e).__name__} | Detalle: {e}"
        )
        raise

    finally:
        if handle is not None:
            handle.close()


def obtener_articulos_pubmed(
    query: str,
    max_results: int = 10
) -> list:
    """
    Busca artículos en PubMed y devuelve sus metadatos.
    Distingue entre una búsqueda sin resultados y un fallo técnico.
    """

    if not query or not query.strip():
        return []

    # Primera búsqueda
    id_list = _ejecutar_busqueda(query.strip(), max_results)

    # Búsqueda de respaldo si no hay resultados
    if not id_list:
        palabras = query.split()

        if len(palabras) > 2:
            query_alternativa = " ".join(palabras[:2])

            print(
                "[PubMed Fallback] Nueva búsqueda: "
                f"{query_alternativa!r}"
            )

            id_list = _ejecutar_busqueda(
                query_alternativa,
                max_results
            )

    if not id_list:
        print(f"[PUBMED SIN RESULTADOS] Consulta: {query!r}")
        return []

    handle = None

    try:
        handle = Entrez.efetch(
            db="pubmed",
            id=id_list,
            retmode="xml"
        )
        records = Entrez.read(handle)

        articulos = []

        for pubmed_article in records.get("PubmedArticle", []):
            medline = pubmed_article.get("MedlineCitation", {})
            article = medline.get("Article", {})

            pmid = str(medline.get("PMID", ""))
            title = str(article.get("ArticleTitle", "Sin título"))

            abstract_list = (
                article.get("Abstract", {}).get("AbstractText", [])
            )
            abstract = " ".join(str(text) for text in abstract_list)

            pub_date = (
                article.get("Journal", {})
                .get("JournalIssue", {})
                .get("PubDate", {})
            )
            year = str(pub_date.get("Year", "Año desconocido"))

            articulos.append({
                "pmid": pmid,
                "title": title,
                "abstract": abstract or "Sin resumen disponible",
                "year": year,
                "source": f"PubMed PMID: {pmid}",
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            })

        return articulos

    except Exception as e:
        print(
            f"[ERROR AL DESCARGAR ARTÍCULOS] "
            f"Tipo: {type(e).__name__} | Detalle: {e}"
        )
        raise

    finally:
        if handle is not None:
            handle.close()
