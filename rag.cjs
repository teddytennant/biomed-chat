const { pipeline } = require('@xenova/transformers');
const fs = require('fs/promises');

let embedder;
let index = []; // Simple array to store { text, embedding }

async function initializeEmbedder(modelName = 'all-MiniLM-L6-v2') {
  if (!embedder) {
    embedder = await pipeline('feature-extraction', modelName);
  }
}

function cosineSimilarity(vecA, vecB) {
  let dotProduct = 0.0;
  let normA = 0.0;
  let normB = 0.0;
  for (let i = 0; i < vecA.length; i++) {
    dotProduct += vecA[i] * vecB[i];
    normA += vecA[i] * vecA[i];
    normB += vecB[i] * vecB[i];
  }
  return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
}

async function add_to_rag(chunks) {
  await initializeEmbedder();
  for (const chunk of chunks) {
    const embedding = await embedder(chunk, { pooling: 'mean', normalize: true });
    index.push({ text: chunk, embedding: embedding.data });
  }
}

async function retrieve_from_rag(query, top_k = 3) {
  if (index.length === 0) {
    return "";
  }
  await initializeEmbedder();
  const queryEmbedding = await embedder(query, { pooling: 'mean', normalize: true });

  const similarities = index.map(item => ({
    text: item.text,
    similarity: cosineSimilarity(queryEmbedding.data, item.embedding)
  }));

  similarities.sort((a, b) => b.similarity - a.similarity);

  return similarities.slice(0, top_k).map(item => item.text).join('\n\n');
}

async function save_rag_index(filePath = 'rag_index.json') {
  await fs.writeFile(filePath, JSON.stringify(index));
}

async function load_rag_index(filePath = 'rag_index.json') {
  try {
    const data = await fs.readFile(filePath, 'utf-8');
    index = JSON.parse(data);
  } catch (error) {
    if (error.code === 'ENOENT') {
      console.log('No RAG index found, starting with an empty one.');
      index = [];
    } else {
      throw error;
    }
  }
}

module.exports = { add_to_rag, retrieve_from_rag, save_rag_index, load_rag_index };