"""
DEBUG: Warum wird der Code nicht erkannt obwohl er im Prompt steht?
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

print(f"Testing with version: {current_version.version_id}")
print(f"Original code length: {len(current_version.code)}")

# Generiere Prompt
prompts = templates.get_coder_generation_prompt(
    instruction="Fix the compilation errors",
    knowledge_context=kb.generate_knowledge_context(),
    previous_errors=["Test error"],
    evolution=evolution
)

user_prompt = prompts["user"]
print(f"User prompt length: {len(user_prompt)}")

# Debug: Finde Code-Sektion
print("\n=== DEBUGGING CODE SECTION ===")

# Suche nach verschiedenen Code-Patterns
patterns = [
    "```mql5",
    current_version.code[:100],
    current_version.code[:50],
    "FTMO_Expert_Advisor.mq5"
]

for i, pattern in enumerate(patterns):
    found = pattern in user_prompt
    print(f"Pattern {i+1} ('{pattern[:30]}...'): {found}")

# Extrahiere die tatsächliche Code-Sektion
code_start = user_prompt.find("```mql5")
if code_start >= 0:
    code_end = user_prompt.find("```", code_start + 7)
    if code_end >= 0:
        extracted_code = user_prompt[code_start+7:code_end]
        print(f"\nExtracted code length: {len(extracted_code)}")
        print(f"Original code length: {len(current_version.code)}")
        print(f"Match: {extracted_code == current_version.code}")
        
        # Prüfe die ersten Zeilen
        orig_lines = current_version.code.split('\n')[:5]
        extr_lines = extracted_code.split('\n')[:5]
        
        print("\nFirst 5 lines comparison:")
        for i, (orig, extr) in enumerate(zip(orig_lines, extr_lines)):
            match = orig == extr
            print(f"Line {i+1}: {match}")
            if not match:
                print(f"  Orig: '{orig}'")
                print(f"  Extr: '{extr}'")
                break
else:
    print("❌ Keine Code-Sektion gefunden!")

# KRITISCHER TEST: Was passiert wenn wir substring-search machen?
print(f"\n=== SUBSTRING SEARCH ===")
code_sample = current_version.code[100:600]  # Mittlerer Teil des Codes
found_substring = code_sample in user_prompt
print(f"Substring found: {found_substring}")

if not found_substring:
    # Finde ähnlichen Text
    print("Suche nach ähnlichem Text...")
    for line in current_version.code.split('\n')[5:15]:
        if line.strip() and len(line) > 20:
            found_line = line in user_prompt
            print(f"Line '{line[:50]}...': {found_line}")
            if found_line:
                break
