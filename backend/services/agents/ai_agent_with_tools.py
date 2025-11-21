"""
AI Agent với Tools từ Authority Control Service
Sử dụng tools để chuẩn hóa keywords thành controlled vocabulary

Framework: Có thể tích hợp với CrewAI, LangGraph, hoặc LangChain
"""
import logging
from typing import List, Dict, Any, Optional
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from services.authority.tools import AuthorityTools

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KeywordProcessorAgent:
    """
    AI Agent để xử lý keywords với Authority Control tools
    
    Agent này có thể:
    1. Nhận raw keywords từ OCR/user input
    2. Sử dụng tools để search, validate, map keywords
    3. Trả về classification frameworks và controlled keywords
    4. Generate MARC21 fields
    
    Có thể tích hợp với:
    - CrewAI: Define agent với tools
    - LangGraph: Node trong graph với tool calling
    - LangChain: Agent với custom tools
    """
    
    def __init__(self):
        """Initialize agent with tools"""
        self.tools = AuthorityTools()
        self.tool_definitions = self.tools.get_tool_definitions()
        logger.info(f"Agent initialized with {len(self.tool_definitions)} tools")
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Get tool definitions for AI framework
        Format tương thích với CrewAI, LangChain
        """
        return self.tool_definitions
    
    def process_keywords(
        self, 
        keywords: List[str], 
        subject_type: str = 'general'
    ) -> Dict[str, Any]:
        """
        Main workflow: Process keywords end-to-end
        
        Steps:
        1. Validate input
        2. Search authorities for each keyword
        3. Map to controlled vocabulary
        4. Get classification frameworks
        5. Generate MARC fields
        
        Args:
            keywords: Raw keywords from OCR or user
            subject_type: 'medical', 'general', 'science'
            
        Returns:
            Complete result with frameworks, keywords, MARC fields
        """
        logger.info(f"Processing {len(keywords)} keywords (type: {subject_type})")
        
        # Step 1: Get classification and keywords using Tool #6
        result = self.tools.get_classification_and_keywords(
            keywords=keywords,
            subject_type=subject_type
        )
        
        if not result['success']:
            logger.error(f"Failed to process keywords: {result.get('error')}")
            return result
        
        # Extract outputs
        classification_frameworks = result['output']['classification_framework']
        controlled_keywords = result['output']['controlled_keywords']
        
        logger.info(f"Found {len(classification_frameworks)} classifications")
        logger.info(f"Found {len(controlled_keywords)} controlled keywords")
        
        return result
    
    def search_single_keyword(
        self, 
        keyword: str, 
        source: str = 'ALL'
    ) -> Dict[str, Any]:
        """
        Search authority terms for a single keyword
        Uses Tool #1: search_authority_terms
        
        Args:
            keyword: Single keyword to search
            source: 'MESH', 'LCSH', 'LCC', 'NLM', or 'ALL'
        """
        tool = next(
            (t for t in self.tool_definitions if t['name'] == 'search_authority_terms'),
            None
        )
        
        if not tool:
            return {'success': False, 'error': 'Tool not found'}
        
        return tool['function'](keyword, source)
    
    def validate_term(
        self, 
        term: str, 
        source: str
    ) -> Dict[str, Any]:
        """
        Validate if a term is a valid authority term
        Uses Tool #3: validate_authority_term
        
        Args:
            term: Term to validate
            source: 'MESH', 'LCSH', or 'LCC'
        """
        tool = next(
            (t for t in self.tool_definitions if t['name'] == 'validate_authority_term'),
            None
        )
        
        if not tool:
            return {'success': False, 'error': 'Tool not found'}
        
        return tool['function'](term, source)
    
    def generate_marc_fields(
        self, 
        authorities: List[Dict]
    ) -> Dict[str, Any]:
        """
        Generate MARC21 650 fields from authorities
        Uses Tool #4: generate_marc21_650_fields
        
        Args:
            authorities: List of authority term dictionaries
        """
        tool = next(
            (t for t in self.tool_definitions if t['name'] == 'generate_marc21_650_fields'),
            None
        )
        
        if not tool:
            return {'success': False, 'error': 'Tool not found'}
        
        return tool['function'](authorities)
    
    def get_tool_for_llm(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get tool definition for LLM framework
        
        Format for CrewAI/LangChain:
        {
            'name': str,
            'description': str,
            'parameters': dict,
            'function': callable
        }
        """
        return next(
            (t for t in self.tool_definitions if t['name'] == tool_name),
            None
        )


# =============================================================================
# Integration Examples
# =============================================================================

def example_crewai_integration():
    """
    Example: Tích hợp với CrewAI framework
    
    CrewAI cho phép define agents với tools và tasks
    """
    print("="*80)
    print("EXAMPLE: CrewAI Integration")
    print("="*80)
    
    # Pseudo-code for CrewAI (requires: pip install crewai)
    """
    from crewai import Agent, Task, Crew
    
    # Create agent with tools
    keyword_agent = KeywordProcessorAgent()
    
    # Define CrewAI agent
    crew_agent = Agent(
        role='Keyword Processor',
        goal='Chuẩn hóa keywords thành controlled vocabulary',
        backstory='Expert in library science and metadata standards',
        tools=keyword_agent.get_available_tools(),
        verbose=True
    )
    
    # Define task
    task = Task(
        description='Process keywords: diabetes, insulin, clinical medicine',
        agent=crew_agent
    )
    
    # Create crew and run
    crew = Crew(agents=[crew_agent], tasks=[task])
    result = crew.kickoff()
    """
    
    print("CrewAI integration requires: pip install crewai")
    print("See code comments for example")


def example_langgraph_integration():
    """
    Example: Tích hợp với LangGraph framework
    
    LangGraph cho phép build stateful multi-agent workflows
    """
    print("\n" + "="*80)
    print("EXAMPLE: LangGraph Integration")
    print("="*80)
    
    # Pseudo-code for LangGraph (requires: pip install langgraph)
    """
    from langgraph.graph import Graph
    from langchain.chat_models import ChatGoogleGenerativeAI
    
    # Create agent
    keyword_agent = KeywordProcessorAgent()
    
    # Define node function
    def process_keywords_node(state):
        keywords = state['keywords']
        result = keyword_agent.process_keywords(keywords)
        return {'processed': result}
    
    # Build graph
    graph = Graph()
    graph.add_node('process_keywords', process_keywords_node)
    graph.set_entry_point('process_keywords')
    
    # Run
    result = graph.invoke({'keywords': ['diabetes', 'insulin']})
    """
    
    print("LangGraph integration requires: pip install langgraph")
    print("See code comments for example")


def example_standalone_usage():
    """
    Example: Sử dụng standalone (không cần framework)
    """
    print("\n" + "="*80)
    print("EXAMPLE: Standalone Usage (No Framework Required)")
    print("="*80)
    
    # Create agent
    agent = KeywordProcessorAgent()
    
    # Test keywords
    keywords = ['diabetes', 'insulin', 'clinical medicine']
    
    print(f"\nInput keywords: {keywords}")
    print("\nProcessing...")
    
    # Process keywords
    result = agent.process_keywords(
        keywords=keywords,
        subject_type='medical'
    )
    
    if result['success']:
        print("\n--- CLASSIFICATION FRAMEWORKS ---")
        for cls in result['output']['classification_framework']:
            print(f"  {cls['framework']}: {cls['classification_number']}")
        
        print("\n--- CONTROLLED KEYWORDS ---")
        for kw in result['output']['controlled_keywords']:
            print(f"  {kw['vocabulary']}: {kw['keyword']}")
        
        print("\n--- MARC FIELDS ---")
        print("Classification (050/060):")
        for field in result['marc_fields']['classification']:
            print(f"  {field}")
        
        print("\nSubjects (650):")
        for field in result['marc_fields']['subjects'][:3]:
            print(f"  {field}")
        
        print("\n--- SUMMARY ---")
        summary = result['summary']
        print(f"Total keywords: {summary['total_keywords']}")
        print(f"Classifications: {summary['classifications_found']}")
        print(f"Controlled terms: {summary['controlled_terms_found']}")


def example_tool_calling():
    """
    Example: Gọi individual tools (như LLM tool calling)
    """
    print("\n" + "="*80)
    print("EXAMPLE: Individual Tool Calling")
    print("="*80)
    
    agent = KeywordProcessorAgent()
    
    # Tool 1: Search
    print("\n1. Search authority terms")
    result = agent.search_single_keyword('diabetes', 'MESH')
    print(f"Found {result['count']} results")
    
    # Tool 3: Validate
    print("\n2. Validate authority term")
    result = agent.validate_term('Diabetes Mellitus', 'MESH')
    print(f"Valid: {result['is_valid']}")
    
    # Tool 6: Get classification + keywords
    print("\n3. Get classification frameworks and keywords")
    result = agent.process_keywords(['diabetes'])
    print(f"Classifications: {len(result['output']['classification_framework'])}")
    print(f"Keywords: {len(result['output']['controlled_keywords'])}")


# =============================================================================
# Main Demo
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("AI AGENT WITH AUTHORITY CONTROL TOOLS")
    print("="*80)
    
    print("\nAgent co the su dung 6 tools:")
    print("  1. search_authority_terms - Tim kiem authority")
    print("  2. map_keywords_to_authorities - Map batch keywords")
    print("  3. validate_authority_term - Validate term")
    print("  4. generate_marc21_650_fields - Generate MARC")
    print("  5. get_cache_statistics - Cache stats")
    print("  6. get_classification_and_keywords - Phan tach frameworks + keywords")
    
    print("\nFramework recommendations:")
    print("  - CrewAI - Multi-agent collaboration, easy setup")
    print("  - LangGraph - Stateful workflows, complex logic")
    print("  - LangChain - General purpose, many integrations")
    print("  - Standalone - No framework needed, direct usage")
    
    print("\nIntegration voi Gemini:")
    print("  - Tat ca frameworks ho tro Gemini (via LangChain)")
    print("  - pip install langchain-google-genai")
    print("  - Hoac dung Google AI SDK truc tiep voi function calling")
    
    # Run examples
    example_standalone_usage()
    example_tool_calling()
    example_crewai_integration()
    example_langgraph_integration()
    
    print("\n" + "="*80)
    print("✅ Agent ready to use with any framework!")
    print("="*80)
