# ============================================================
# RAG Azure Function — HTTP trigger
# Принимает вопрос → возвращает ответ из Seven Moving документов
# ============================================================

import azure.functions as func
import json
import os
import logging

from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential

# Инициализируем приложение
# auth_level=ANONYMOUS — запросы без ключа (для разработки)
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# ============================================================
# Инициализируем клиентов один раз при старте функции
# Не внутри handler — иначе новое подключение на каждый запрос
# ============================================================

openai_client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_KEY"],
    api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"]
)

search_client = SearchClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    index_name="moving-docs",
    credential=AzureKeyCredential(os.environ["AZURE_SEARCH_KEY"])
)

# ============================================================
# Вспомогательные функции — те же что в предыдущих днях
# ============================================================

def get_embedding(text: str) -> list[float]:
    response = openai_client.embeddings.create(
        input=text,
        model=os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"]
    )
    return response.data[0].embedding


def hybrid_search(query: str, top_k: int = 3) -> list[dict]:
    embedding = get_embedding(query)
    vector_query = VectorizedQuery(
        vector=embedding,
        k_nearest_neighbors=top_k,
        fields="embedding"
    )
    results = search_client.search(
        search_text=query,
        vector_queries=[vector_query],
        select=["id", "content"],
        top=top_k
    )
    return [{"id": r["id"], "content": r["content"]} for r in results]


def generate_answer(question: str, context: str) -> str:
    response = openai_client.chat.completions.create(
        model=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"],
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant for Seven Moving company. "
                    "Answer ONLY based on the context below. "
                    "If not in context say: "
                    "'I don't have information about this in our documents.'\n\n"
                    f"Context:\n{context}"
                )
            },
            {"role": "user", "content": question}
        ],
        temperature=0,
        max_tokens=500
    )
    return response.choices[0].message.content


# ============================================================
# ГЛАВНЫЙ HANDLER — вызывается на каждый HTTP запрос
# ============================================================

@app.route(route="rag")
def rag_query(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP trigger функция.
    Принимает GET или POST запрос с параметром 'question'.
    Возвращает JSON с ответом.

    Пример GET запроса:
    GET /api/rag?question=Is there a discount for cash?

    Пример POST запроса:
    POST /api/rag
    Body: {"question": "Is there a discount for cash?"}
    """

    logging.info("RAG function triggered")

    # ----------------------------------------------------------
    # Шаг 1: Получаем вопрос из запроса
    # Поддерживаем оба варианта: GET параметр и POST body
    # ----------------------------------------------------------

    # Пробуем GET параметр
    question = req.params.get("question")

    # Если нет в GET — пробуем POST body
    if not question:
        try:
            req_body = req.get_json()
            question = req_body.get("question")
        except ValueError:
            pass

    # Если вопроса нет вообще — возвращаем ошибку
    if not question:
        return func.HttpResponse(
            json.dumps({
                "error": "Please provide a question parameter",
                "example_get": "/api/rag?question=Is there a discount for cash?",
                "example_post": '{"question": "Is there a discount for cash?"}'
            }),
            status_code=400,
            mimetype="application/json"
        )

    # ----------------------------------------------------------
    # Шаг 2: Выполняем RAG pipeline
    # ----------------------------------------------------------

    try:
        # Поиск релевантных чанков
        chunks = hybrid_search(question, top_k=3)
        context = "\n\n".join([c["content"] for c in chunks])
        chunk_ids = [c["id"] for c in chunks]

        # Генерация ответа
        answer = generate_answer(question, context)

        logging.info(f"Question: {question}")
        logging.info(f"Chunks used: {chunk_ids}")
        logging.info(f"Answer: {answer[:100]}...")

        # ----------------------------------------------------------
        # Шаг 3: Возвращаем JSON ответ
        # ----------------------------------------------------------

        response_body = {
            "question": question,
            "answer": answer,
            "chunks_used": chunk_ids,
            "status": "success"
        }

        return func.HttpResponse(
            json.dumps(response_body),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        # Если что-то пошло не так — возвращаем ошибку
        logging.error(f"Error processing request: {str(e)}")

        return func.HttpResponse(
            json.dumps({
                "error": str(e),
                "status": "error"
            }),
            status_code=500,
            mimetype="application/json"
        )