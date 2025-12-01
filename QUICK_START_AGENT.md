# Quick Start: AI Agent

## 🚀 3 Bước Để Chạy Agent

### Step 1: Activate Environment

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Test Agent (No Framework)

```bash
python services/agents/ai_agent_with_tools.py
```

**Output:** Demonstrates all 6 tools với examples

### Step 3: Choose Framework

#### Option A: CrewAI (Easiest) ⭐

```bash
pip install crewai
```

Create `my_agent.py`:

```python
from crewai import Agent, Task, Crew
from services.agents.ai_agent_with_tools import KeywordProcessorAgent

# Create agent
keyword_agent = KeywordProcessorAgent()

# Define CrewAI agent
agent = Agent(
    role='Cataloger',
    goal='Chuẩn hóa keywords',
    tools=keyword_agent.get_available_tools()
)

# Task
task = Task(
    description='Process: diabetes, insulin',
    agent=agent
)

# Run
crew = Crew(agents=[agent], tasks=[task])
print(crew.kickoff())
```

Run:
```bash
python my_agent.py
```

#### Option B: LangGraph (Advanced)

```bash
pip install langgraph
```

```python
from langgraph.graph import Graph
from services.agents.ai_agent_with_tools import KeywordProcessorAgent

agent = KeywordProcessorAgent()

def process(state):
    return {'result': agent.process_keywords(state['keywords'])}

graph = Graph()
graph.add_node('process', process)
graph.set_entry_point('process')

result = graph.invoke({'keywords': ['diabetes']})
print(result)
```

#### Option C: Gemini Direct

```bash
pip install google-generativeai
```

```python
import google.generativeai as genai
from services.agents.ai_agent_with_tools import KeywordProcessorAgent

genai.configure(api_key="YOUR_KEY")
model = genai.GenerativeModel('gemini-1.5-pro')

agent = KeywordProcessorAgent()

response = model.generate_content(
    "Process keywords: diabetes, insulin",
    tools=agent.get_available_tools()
)

print(response)
```

## 📝 Common Tasks

### Task: Process Single Keyword

```python
from services.agents.ai_agent_with_tools import KeywordProcessorAgent

agent = KeywordProcessorAgent()
result = agent.search_single_keyword('diabetes', 'MESH')
print(result)
```

### Task: Get Classification + Keywords

```python
agent = KeywordProcessorAgent()
result = agent.process_keywords(['diabetes', 'insulin'])

# Extract
frameworks = result['output']['classification_framework']
keywords = result['output']['controlled_keywords']
```

### Task: Generate MARC Fields

```python
agent = KeywordProcessorAgent()
result = agent.generate_marc_fields(['diabetes'])
print(result['marc_fields'])
```

## ❓ Troubleshooting

### Issue: ModuleNotFoundError

**Solution:** Run from project root
```bash
cd c:\Workspace\Bien_muc\MARC-A-BOT
python backend/services/agents/ai_agent_with_tools.py
```

### Issue: MESH API 404

**Status:** Normal - External API may have changed endpoint  
**Impact:** Falls back to UNCONTROLLED, other APIs still work

### Issue: UnicodeEncodeError

**Solution:** Already fixed in code (removed emojis)

## 📊 Expected Output

```
Agent initialized with 6 tools
Available tools: ['search_authority_terms', 'map_keywords_to_authorities', ...]

Processing keywords: ['diabetes', 'insulin']
Found 1 classifications (LCC/NLM)
Found 2 controlled keywords (MESH/LCSH)

MARC Fields:
050 _4 $a R729
650 _0 $a Diabetes Mellitus
650 _0 $a Insulin
```

## 🎯 Next Steps

1. **Test standalone:** `python backend/services/agents/ai_agent_with_tools.py`
2. **Pick framework:** CrewAI (easy) or LangGraph (advanced)
3. **Install framework:** `pip install crewai`
4. **Create agent:** Use examples above
5. **Integrate Gemini:** Add API key và run

---

**Status:** ✅ Ready  
**Recommended:** Start với CrewAI (easiest)
