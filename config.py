"""Configuration for the Biomed chat application."""

import os

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-api-key-here")
GROK_API_KEY = os.getenv("GROK_API_KEY", "your-api-key-here")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "your-api-key-here")
API_PROVIDER = os.getenv(
    "API_PROVIDER", "grok"
)  # "grok", "gemini", "openai", or "anthropic"

# System Prompt
SYSTEM_PROMPT = """You are an expert biomedical engineering assistant with deep knowledge in:
- Molecular biology and genetics
- Medical imaging and signal processing
- Biomaterials and tissue engineering
- Computational biology and bioinformatics
- Medical device design and regulatory affairs
- Clinical research and biostatistics

When provided with Retrieved Context, use it to inform your responses with relevant past information.
Be precise, cite sources when available, and provide actionable insights for biomedical engineering tasks.
If unsure about something, acknowledge limitations and suggest appropriate resources or experts to consult."""

# Tool Definitions (OpenAI function calling format)
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_pubmed",
            "description": "Search PubMed database for biomedical literature",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for PubMed",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_sequence",
            "description": "Analyze DNA, RNA, or protein sequences",
            "parameters": {
                "type": "object",
                "properties": {
                    "sequence": {
                        "type": "string",
                        "description": "Biological sequence to analyze",
                    },
                    "sequence_type": {
                        "type": "string",
                        "enum": ["DNA", "RNA", "protein"],
                        "description": "Type of biological sequence",
                    },
                },
                "required": ["sequence", "sequence_type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_drug_properties",
            "description": "Calculate molecular properties for drug compounds",
            "parameters": {
                "type": "object",
                "properties": {
                    "smiles": {
                        "type": "string",
                        "description": "SMILES notation of the compound",
                    },
                    "properties": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": [
                                "molecular_weight",
                                "logP",
                                "tpsa",
                                "hbd",
                                "hba",
                                "rotatable_bonds",
                            ],
                        },
                        "description": "Properties to calculate",
                    },
                },
                "required": ["smiles"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "simulate_pharmacokinetics",
            "description": "Simulate drug pharmacokinetics (PK) parameters",
            "parameters": {
                "type": "object",
                "properties": {
                    "dose": {"type": "number", "description": "Drug dose in mg"},
                    "half_life": {"type": "number", "description": "Drug half-life in hours"},
                    "volume_distribution": {
                        "type": "number",
                        "description": "Volume of distribution in L/kg",
                    },
                    "time_points": {
                        "type": "integer",
                        "description": "Number of time points to simulate",
                        "default": 24,
                    },
                },
                "required": ["dose", "half_life", "volume_distribution"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_medical_image",
            "description": "Analyze medical images for basic metrics",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_path": {
                        "type": "string",
                        "description": "Path to the medical image file",
                    },
                    "modality": {
                        "type": "string",
                        "enum": ["CT", "MRI", "X-ray", "ultrasound"],
                        "description": "Imaging modality",
                    },
                    "analysis_type": {
                        "type": "string",
                        "enum": [
                            "segmentation",
                            "measurement",
                            "enhancement",
                            "registration",
                        ],
                        "description": "Type of analysis to perform",
                    },
                },
                "required": ["image_path", "modality"],
            },
        },
    },
]

# RAG Configuration
RAG_TOP_K = 3  # Number of similar documents to retrieve
RAG_CHUNK_SIZE = 1000  # Maximum chunk size for text splitting
RAG_MODEL = "all-MiniLM-L6-v2"  # Embedding model for RAG

# Optional: Biomedical-specific embedding model (requires more resources)
# RAG_MODEL = "dmis-lab/biobert-base-cased-v1.2"  # For GPU environments

# File paths
RAG_INDEX_PATH = "rag_index.faiss"
RAG_DOCUMENTS_PATH = "documents.jsonl"

# Session Configuration
MAX_CONVERSATION_LENGTH = 50  # Maximum number of messages to keep in context
SAVE_CONVERSATION = True  # Whether to save conversation history

# UI Configuration
STREAMLIT_THEME = {
    "primaryColor": "#0066CC",
    "backgroundColor": "#FFFFFF",
    "secondaryBackgroundColor": "#F0F2F6",
    "textColor": "#262730",
    "font": "sans serif",
}
