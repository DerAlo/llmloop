"""
CRITICAL ERROR ANALYSIS - Warum werden Fehler nicht besser?
===========================================================

Analysiert die Evolution-Sessions um herauszufinden warum trotz
Error Memory die Fehler-Anzahl nicht reduziert wird.
"""

import json
import os
from pathlib import Path
from collections import Counter, defaultdict
from code_evolution import CodeEvolution

def analyze_error_progression():
    """Analysiert die Fehler-Progression über alle Sessions"""
    
    print("🔍 CRITICAL ERROR ANALYSIS")
    print("=" * 60)
    
    # Finde alle Evolution JSON Dateien
    evolution_files = list(Path('.').glob('evolution_*.json'))
    print(f"Gefundene Sessions: {len(evolution_files)}")
    
    if not evolution_files:
        print("❌ Keine Evolution Dateien gefunden!")
        return
    
    # Analysiere jede Session
    for evo_file in evolution_files[-3:]:  # Letzte 3 Sessions
        session_id = evo_file.stem.replace('evolution_', '')
        print(f"\n📊 ANALYZING SESSION: {session_id}")
        print("-" * 40)
        
        try:
            evolution = CodeEvolution(session_id)
            analyze_single_session(evolution, session_id)
        except Exception as e:
            print(f"❌ Fehler beim Laden von {session_id}: {e}")
    
    # Globale Analyse aller häufigsten Fehler
    print(f"\n🎯 GLOBAL ERROR PATTERN ANALYSIS")
    print("=" * 50)
    analyze_global_error_patterns()

def analyze_single_session(evolution: CodeEvolution, session_id: str):
    """Analysiert eine einzelne Session im Detail"""
    
    versions = evolution.versions
    print(f"Versionen: {len(versions)}")
    
    if len(versions) == 0:
        print("❌ Keine Versionen in dieser Session!")
        return
    
    # Fehler-Progression Analysis
    print("\n🔄 FEHLER PROGRESSION:")
    for i, version in enumerate(versions):
        error_count = len(version.compilation_errors)
        fixed_count = len(version.fixed_errors) if version.fixed_errors else 0
        
        status = "✅" if version.compilation_success else "❌"
        print(f"  v{i}: {status} {error_count} Fehler ({fixed_count} behoben)")
        
        # Zeige die häufigsten Fehler dieser Version
        if version.compilation_errors and i < 3:  # Nur erste 3 Versionen
            error_types = [err.error_type for err in version.compilation_errors[:5]]
            error_counter = Counter(error_types)
            print(f"    Top Fehler: {dict(error_counter.most_common(3))}")
    
    # Wiederkehrende Fehler Analysis
    recurring = evolution.get_recurring_errors()
    print(f"\n🔄 WIEDERKEHRENDE FEHLER: {len(recurring)}")
    for error, count in list(recurring.items())[:5]:
        print(f"  {count}x: {error[:80]}...")
    
    # Error Learning Context Analysis
    context = evolution.get_error_learning_context()
    print(f"\n📚 ERROR LEARNING CONTEXT: {len(context)} Zeichen")
    
    # Pattern Recognition: Werden gleiche Fehler wirklich behoben?
    print(f"\n🎯 PATTERN ANALYSIS:")
    analyze_error_patterns(versions)

def analyze_error_patterns(versions):
    """Analysiert ob gleiche Fehler über Versionen hinweg behoben werden"""
    
    if len(versions) < 2:
        print("  ⚠️ Zu wenige Versionen für Pattern-Analyse")
        return
    
    # Sammle alle Fehler-Messages über alle Versionen
    version_errors = {}
    for i, version in enumerate(versions):
        if version.compilation_errors:
            version_errors[i] = {err.error_message for err in version.compilation_errors}
    
    # Prüfe welche Fehler zwischen Versionen persistieren
    persistent_errors = set()
    if len(version_errors) >= 2:
        first_errors = version_errors.get(0, set())
        last_errors = version_errors.get(len(versions)-1, set())
        
        # Fehler die vom ersten bis zum letzten bestehen
        persistent_errors = first_errors.intersection(last_errors)
        
        print(f"  Persistente Fehler (v0 → v{len(versions)-1}): {len(persistent_errors)}")
        for error in list(persistent_errors)[:3]:
            print(f"    🔄 {error[:60]}...")
    
    # Prüfe welche neuen Fehler hinzugekommen sind
    if len(version_errors) >= 2:
        first_errors = version_errors.get(0, set())
        last_errors = version_errors.get(len(versions)-1, set())
        
        new_errors = last_errors - first_errors
        print(f"  Neue Fehler hinzugekommen: {len(new_errors)}")
        for error in list(new_errors)[:3]:
            print(f"    ➕ {error[:60]}...")

def analyze_global_error_patterns():
    """Analysiert globale Fehler-Patterns über alle Sessions"""
    
    all_errors = Counter()
    all_fixed_errors = Counter()
    
    # Sammle alle Fehler aus allen Sessions
    evolution_files = list(Path('.').glob('evolution_*.json'))
    for evo_file in evolution_files:
        try:
            session_id = evo_file.stem.replace('evolution_', '')
            evolution = CodeEvolution(session_id)
            
            # Sammle Fehler
            for version in evolution.versions:
                if version.compilation_errors:
                    for error in version.compilation_errors:
                        all_errors[error.error_type] += 1
                
                if version.fixed_errors:
                    for error in version.fixed_errors:
                        all_fixed_errors[error] += 1
        except Exception as e:
            print(f"⚠️ Fehler beim Laden {session_id}: {e}")
    
    print(f"📊 GLOBAL ERROR STATISTICS:")
    print(f"  Total Error Types: {len(all_errors)}")
    print(f"  Total Fixed Errors: {sum(all_fixed_errors.values())}")
    
    print(f"\n🔥 TOP 10 HÄUFIGSTE FEHLER-TYPEN:")
    for error_type, count in all_errors.most_common(10):
        fix_rate = all_fixed_errors.get(error_type, 0)
        print(f"  {count:3}x {error_type[:50]:<50} (Fixed: {fix_rate})")
    
    # KRITISCHE ERKENNTNIS: Fix-Rate Analyse
    print(f"\n⚡ CRITICAL INSIGHTS:")
    total_errors = sum(all_errors.values())
    total_fixed = sum(all_fixed_errors.values())
    fix_rate = (total_fixed / total_errors * 100) if total_errors > 0 else 0
    
    print(f"  Total Errors Generated: {total_errors}")
    print(f"  Total Errors Fixed: {total_fixed}")
    print(f"  Global Fix Rate: {fix_rate:.1f}%")
    
    if fix_rate < 50:
        print(f"  🚨 PROBLEM: Fix-Rate unter 50%! LLM lernt nicht effektiv!")
    else:
        print(f"  ✅ Fix-Rate über 50% - LLM lernt, aber nicht schnell genug!")

if __name__ == "__main__":
    analyze_error_progression()
