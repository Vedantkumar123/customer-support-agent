import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Any


class SupportLogger:
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        
        os.makedirs(log_dir, exist_ok=True)
        
        self.logger = logging.getLogger('customer_support')
        self.logger.setLevel(logging.INFO)
        
        log_file = os.path.join(log_dir, 'support_interactions.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def log_interaction(
        self,
        query: str,
        mode: str,
        retrieved_docs: List[Dict],
        similarity_scores: List[float],
        prompt_used: str,
        response: str,
        temperature: float,
        max_tokens: int,
        model: str
    ) -> None:
        
        interaction_data = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'mode': mode,
            'retrieved_documents': [
                {
                    'id': doc['id'],
                    'title': doc['title'],
                    'score': float(similarity_scores[i]) if i < len(similarity_scores) else 0.0
                }
                for i, doc in enumerate(retrieved_docs)
            ],
            'llm_parameters': {
                'temperature': temperature,
                'max_tokens': max_tokens,
                'model': model
            },
            'response_length': len(response),
            'prompt_length': len(prompt_used)
        }
        
        self._log_to_json(interaction_data)
        
        self.logger.info(
            f"Query: {query[:100]}... | Mode: {mode} | "
            f"Docs: {len(retrieved_docs)} | Temp: {temperature}"
        )
    
    def _log_to_json(self, interaction_data: Dict[str, Any]) -> None:
        json_log_file = os.path.join(self.log_dir, 'interactions.jsonl')
        
        try:
            with open(json_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(interaction_data, ensure_ascii=False) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to write JSON log: {str(e)}")
    
    def log_error(self, error_message: str, query: str = "", mode: str = "") -> None:
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'error': error_message,
            'query': query,
            'mode': mode
        }
        
        self._log_to_json(error_data)
        self.logger.error(f"Error - Query: {query[:100] if query else 'N/A'} | {error_message}")
    
    def get_statistics(self) -> Dict[str, Any]:
        json_log_file = os.path.join(self.log_dir, 'interactions.jsonl')
        
        if not os.path.exists(json_log_file):
            return {'total_interactions': 0}
        
        stats = {
            'total_interactions': 0,
            'by_mode': {},
            'avg_response_length': 0,
            'total_response_length': 0
        }
        
        try:
            with open(json_log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        if 'error' not in data:
                            stats['total_interactions'] += 1
                            mode = data.get('mode', 'unknown')
                            stats['by_mode'][mode] = stats['by_mode'].get(mode, 0) + 1
                            stats['total_response_length'] += data.get('response_length', 0)
                    except json.JSONDecodeError:
                        continue
            
            if stats['total_interactions'] > 0:
                stats['avg_response_length'] = (
                    stats['total_response_length'] / stats['total_interactions']
                )
        except Exception as e:
            self.logger.error(f"Failed to calculate statistics: {str(e)}")
        
        return stats
