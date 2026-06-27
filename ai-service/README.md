# AI Service — Scrum Ceremony Platform

## Overview
Local LLM inference service using Ollama with Gemma 3 9B (instruct) for summaries,
action extraction, and sentiment analysis. Uses mxbai-embed-large for embeddings.

## Models
- **Gemma 3 9B** (Q4_K_M, ~6GB): Summarization, action extraction, action quality scoring, sentiment
- **mxbai-embed-large** (334M, ~670MB): Note embeddings for clustering and similarity

## API Endpoints
- POST /generate — Structured generation with JSON schema enforcement
- POST /embed — Generate embeddings for text batches
- POST /cluster — Embed + DBSCAN cluster + label suggestions
- POST /summary — Generate retrospective summary draft
- POST /extract-actions — Extract action items from notes
- POST /sentiment — Analyze sentiment of notes
- POST /action-quality — Score action item quality
- GET /health — Service health + model status

## Configuration
- OLLAMA_BASE_URL — Ollama server URL
- OLLAMA_MODEL — Primary model (default: gemma3:9b)
- EMBEDDING_MODEL — Embedding model (default: mxbai-embed-large)
- OPENROUTER_API_KEY — Fallback cloud LLM key
- FALLBACK_ENABLED — Whether to fall back to cloud LLM on Ollama failure
- MAX_TOKENS — Max generation tokens (default: 2048)
- TEMPERATURE — Generation temperature (default: 0.3 for structured, 0.7 for creative)
