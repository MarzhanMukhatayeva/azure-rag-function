# Azure RAG AI Assistant

An AI-powered conversational assistant built with Microsoft Azure, Python, and Streamlit.

This project demonstrates how Retrieval-Augmented Generation (RAG) can be used to answer user questions based on a company's internal knowledge base.

The application combines Azure AI Search for document retrieval, Azure OpenAI for response generation, Azure Functions for backend processing, and Streamlit for an interactive chat interface.

## Project Overview

The AI assistant helps users find information about moving services, pricing, payment policies, and company procedures.

Instead of relying only on the language model's general knowledge, the application retrieves relevant information from indexed documents before generating an answer.

This approach helps improve answer relevance and reduce hallucinations.

## Technologies Used

- Python
- Microsoft Azure
- Azure OpenAI
- Azure AI Search
- Azure Functions
- Streamlit
- REST API
- Git and GitHub

## Key Features

- Conversational AI chat interface
- Retrieval-Augmented Generation (RAG)
- Hybrid document search
- Context-aware answer generation
- Source references for retrieved documents
- Chat history during the Streamlit session
- REST API integration
- Environment-based configuration

## System Architecture

```text
                 USER
                   |
                   v
          Streamlit Chat UI
                   |
                   v
            HTTP Request
                   |
                   v
           Azure Functions
                   |
                   v
            Hybrid Search
                   |
                   v
            Azure AI Search
                   |
                   v
         Relevant Document Chunks
                   |
                   v
              Azure OpenAI
                   |
                   v
           Generated Answer
                   |
                   v
         JSON API Response
                   |
                   v
          Streamlit Chat UI
                   |
                   v
           Answer + Sources
```

## How RAG Works

1. The user submits a question through the Streamlit interface.
2. Streamlit sends the question to the Azure Functions API.
3. The backend searches indexed documents using Azure AI Search.
4. Relevant document chunks are retrieved.
5. The retrieved information is added to the language model's context.
6. Azure OpenAI generates an answer based on the retrieved context.
7. The API returns the answer and source references.
8. Streamlit displays the response to the user.

## Example Question

**User:**

Is there a discount for cash payments?

**AI Assistant:**

Yes, there is a 5% discount off the total bill for cash payments.

The application also displays references to the retrieved knowledge base documents.

## Project Structure

```text
rag-function/
|
|-- function_app.py
|-- streamlit_app.py
|-- requirements.txt
|-- host.json
|-- README.md
|-- .gitignore
```

## API Endpoint

Local endpoint:

```text
http://localhost:7071/api/rag
```

Example POST request:

```json
{
  "question": "Is there a discount for cash payments?"
}
```

Example response (simplified):

```json
{
  "question": "Is there a discount for cash payments?",
  "answer": "Yes, there is a 5% discount off the total bill for cash payments.",
  "status": "success"
}
```

The API also returns retrieved source information.

## Running the Application Locally

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Azure Services

Configure the required Azure OpenAI and Azure AI Search settings using environment variables or local Azure Functions settings.

Never commit API keys or credentials to GitHub.

### 3. Start Azure Functions

```bash
func start
```

The API will be available at:

```text
http://localhost:7071/api/rag
```

### 4. Start Streamlit

Open another terminal:

```bash
python3 -m streamlit run streamlit_app.py
```

Open the local Streamlit URL displayed in the terminal.

## Current Project Status

- Azure OpenAI integration: Implemented
- Azure AI Search integration: Implemented
- Azure Functions API: Implemented
- Streamlit chat interface: Implemented
- Source references: Implemented
- Local end-to-end testing: Completed
- Cloud deployment: Planned

## Future Improvements

- Deploy the backend to Azure
- Host the frontend online
- Add user authentication
- Improve retrieval evaluation
- Add automated testing
- Support additional knowledge bases

## Author

Marzhan Mukhatayeva

AI Engineering Portfolio Project