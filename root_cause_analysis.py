"""
ROOT CAUSE ANALYSIS - Warum generiert der LLM immer neuen fehlerhaften Code?
===========================================================================

Prüft ob der LLM tatsächlich den vorherigen Code bekommt oder immer von vorne anfängt.
"""

from code_evolution import CodeEvolution

def analyze_code_continuity():
    """Prüft ob Code zwischen Iterationen kontinuierlich weitergegeben wird"""
    
    # Lade die letzte Session
    evolution = CodeEvolution("874d9c22")
    versions = evolution.versions
    
    print("🔍 CODE CONTINUITY ANALYSIS")
    print("=" * 50)
    print(f"Versionen analysiert: {len(versions)}")
    
    # Prüfe Code-Längen und Content-Ähnlichkeit
    for i, version in enumerate(versions[:10]):  # Erste 10 Versionen
        code_length = len(version.code)
        has_errors = len(version.compilation_errors) > 0
        
        print(f"\nVersion {i}:")
        print(f"  Code Länge: {code_length:,} Zeichen")
        print(f"  Compilation Errors: {len(version.compilation_errors)}")
        print(f"  Quality Score: {version.quality_score:.2f}")
        
        # Prüfe ob Code-Strukturen ähnlich sind
        if i > 0:
            prev_version = versions[i-1]
            similarity = calculate_similarity(prev_version.code, version.code)
            print(f"  Ähnlichkeit zu v{i-1}: {similarity:.1f}%")
            
            # KRITISCH: Prüfe ob der Code komplett neu ist
            if similarity < 30 and code_length > 1000:
                print(f"  🚨 PROBLEM: Code ist komplett neu! (Similarity: {similarity:.1f}%)")
            elif code_length < 100:
                print(f"  ⚠️ WARNING: Code zu kurz - möglicherweise leer oder unvollständig!")
        
        # Zeige ersten Code-Ausschnitt
        if code_length > 0:
            code_preview = version.code[:200].replace('\n', '\\n')
            print(f"  Code Preview: {code_preview}...")

def calculate_similarity(code1: str, code2: str) -> float:
    """Berechnet die Ähnlichkeit zwischen zwei Code-Strings"""
    if not code1 or not code2:
        return 0.0
    
    # Einfache Ähnlichkeits-Berechnung basierend auf gemeinsamen Zeilen
    lines1 = set(line.strip() for line in code1.split('\n') if line.strip())
    lines2 = set(line.strip() for line in code2.split('\n') if line.strip())
    
    if not lines1 or not lines2:
        return 0.0
    
    common_lines = lines1.intersection(lines2)
    total_lines = lines1.union(lines2)
    
    return (len(common_lines) / len(total_lines)) * 100

def check_prompt_integration():
    """Prüft ob die Prompt-Templates den vorherigen Code korrekt integrieren"""
    
    print(f"\n🔍 PROMPT INTEGRATION CHECK")
    print("=" * 50)
    
    from prompt_templates import PromptTemplates
    from knowledge_base import KnowledgeBase
    
    kb = KnowledgeBase()
    templates = PromptTemplates(kb)
    evolution = CodeEvolution("874d9c22")
    
    # Test mit einer Version die Code hat
    current_version = None
    for version in evolution.versions:
        if len(version.code) > 1000:  # Version mit substantiellem Code
            current_version = version
            break
    
    if not current_version:
        print("❌ Keine Version mit substantiellem Code gefunden!")
        return
    
    print(f"Teste mit Version: {current_version.version_id}")
    print(f"Code Länge: {len(current_version.code):,} Zeichen")
    
    # Generiere Prompt wie im System
    prompts = templates.get_coder_generation_prompt(
        instruction="Fix the compilation errors",
        knowledge_context=kb.generate_knowledge_context(),
        previous_errors=["Test error"],
        evolution=evolution
    )
    
    user_prompt = prompts["user"]
    
    # Prüfe ob der Code im Prompt enthalten ist
    code_in_prompt = current_version.code[:500] in user_prompt
    print(f"Vorheriger Code im Prompt: {code_in_prompt}")
    
    if code_in_prompt:
        print("✅ Code wird korrekt an LLM weitergegeben!")
    else:
        print("🚨 CRITICAL BUG: Code wird NICHT an LLM weitergegeben!")
        
        # Debug: Schaue was im Prompt steht
        print(f"\nPrompt Länge: {len(user_prompt):,} Zeichen")
        has_code_section = "VORHERIGE VERSION" in user_prompt
        print(f"Hat 'VORHERIGE VERSION' Sektion: {has_code_section}")
        
        if has_code_section:
            # Finde die Code-Sektion
            start = user_prompt.find("```mql5")
            end = user_prompt.find("```", start + 1)
            if start > 0 and end > 0:
                code_section = user_prompt[start:end+3]
                print(f"Code Sektion Länge: {len(code_section)} Zeichen")
                print(f"Code Sektion Preview: {code_section[:200]}...")
            else:
                print("❌ Keine ```mql5 Code-Sektion gefunden!")

if __name__ == "__main__":
    analyze_code_continuity()
    check_prompt_integration()
