"""
DEEP CODE COMPARISON - Findet wo exakt der Unterschied ist
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

# Extract Code
code_start = user_prompt.find("```mql5")
code_end = user_prompt.find("```", code_start + 7)
newline_pos = user_prompt.find('\n', code_start + 7)
extracted_code = user_prompt[newline_pos+1:code_end]

print("=== DEEP CODE COMPARISON ===")
print(f"Original length: {len(current_version.code)}")
print(f"Extracted length: {len(extracted_code)}")
print(f"Length difference: {len(current_version.code) - len(extracted_code)}")

# Finde erste Differenz
orig = current_version.code
extr = extracted_code

min_len = min(len(orig), len(extr))
first_diff = -1

for i in range(min_len):
    if orig[i] != extr[i]:
        first_diff = i
        break

if first_diff >= 0:
    print(f"\nFirst difference at position: {first_diff}")
    
    # Zeige Kontext um die Differenz
    start = max(0, first_diff - 50)
    end = min(len(orig), first_diff + 50)
    
    print("Original context:")
    print(repr(orig[start:end]))
    
    if first_diff < len(extr):
        print("Extracted context:")
        print(repr(extr[start:end]))
    
    print(f"Char at diff - Orig: '{orig[first_diff]}' ({ord(orig[first_diff])})")
    if first_diff < len(extr):
        print(f"Char at diff - Extr: '{extr[first_diff]}' ({ord(extr[first_diff])})")
else:
    # Keine char-Differenz, aber verschiedene Längen
    if len(orig) != len(extr):
        print(f"\nNo character difference found, but length differs by {abs(len(orig) - len(extr))}")
        if len(orig) > len(extr):
            print("Original is longer - extracted is missing end:")
            print(repr(orig[len(extr):len(extr)+100]))
        else:
            print("Extracted is longer - extracted has extra at end:")
            print(repr(extr[len(orig):len(orig)+100]))

# CRITICAL TEST: Are there any non-printable characters?
print(f"\n=== NON-PRINTABLE CHARACTER CHECK ===")

def find_non_printable(text, name):
    non_printables = []
    for i, char in enumerate(text[:1000]):  # Check first 1000 chars
        if ord(char) < 32 and char not in ['\n', '\r', '\t']:
            non_printables.append((i, char, ord(char)))
    return non_printables

orig_np = find_non_printable(orig, "Original")
extr_np = find_non_printable(extr, "Extracted")

print(f"Non-printables in original: {len(orig_np)}")
print(f"Non-printables in extracted: {len(extr_np)}")

for i, char, code in orig_np[:5]:
    print(f"  Orig pos {i}: '{char}' (code {code})")

for i, char, code in extr_np[:5]:
    print(f"  Extr pos {i}: '{char}' (code {code})")

# FINAL TEST: Let's just check if the IMPORTANT parts are there
print(f"\n=== IMPORTANT PARTS CHECK ===")
important_strings = [
    "OnInit()",
    "OnTick()",
    "CTrade",
    "FTMO",
    "#include",
    "double LotSize"
]

for s in important_strings:
    orig_has = s in orig
    extr_has = s in extr
    print(f"'{s}': Orig={orig_has}, Extr={extr_has}, Match={orig_has==extr_has}")

# Show a meaningful portion of both
print(f"\n=== CODE COMPARISON (first 500 chars) ===")
print("ORIGINAL:")
print(orig[:500])
print("\nEXTRACTED:")
print(extr[:500])

print(f"\nFirst 500 chars match: {orig[:500] == extr[:500]}")
