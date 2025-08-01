"""
Debug Test für Prompt Templates
"""

from code_evolution import CodeEvolution
from prompt_templates import PromptTemplates 
from knowledge_base import KnowledgeBase

# Setup
kb = KnowledgeBase()
templates = PromptTemplates(kb)
evolution = CodeEvolution("00ad5701")

# Test der Prompt-Generierung
knowledge_context = kb.generate_knowledge_context()
instruction = "Test instruction"

prompts = templates.get_coder_generation_prompt(
    instruction=instruction,
    knowledge_context=knowledge_context,
    previous_errors=[],
    evolution=evolution
)

user_prompt = prompts["user"]

print("=== USER PROMPT PREVIEW ===")
print(user_prompt[:2000])
print("\n=== CHECKING FOR KEY ELEMENTS ===")

# Check key elements
has_previous_code = "VORHERIGE VERSION" in user_prompt
has_error_memory = "ERROR MEMORY" in user_prompt
has_evolution_feedback = "EVOLUTION GUIDANCE" in user_prompt

print(f"Has Previous Code Context: {has_previous_code}")
print(f"Has Error Memory: {has_error_memory}")  
print(f"Has Evolution Feedback: {has_evolution_feedback}")

if has_previous_code:
    print("\n✅ Previous Code IS being included!")
else:
    print("\n❌ Previous Code is NOT being included!")
    
print(f"\nTotal User Prompt Length: {len(user_prompt)}")
