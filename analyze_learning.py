"""
Analyse der letzten Session Error Memory Learning
"""

from code_evolution import CodeEvolution

# Lade die letzte Session
evolution = CodeEvolution("4b3dabaf")

print("=== SESSION ANALYSIS ===")
print(f"Versionen: {len(evolution.versions)}")

# Analyse Error Learning
learning_context = evolution.get_error_learning_context()
print(f"\nError Learning Context Length: {len(learning_context)}")

# Zeige wiederkehrende Fehler
recurring = evolution.get_recurring_errors()
print(f"\nWiederkehrende Fehler: {len(recurring)}")

for error, count in list(recurring.items())[:5]:
    print(f"  {count}x: {error[:100]}...")

# Zeige Version-zu-Version Verbesserungen
print(f"\n=== VERSION PROGRESSION ===")
for i, version in enumerate(evolution.versions):
    print(f"Version {i}: {len(version.compilation_errors)} Fehler, Score: {version.quality_score:.2f}")
    if i > 0:
        fixed = len(version.fixed_errors) if version.fixed_errors else 0
        print(f"  → {fixed} Fehler behoben")

# Targeted Feedback Analysis
feedback = evolution.get_targeted_feedback()
print(f"\n=== TARGETED FEEDBACK ===")
print(f"Length: {len(feedback)}")
print(feedback[:500] + "..." if len(feedback) > 500 else feedback)
