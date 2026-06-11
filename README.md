# Azure RAG Function API

Azure-based Retrieval Augmented Generation (RAG) API built with:

- Azure Functions
- Azure OpenAI
- Azure AI Search
- Python
- VS Code
- GitHub

## Project Overview

This project receives a user question through an HTTP endpoint, searches indexed documents in Azure AI Search, and generates an answer using Azure OpenAI.

Flow:

User Question
→ Azure Function
→ Azure AI Search
→ Azure OpenAI
→ JSON Response

## API Endpoint

```text
/api/rag?question=YOUR_QUESTION
```

Example:

```text
/api/rag?question=What is the minimum charge
```

Example Response:

```json
{
  "question": "What is the minimum charge",
  "answer": "The minimum charge is 2 hours plus travel time."
}
```

## Local Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run locally:

```bash
func start
```

## Deploy

Deploy to Azure:

```bash
func azure functionapp publish seven-moving-rag-api
```

## Author

Built by Marzhan Mukhatayeva
