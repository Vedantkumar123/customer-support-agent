import json
import os
from typing import List, Dict, Tuple
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer


class PineconeRetriever:
    
    def __init__(self, dataset_path: str = "policies.json", index_name: str = "policies"):
        self.documents = self._load_documents(dataset_path)
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.index_name = index_name
        
        api_key = os.getenv('PINECONE_API_KEY')
        
        if api_key:
            try:
                self.pc = Pinecone(api_key=api_key)
                self._initialize_index()
            except Exception as e:
                print(f"WARNING: Pinecone initialization failed: {e}")
                self.pc = None
                self.index = None
                print("Using mock embeddings mode.")
        else:
            self.pc = None
            self.index = None
            print("WARNING: PINECONE_API_KEY not set. Using mock embeddings mode.")
    
    def _load_documents(self, dataset_path: str) -> List[Dict]:
        if not os.path.exists(dataset_path):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            dataset_path = os.path.join(script_dir, "policies.json")
        
        with open(dataset_path, 'r', encoding='utf-8') as f:
            documents = json.load(f)
        
        return documents
    
    def _initialize_index(self):
        try:
            list_indexes = self.pc.list_indexes()
            index_names = [idx.name for idx in list_indexes.indexes]
            
            if self.index_name not in index_names:
                dimension = len(self.model.encode("test"))
                self.pc.create_index(
                    name=self.index_name,
                    dimension=dimension,
                    metric='cosine',
                    spec={
                        "serverless": {
                            "cloud": "aws",
                            "region": "us-east-1"
                        }
                    }
                )
            
            self.index = self.pc.Index(self.index_name)
            self._upsert_documents()
        except Exception as e:
            print(f"Error initializing Pinecone index: {e}")
            self.index = None
    
    def _upsert_documents(self):
        vectors = []
        for doc in self.documents:
            full_text = f"{doc['title']} {doc['content']}"
            embedding = self.model.encode(full_text)
            
            vectors.append({
                'id': str(doc['id']),
                'values': embedding.tolist(),
                'metadata': {
                    'id': doc['id'],
                    'title': doc['title'],
                    'content': doc['content']
                }
            })
        
        self.index.upsert(vectors=vectors, batch_size=100)
    
    def retrieve(self, query: str, top_k: int = 3) -> Tuple[List[Dict], List[float]]:
        query_embedding = self.model.encode(query)
        
        if self.index is not None:
            results = self.index.query(
                vector=query_embedding.tolist(),
                top_k=top_k,
                include_metadata=True
            )
            
            retrieved_docs = []
            retrieved_scores = []
            
            for match in results['matches']:
                metadata = match['metadata']
                retrieved_docs.append({
                    'id': metadata['id'],
                    'title': metadata['title'],
                    'content': metadata['content']
                })
                retrieved_scores.append(float(match['score']))
            
            return retrieved_docs, retrieved_scores
        else:
            return self._mock_retrieve(query, top_k)
    
    def _mock_retrieve(self, query: str, top_k: int) -> Tuple[List[Dict], List[float]]:
        query_embedding = self.model.encode(query)
        
        scores = []
        for doc in self.documents:
            full_text = f"{doc['title']} {doc['content']}"
            doc_embedding = self.model.encode(full_text)
            
            similarity = (query_embedding @ doc_embedding) / (
                (query_embedding @ query_embedding) ** 0.5 * 
                (doc_embedding @ doc_embedding) ** 0.5
            )
            scores.append((doc, float(similarity)))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        top_results = scores[:top_k]
        
        retrieved_docs = [doc for doc, _ in top_results]
        retrieved_scores = [score for _, score in top_results]
        
        return retrieved_docs, retrieved_scores
    
    def get_document_context(self, documents: List[Dict]) -> str:
        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(
                f"[Policy {i}] {doc['title']}:\n{doc['content']}"
            )
        
        return "\n\n".join(context_parts)
