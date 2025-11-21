"""
Flask API endpoints for Authority Services
"""
from flask import Blueprint, request, jsonify
import logging

from services.authority.tools import AuthorityTools

logger = logging.getLogger(__name__)

# Create Blueprint
authority_bp = Blueprint('authority', __name__, url_prefix='/api/authority')

# Initialize Authority Tools
authority_tools = AuthorityTools()


@authority_bp.route('/search', methods=['POST'])
def search_authority():
    """
    Search authority terms for a keyword
    
    Request body:
        {
            "keyword": "machine learning",
            "source": "ALL"  # MESH, LCSH, LCC, NLM, or ALL
        }
    """
    try:
        data = request.get_json()
        keyword = data.get('keyword', '')
        source = data.get('source', 'ALL')
        
        if not keyword:
            return jsonify({'error': 'keyword is required'}), 400
            
        result = authority_tools.search_authority_terms(keyword, source)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in search_authority: {e}")
        return jsonify({'error': str(e)}), 500


@authority_bp.route('/map', methods=['POST'])
def map_keywords():
    """
    Map keywords to authority terms and generate MARC fields
    
    Request body:
        {
            "keywords": ["machine learning", "artificial intelligence"],
            "subject_type": "general"  # medical, general, or science
        }
    """
    try:
        data = request.get_json()
        keywords = data.get('keywords', [])
        subject_type = data.get('subject_type', 'general')
        
        if not keywords:
            return jsonify({'error': 'keywords is required'}), 400
            
        if not isinstance(keywords, list):
            return jsonify({'error': 'keywords must be an array'}), 400
            
        result = authority_tools.map_keywords_to_authorities(keywords, subject_type)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in map_keywords: {e}")
        return jsonify({'error': str(e)}), 500


@authority_bp.route('/validate', methods=['POST'])
def validate_term():
    """
    Validate if a term is a valid authority term
    
    Request body:
        {
            "term": "Machine Learning",
            "source": "MESH"  # MESH, LCSH, or LCC
        }
    """
    try:
        data = request.get_json()
        term = data.get('term', '')
        source = data.get('source', '')
        
        if not term or not source:
            return jsonify({'error': 'term and source are required'}), 400
            
        result = authority_tools.validate_authority_term(term, source)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in validate_term: {e}")
        return jsonify({'error': str(e)}), 500


@authority_bp.route('/generate-marc', methods=['POST'])
def generate_marc_fields():
    """
    Generate MARC21 650 fields from authority terms
    
    Request body:
        {
            "authorities": [
                {
                    "term": "Machine Learning",
                    "authority_id": "D015996",
                    "source": "MESH",
                    "category": "medical",
                    "score": 100.0,
                    "metadata": {}
                }
            ]
        }
    """
    try:
        data = request.get_json()
        authorities = data.get('authorities', [])
        
        if not authorities:
            return jsonify({'error': 'authorities is required'}), 400
            
        result = authority_tools.generate_marc21_650_fields(authorities)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in generate_marc_fields: {e}")
        return jsonify({'error': str(e)}), 500


@authority_bp.route('/cache/stats', methods=['GET'])
def get_cache_stats():
    """
    Get cache performance statistics
    
    Query parameters:
        days: Number of days for statistics (default: 7)
    """
    try:
        days = request.args.get('days', 7, type=int)
        result = authority_tools.get_cache_statistics(days)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in get_cache_stats: {e}")
        return jsonify({'error': str(e)}), 500


@authority_bp.route('/classification-keywords', methods=['POST'])
def get_classification_keywords():
    """
    Get classification framework (LCC/NLM) and controlled keywords (MESH/LCSH)
    
    Request body:
        {
            "keywords": ["diabetes", "treatment", "clinical"],
            "subject_type": "medical"  # medical, general, science
        }
    
    Response:
        {
            "success": true,
            "output": {
                "classification_framework": [
                    {
                        "framework": "NLM",
                        "classification_number": "WK 810",
                        "description": "Diabetes Mellitus",
                        "marc_field": "060"
                    }
                ],
                "controlled_keywords": [
                    {
                        "keyword": "Diabetes Mellitus",
                        "vocabulary": "MESH",
                        "term_id": "D003920",
                        "confidence": 95.5,
                        "marc_field": "650"
                    }
                ]
            },
            "marc_fields": {
                "classification": ["060 _4 $a WK 810"],
                "subjects": ["650 _2 $a Diabetes Mellitus"]
            }
        }
    """
    try:
        data = request.get_json()
        keywords = data.get('keywords', [])
        subject_type = data.get('subject_type', 'general')
        
        if not keywords:
            return jsonify({'error': 'keywords is required'}), 400
        
        result = authority_tools.get_classification_and_keywords(keywords, subject_type)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in get_classification_keywords: {e}")
        return jsonify({'error': str(e)}), 500


@authority_bp.route('/tools', methods=['GET'])
def get_tool_definitions():
    """
    Get tool definitions for AI Agent
    
    Returns list of available tools with their schemas
    """
    try:
        tools = authority_tools.get_tool_definitions()
        return jsonify({
            'success': True,
            'tools': tools
        })
        
    except Exception as e:
        logger.error(f"Error in get_tool_definitions: {e}")
        return jsonify({'error': str(e)}), 500


@authority_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'authority-control'
    })
