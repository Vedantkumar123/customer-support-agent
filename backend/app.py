from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import sys
from typing import Dict, Any

load_dotenv()

from bm25_retriever import PineconeRetriever
from sarvam_client import SarvamAPIClient
from prompt_engineer import PromptEngineer, SupportMode
from logger import SupportLogger


app = Flask(__name__)
CORS(app)

try:
    retriever = PineconeRetriever("policies.json")
    sarvam_client = SarvamAPIClient()
    support_logger = SupportLogger("logs")
    print("All components initialized successfully")
except Exception as e:
    print(f"Error initializing components: {e}")
    sys.exit(1)


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Customer Support Response Generator',
        'version': '1.0.0'
    })


@app.route('/api/modes', methods=['GET'])
def get_modes():
    modes = PromptEngineer.get_all_modes()
    return jsonify({
        'success': True,
        'modes': modes
    })


@app.route('/api/generate-response', methods=['POST'])
def generate_response():
    
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: query'
            }), 400
        
        query = data.get('query', '').strip()
        mode_str = data.get('mode', 'friendly').lower()
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query cannot be empty'
            }), 400
        
        try:
            mode = SupportMode(mode_str)
        except ValueError:
            return jsonify({
                'success': False,
                'error': f'Invalid mode. Use: strict, friendly, or fallback'
            }), 400
        
        retrieved_docs, similarity_scores = retriever.retrieve(query, top_k=3)
        
        max_score = max(similarity_scores) if similarity_scores else 0
        use_fallback = max_score < 0.5
        
        if use_fallback and mode != SupportMode.FALLBACK:
            print(f"Low similarity score ({max_score:.2f}), switching to fallback mode")
            mode = SupportMode.FALLBACK
        
        config = PromptEngineer.get_config_for_mode(mode)
        temperature = config['temperature']
        max_tokens = config['max_tokens']
        
        if mode == SupportMode.FALLBACK:
            context = ""
            prompt = PromptEngineer.get_prompt(mode, context, query)
        else:
            context = retriever.get_document_context(retrieved_docs)
            prompt = PromptEngineer.get_prompt(mode, context, query)
        
        api_response = sarvam_client.generate_response(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            use_mock=True
        )
        
        response_text = api_response.get('text', '')
        
        support_logger.log_interaction(
            query=query,
            mode=mode.value,
            retrieved_docs=retrieved_docs,
            similarity_scores=similarity_scores,
            prompt_used=prompt,
            response=response_text,
            temperature=temperature,
            max_tokens=max_tokens,
            model=api_response.get('model', 'Unknown')
        )
        
        return jsonify({
            'success': True,
            'response': response_text,
            'mode_used': mode.value,
            'retrieved_documents': [
                {
                    'id': doc['id'],
                    'title': doc['title'],
                    'score': float(similarity_scores[i])
                }
                for i, doc in enumerate(retrieved_docs)
            ],
            'parameters': {
                'temperature': temperature,
                'max_tokens': max_tokens
            },
            'model': api_response.get('model', 'Unknown'),
            'is_mock': api_response.get('mock', False)
        })
    
    except Exception as e:
        support_logger.log_error(str(e), query=data.get('query', ''))
        return jsonify({
            'success': False,
            'error': f'Error generating response: {str(e)}'
        }), 500


@app.route('/api/retrieve-documents', methods=['POST'])
def retrieve_documents():
    
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: query'
            }), 400
        
        query = data.get('query', '').strip()
        top_k = min(int(data.get('top_k', 3)), 5)
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query cannot be empty'
            }), 400
        
        retrieved_docs, similarity_scores = retriever.retrieve(query, top_k=top_k)
        
        return jsonify({
            'success': True,
            'query': query,
            'documents': [
                {
                    'id': doc['id'],
                    'title': doc['title'],
                    'content': doc['content'],
                    'score': float(similarity_scores[i])
                }
                for i, doc in enumerate(retrieved_docs)
            ]
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    
    try:
        stats = support_logger.get_statistics()
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/test-prompt', methods=['POST'])
def test_prompt():
    
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: query'
            }), 400
        
        query = data.get('query', '').strip()
        mode_str = data.get('mode', 'friendly').lower()
        
        try:
            mode = SupportMode(mode_str)
        except ValueError:
            return jsonify({
                'success': False,
                'error': f'Invalid mode. Use: strict, friendly, or fallback'
            }), 400
        
        retrieved_docs, similarity_scores = retriever.retrieve(query, top_k=3)
        
        if mode == SupportMode.FALLBACK:
            context = ""
        else:
            context = retriever.get_document_context(retrieved_docs)
        
        prompt = PromptEngineer.get_prompt(mode, context, query)
        config = PromptEngineer.get_config_for_mode(mode)
        
        return jsonify({
            'success': True,
            'mode': mode.value,
            'prompt': prompt,
            'configuration': {
                'temperature': config['temperature'],
                'max_tokens': config['max_tokens'],
                'description': config['description']
            },
            'retrieved_documents': [
                {
                    'title': doc['title'],
                    'score': float(similarity_scores[i])
                }
                for i, doc in enumerate(retrieved_docs)
            ]
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    print("Starting Customer Support Response Generator Server")
    print("Server running on http://localhost:5000")
    print("API Documentation:")
    print("  - GET  /api/health - Health check")
    print("  - GET  /api/modes - List available modes")
    print("  - POST /api/generate-response - Generate customer support response")
    print("  - POST /api/retrieve-documents - Retrieve documents for query")
    print("  - GET  /api/statistics - View usage statistics")
    print("  - POST /api/test-prompt - Test prompt generation")
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
