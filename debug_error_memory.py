"""
Debug Test: ERROR MEMORY mit aktuellen Fehlern
"""

from code_evolution import CodeEvolution
from prompt_templates import PromptTemplates 
from knowledge_base import KnowledgeBase
import json

# Setup
kb = KnowledgeBase()
templates = PromptTemplates(kb)
evolution = CodeEvolution("00ad5701")

    # AKTUELLE FEHLER AUS DER EVOLUTION
    current_version = evolution.get_current_version()
    if current_version:
        print(f"Current Version: {current_version.version_id}")
        print(f"Compilation Errors: {len(current_version.compilation_errors)}")
        
        # Test mit aktuellen Fehlern
        current_errors = [error.error_message for error in current_version.compilation_errors[:5]]
        print(f"Using {len(current_errors)} errors")    prompts = templates.get_coder_generation_prompt(
        instruction="Fix the compilation errors",
        knowledge_context=kb.generate_knowledge_context(),
        previous_errors=current_errors,
        evolution=evolution
    )
    
    user_prompt = prompts["user"]
    
    print("\n=== CHECKING ERROR MEMORY ===")
    has_error_memory = "ERROR MEMORY" in user_prompt or "AKTUELLE FEHLER" in user_prompt
    print(f"Has Error Memory: {has_error_memory}")
    
    if has_error_memory:
        print("✅ ERROR MEMORY is working!")
    else:
        print("❌ ERROR MEMORY still not working!")
        
else:
    print("❌ No current version found!")
