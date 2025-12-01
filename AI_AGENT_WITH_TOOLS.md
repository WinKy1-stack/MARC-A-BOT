# AI Agent với Authority Control Tools

## 📋 Tổng quan

Agent này sử dụng 6 tools từ Authority Control Service để chuẩn hóa keywords thành controlled vocabulary và classification frameworks.

**File:** `backend/services/agents/ai_agent_with_tools.py`

## 🛠️ Tools Available (6 tools)

1. **search_authority_terms** - Tìm kiếm authority terms cho keyword
2. **map_keywords_to_authorities** - Map batch keywords + generate MARC
3. **validate_authority_term** - Validate term có phải authority hợp lệ
4. **generate_marc21_650_fields** - Generate MARC21 650 fields
5. **get_cache_statistics** - Cache performance statistics
6. **get_classification_and_keywords** ⭐ - Phân tách classification frameworks và controlled keywords

## 🚀 Sử dụng

### Standalone (Không cần framework)

```python
from backend.services.agents.ai_agent_with_tools import KeywordProcessorAgent

# Create agent
agent = KeywordProcessorAgent()

# Process keywords
result = agent.process_keywords(
    keywords=['diabetes', 'insulin'],
    subject_type='medical'
)

# Access results
frameworks = result['output']['classification_framework']  # LCC/NLM
keywords = result['output']['controlled_keywords']         # MESH/LCSH
```

### Individual Tool Calling

```python
# Tool 1: Search single keyword
result = agent.search_single_keyword('diabetes', 'MESH')

# Tool 3: Validate term
result = agent.validate_term('Diabetes Mellitus', 'MESH')

# Tool 6: Get classification + keywords
result = agent.process_keywords(['diabetes', 'insulin'])
```

## 🤖 Framework Integration

### Recommended Frameworks

#### 1. **CrewAI** (Easiest)
- **Tốt cho:** Multi-agent collaboration, easy setup
- **Install:** `pip install crewai`
- **Use case:** Multiple agents work together với roles & tasks

```python
from crewai import Agent, Task, Crew
from backend.services.agents.ai_agent_with_tools import KeywordProcessorAgent

# Create agent with tools
keyword_agent = KeywordProcessorAgent()

# Define CrewAI agent
agent = Agent(
    role='Keyword Processor',
    goal='Chuẩn hóa keywords thành controlled vocabulary',
    backstory='Expert in library science',
    tools=keyword_agent.get_available_tools(),
    verbose=True
)

# Define task
task = Task(
    description='Process keywords: diabetes, insulin',
    agent=agent
)

# Run
crew = Crew(agents=[agent], tasks=[task])
result = crew.kickoff()
```

#### 2. **LangGraph** (Most Flexible)
- **Tốt cho:** Stateful workflows, complex logic, conditional paths
- **Install:** `pip install langgraph`
- **Use case:** Multi-step workflows với state management

```python
from langgraph.graph import Graph
from backend.services.agents.ai_agent_with_tools import KeywordProcessorAgent

agent = KeywordProcessorAgent()

# Define node
def process_node(state):
    keywords = state['keywords']
    result = agent.process_keywords(keywords)
    return {'processed': result}

# Build graph
graph = Graph()
graph.add_node('process', process_node)
graph.set_entry_point('process')

# Run
result = graph.invoke({'keywords': ['diabetes']})
```

#### 3. **LangChain** (Most Popular)
- **Tốt cho:** General purpose, many integrations
- **Install:** `pip install langchain`
- **Use case:** Standard agent với tools

```python
from langchain.agents import AgentExecutor
from langchain.chat_models import ChatGoogleGenerativeAI
from backend.services.agents.ai_agent_with_tools import KeywordProcessorAgent

agent = KeywordProcessorAgent()
llm = ChatGoogleGenerativeAI(model="gemini-pro")

# Get tools in LangChain format
tools = agent.get_available_tools()

# Create agent executor
executor = AgentExecutor(agent=llm, tools=tools)

# Run
result = executor.run("Process keywords: diabetes, insulin")
```

## 🔧 Integration với Gemini

### Option 1: Via LangChain (Recommended)

```bash
pip install langchain-google-genai
```

```python
from langchain_google_genai import ChatGoogleGenerativeAI
from backend.services.agents.ai_agent_with_tools import KeywordProcessorAgent

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    google_api_key="YOUR_API_KEY"
)

agent = KeywordProcessorAgent()
# Use with any framework above
```

### Option 2: Direct Google AI SDK

```bash
pip install google-generativeai
```

```python
import google.generativeai as genai
from backend.services.agents.ai_agent_with_tools import KeywordProcessorAgent

genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-1.5-pro')

agent = KeywordProcessorAgent()

# Use function calling
tools = agent.get_available_tools()
response = model.generate_content(
    "Process keywords: diabetes",
    tools=tools
)
```

## 📊 Output Structure

```python
{
  'success': True,
  'output': {
    # CLASSIFICATION FRAMEWORKS
    'classification_framework': [
      {
        'framework': 'LCC' | 'NLM',
        'classification_number': 'R729',
        'description': 'Clinical medicine',
        'marc_field': '050' | '060'
      }
    ],
    
    # CONTROLLED KEYWORDS
    'controlled_keywords': [
      {
        'keyword': 'Diabetes Mellitus',
        'vocabulary': 'MESH' | 'LCSH',
        'term_id': 'D003920',
        'confidence': 0.95,
        'marc_field': '650'
      }
    ]
  },
  
  # MARC FIELDS
  'marc_fields': {
    'classification': ['050 _4 $a R729'],  # LCC/NLM
    'subjects': ['650 _0 $a Diabetes']     # MESH/LCSH
  },
  
  # SUMMARY
  'summary': {
    'total_keywords': 2,
    'classifications_found': 1,
    'controlled_terms_found': 2,
    'uncontrolled_terms': 0
  }
}
```

## 🧪 Testing

```bash
# Test agent
python backend/services/agents/ai_agent_with_tools.py

# Output shows:
# - Standalone usage example
# - Individual tool calling
# - Framework integration examples
```

## 💡 Use Cases

### 1. Cataloging Workflow
```python
agent = KeywordProcessorAgent()

# Step 1: Extract keywords from OCR
keywords = extract_from_ocr(image)

# Step 2: Process với agent
result = agent.process_keywords(keywords, 'medical')

# Step 3: Use in MARC record
marc_record['650'] = result['marc_fields']['subjects']
marc_record['050'] = result['marc_fields']['classification']
```

### 2. Batch Processing
```python
agent = KeywordProcessorAgent()

for document in documents:
    keywords = document['keywords']
    result = agent.process_keywords(keywords)
    document['marc_data'] = result
```

### 3. Interactive Assistant
```python
# User uploads document
# OCR extracts text
# Agent processes keywords
# User reviews and confirms

agent = KeywordProcessorAgent()

while True:
    keywords = get_user_input()
    result = agent.process_keywords(keywords)
    display_to_user(result)
    if user_confirms():
        save_to_database(result)
```

## 🎯 Advantages

✅ **Tool-based Architecture** - Agent có thể gọi tools khi cần  
✅ **Framework Agnostic** - Hoạt động với CrewAI, LangGraph, LangChain  
✅ **Gemini Compatible** - Tích hợp dễ dàng với Gemini  
✅ **Production Ready** - Error handling, logging  
✅ **Type Safe** - Full type hints

## 📚 Framework Comparison

| Framework | Difficulty | Use Case | Best For |
|-----------|-----------|----------|----------|
| **CrewAI** | ⭐ Easy | Multi-agent teams | Quick setup, collaboration |
| **LangGraph** | ⭐⭐⭐ Hard | Complex workflows | State management, conditionals |
| **LangChain** | ⭐⭐ Medium | General agents | Standard use cases |
| **Standalone** | ⭐ Easy | Direct usage | Simple integration |

## 🔗 Resources

- CrewAI: https://github.com/joaomdmoura/crewAI
- LangGraph: https://github.com/langchain-ai/langgraph
- LangChain: https://python.langchain.com/
- Gemini: https://ai.google.dev/

---

**Status:** ✅ Ready to use  
**Updated:** November 2024
