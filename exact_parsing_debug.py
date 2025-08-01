"""
EXACT PARSING DEBUG - Findet das exakte Parsing-Problem
"""

from code_evolution import CodeEvolution
from prompt_templates import PromptTemplates
from knowledge_base import KnowledgeBase

# Setup
evolution = CodeEvolution("874d9c22")
kb = KnowledgeBase()
templates = PromptTemplates(kb)

# Finde Version mit Code
current_version = None
for version in evolution.versions:
    if len(version.code) > 1000:
        current_version = version
        break

# Generiere Prompt
prompts = templates.get_coder_generation_prompt(
    instruction="Fix the compilation errors",
    knowledge_context=kb.generate_knowledge_context(),
    previous_errors=["Test error"],
    evolution=evolution
)

user_prompt = prompts["user"]

# EXACT CODE PARSING
print("=== EXACT PARSING DEBUG ===")

code_start = user_prompt.find("```mql5")
code_end = user_prompt.find("```", code_start + 7)

if code_start >= 0 and code_end >= 0:
    # Zeige den Kontext um ```mql5
    context_start = max(0, code_start - 100)
    context_end = min(len(user_prompt), code_start + 200)
    context = user_prompt[context_start:context_end]
    
    print("Context around ```mql5:")
    print(repr(context))
    
    # Extrahiere Code exakt
    raw_extracted = user_prompt[code_start:code_end+3]
    print(f"\nRaw extracted section length: {len(raw_extracted)}")
    
    # Verschiedene Parsing-Versuche
    print("\n=== PARSING ATTEMPTS ===")
    
    # Attempt 1: Nach ```mql5
    attempt1 = user_prompt[code_start+7:code_end]
    print(f"Attempt 1 length: {len(attempt1)}")
    print(f"Attempt 1 first 100 chars: {repr(attempt1[:100])}")
    
    # Attempt 2: Nach ```mql5\n
    newline_pos = user_prompt.find('\n', code_start + 7)
    if newline_pos > 0:
        attempt2 = user_prompt[newline_pos+1:code_end]
        print(f"Attempt 2 length: {len(attempt2)}")
        print(f"Attempt 2 first 100 chars: {repr(attempt2[:100])}")
    
    # Vergleiche mit Original
    orig_first_100 = current_version.code[:100]
    print(f"\nOriginal first 100 chars: {repr(orig_first_100)}")
    
    # Test Matches
    print(f"\nAttempt 1 matches original: {attempt1 == current_version.code}")
    if newline_pos > 0:
        print(f"Attempt 2 matches original: {attempt2 == current_version.code}")
    
    # CHARACTER-BY-CHARACTER COMPARISON
    print(f"\n=== CHARACTER COMPARISON ===")
    if newline_pos > 0:
        test_code = attempt2
    else:
        test_code = attempt1
        
    for i in range(min(50, len(test_code), len(current_version.code))):
        orig_char = current_version.code[i]
        test_char = test_code[i]
        if orig_char != test_char:
            print(f"DIFF at pos {i}: orig='{orig_char}' ({ord(orig_char)}) vs test='{test_char}' ({ord(test_char)})")
            break
    else:
        print("First 50 characters match!")
