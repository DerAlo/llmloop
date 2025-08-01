"""
Debug Test für Code Evolution System
"""

import json
from code_evolution import CodeEvolution

# Lade letzte Session
session_id = "00ad5701"
evolution = CodeEvolution(session_id)

print(f"Session ID: {session_id}")
print(f"Anzahl Versionen: {len(evolution.versions)}")
print(f"Current Version Index: {evolution.current_version}")

if evolution.versions:
    current = evolution.get_current_version()
    if current:
        print(f"Current Version ID: {current.version_id}")
        print(f"Current Version Code Length: {len(current.code)}")
        print(f"Current Version Quality: {current.quality_score}")
        print(f"First 100 chars: {current.code[:100]}")
    else:
        print("❌ get_current_version() returned None!")
else:
    print("❌ Keine Versionen in der Evolution!")

# Test error learning context
error_context = evolution.get_error_learning_context()
print(f"\nError Learning Context Length: {len(error_context)}")
print(f"Error Context Preview: {error_context[:200]}...")
