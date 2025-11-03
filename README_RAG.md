# RAG-Enhanced Biomedical Chatbot (Python Implementation)

This is the Python implementation of the RAG (Retrieval-Augmented Generation) system that can be integrated with your existing Biomed Chat application.

## 🚀 RAG Components Overview

The RAG system enhances your chatbot with:
- **Semantic Memory**: Stores and retrieves relevant context from conversations
- **Tool Output Indexing**: Automatically indexes results from biomedical tools
- **Context-Aware Responses**: Uses retrieved information for more accurate answers

## 📁 Python RAG Files

```
rag.py                 # Core RAG implementation with FAISS
api_client.py          # Grok-4 API integration with RAG
tools.py               # Biomedical tool implementations
config.py              # Configuration and system prompts
streamlit_app.py       # Standalone Python UI (optional)
requirements.txt       # Python dependencies
```

## 🛠️ Installation

### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure API Keys
Create a `.env` file for Python components:
```env
GROK_API_KEY=your-xai-api-key-here
```

## 🔧 Integration with Your Node.js App

### Option 1: Python Microservice
Run the RAG system as a separate service that your Node.js app can call:

```python
# Create a Flask/FastAPI endpoint in api_service.py
from flask import Flask, request, jsonify
from api_client import process_query

app = Flask(__name__)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    response = process_query(data['query'])
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(port=5000)
```

Then call from your Node.js app:
```javascript
const response = await fetch('http://localhost:5000/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: userMessage })
});
```

### Option 2: Direct Python Execution
Use `child_process` in Node.js to run Python scripts:

```javascript
const { spawn } = require('child_process');

function queryRAG(userInput) {
    return new Promise((resolve, reject) => {
        const python = spawn('python', ['query_rag.py', userInput]);
        let result = '';
        
        python.stdout.on('data', (data) => {
            result += data.toString();
        });
        
        python.on('close', (code) => {
            if (code === 0) resolve(result);
            else reject(new Error(`Process exited with code ${code}`));
        });
    });
}
```

## 🧬 Available Biomedical Tools

The Python implementation includes these specialized tools:

### 1. **PubMed Search**
- Searches biomedical literature
- Returns abstracts and citations
- Automatically indexed in RAG

### 2. **Sequence Analysis**
- DNA/RNA/Protein analysis
- GC content, complementary sequences
- Hydrophobicity calculations

### 3. **Drug Properties**
- SMILES to property conversion
- Lipinski's Rule of Five evaluation
- ADMET predictions

### 4. **Pharmacokinetics Simulation**
- One-compartment model
- Concentration-time curves
- Dosing recommendations

### 5. **Medical Image Analysis**
- Basic metrics extraction
- Modality-specific analysis
- Segmentation support

## 💾 RAG Persistence

The system saves its knowledge base:
- **Vector Index**: `rag_index.faiss`
- **Documents**: `documents.jsonl`

Load existing knowledge on startup:
```python
from rag import load_rag_index
load_rag_index('rag_index.faiss')
```

## 🔄 Workflow Integration

### Adding RAG to Your Existing Chat Flow:

1. **Before API Call**: Retrieve relevant context
```python
context = retrieve_from_rag(user_query)
augmented_query = f"{user_query}\n\nContext: {context}"
```

2. **After Tool Execution**: Store results
```python
tool_result = execute_tool(tool_name, args)
add_to_rag([f"Tool: {tool_name}\nResult: {tool_result}"])
```

3. **Response Generation**: Use augmented prompt
```python
response = grok_api_call(augmented_query)
```

## 📊 Performance Considerations

### Memory Usage:
- Base model: ~500MB
- BioBART model: ~1.5GB
- FAISS index: Grows with data

### Speed:
- Embedding generation: ~100ms per chunk
- Retrieval: <50ms for 10k documents
- Add GPU support for 10x speedup

## 🐛 Troubleshooting

### Common Issues:

**FAISS not installing:**
```bash
# For M1/M2 Macs:
conda install -c conda-forge faiss-cpu

# For Linux/Windows:
pip install faiss-cpu
```

**Sentence-transformers memory error:**
```python
# Use smaller model in config.py:
RAG_MODEL = "all-MiniLM-L6-v2"  # Instead of biobert
```

**API timeout issues:**
```python
# Increase timeout in api_client.py:
client = OpenAI(api_key=key, timeout=60)
```

## 🎯 Next Steps

### To Fully Integrate:

1. **Connect Your Node.js Frontend**: 
   - Use the Python API service approach
   - Or spawn Python processes for each query

2. **Enhance Tool Implementations**:
   - Replace mock tools with real APIs
   - Add PubMed API integration
   - Connect to ChEMBL for drug data

3. **Production Deployment**:
   - Use Redis instead of in-memory storage
   - Implement proper error handling
   - Add request rate limiting

4. **Advanced RAG Features**:
   - Implement hybrid search
   - Add document reranking
   - Use query expansion

## 📝 Testing the RAG System

Run the standalone Streamlit app to test:
```bash
streamlit run streamlit_app.py
```

Or test programmatically:
```python
from api_client import process_query

# Test basic query
response = process_query("What is CRISPR?")
print(response)

# Test with tool calling
response = process_query("Analyze the DNA sequence ATGCGATCG")
print(response)

# Check if context is retrieved
response = process_query("What did we discuss about CRISPR?")
print(response)
```

## 🤝 Contributing

To add new biomedical tools:
1. Define tool in `config.py`
2. Implement in `tools.py`
3. RAG will automatically index outputs

## 📚 Resources

- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [Sentence Transformers](https://www.sbert.net/)
- [xAI API Docs](https://docs.x.ai/)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

This RAG system is designed to enhance your existing Biomed Chat application with persistent memory and context-aware responses.
