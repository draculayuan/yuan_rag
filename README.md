# RAG Application on Google Cloud

This is a Retrieval-Augmented Generation (RAG) application built on Google Cloud Platform, consisting of two main subsystems:

## Architecture Overview

### Data Ingestion Subsystem
- Ingests documents from external sources into Cloud Storage
- Processes documents into chunks
- Generates embeddings using Vertex AI
- Builds and maintains Vector Search index

### Serving Subsystem
- Provides REST API endpoints for user queries
- Processes queries through RAG pipeline
- Generates responses using Vertex AI LLM
- Implements safety filters and monitoring

## Setup Instructions

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up Google Cloud credentials:
- Create a service account with necessary permissions
- Download the service account key JSON file
- Set the environment variable:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
```

3. Configure the application:
- Copy `.env.example` to `.env`
- Update the configuration values

4. Run the application:

For data ingestion:
```bash
python -m data_ingestion.main
```

For serving:
```bash
python -m serving.main
```

## Project Structure

```
rag-app/
├── data_ingestion/     # Data ingestion subsystem
├── serving/            # Serving subsystem
├── utils/             # Shared utilities
├── config/            # Configuration files
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## Configuration

The application requires the following environment variables:
- `PROJECT_ID`: Google Cloud Project ID
- `REGION`: Google Cloud Region
- `BUCKET_NAME`: Cloud Storage bucket for document storage
- `PUBSUB_TOPIC`: Pub/Sub topic for notifications
- `VERTEX_MODEL`: Vertex AI model name
- More details in `.env.example`

## License

MIT License 