"""
SYNC Template Code Fixing - Synchrone Version ohne async
"""

import subprocess
import tempfile
import os
from pathlib import Path

class SyncMQL5Validator:
    """Synchroner MQL5 Validator ohne async"""
    
    def validate_syntax_sync(self, code: str):
        """Synchrone Syntax-Validierung"""
        
        # Temporäre MQL5 Datei erstellen
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mq5', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name
        
        try:
            # PowerShell Compile-Skript verwenden
            script_dir = os.path.dirname(os.path.abspath(__file__))
            compile_script = os.path.join(script_dir, "compile.ps1")
            
            result = subprocess.run([
                "powershell.exe",
                "-ExecutionPolicy", "Bypass",
                "-File", compile_script,
                "-FileToCompile", temp_file_path
            ], capture_output=True, text=True, timeout=120, check=False)
            
            # Parse Fehler aus dem Output
            compilation_errors = []
            
            if result.returncode != 0:
                # Lese Log-Datei
                log_file = temp_file_path + '.log'
                if os.path.exists(log_file):
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        log_content = f.read()
                        
                        # Parse Fehler aus Log
                        for line in log_content.split('\n'):
                            if ' : error ' in line:
                                compilation_errors.append(line.strip())
            
            # Cleanup
            try:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                ex5_file = temp_file_path.replace('.mq5', '.ex5')
                if os.path.exists(ex5_file):
                    os.remove(ex5_file)
                log_file = temp_file_path + '.log'
                if os.path.exists(log_file):
                    os.remove(log_file)
            except Exception:
                pass
            
            return {
                'success': result.returncode == 0,
                'error_count': len(compilation_errors),
                'compilation_errors': compilation_errors
            }
            
        except Exception as e:
            print(f"Validation error: {e}")
            return {
                'success': False,
                'error_count': 999,
                'compilation_errors': [f"Validation failed: {e}"]
            }

def sync_template_fixing():
    """Synchrone Template-basierte Code-Fixing"""
    
    from code_evolution import CodeEvolution
    
    print("🔧 SYNC TEMPLATE-BASED CODE FIXING")
    print("=" * 40)
    
    evolution = CodeEvolution("f3762369")
    current_version = evolution.get_current_version()
    
    if not current_version:
        print("❌ Keine aktuelle Version gefunden!")
        return
    
    print(f"Current version: {current_version.version_id}")
    print(f"Original errors: {len(current_version.compilation_errors)}")
    
    # Wende Template-Fixes an
    print("🔧 Wende Syntax-Fixes an...")
    
    # Basic fixes
    fixed_code = current_version.code
    
    fixes = [
        # Include fixes
        ('#include <Trade\\Trade.mqh>', '#include <Trade\\\\Trade.mqh>'),
        ('#include <Trade/Trade.mqh>', '#include <Trade\\\\Trade.mqh>'),
        
        # Common errors
        ('Ask', 'SymbolInfoDouble(_Symbol, SYMBOL_ASK)'),
        ('Bid', 'SymbolInfoDouble(_Symbol, SYMBOL_BID)'),
        ('OP_BUY', 'ORDER_TYPE_BUY'),
        ('OP_SELL', 'ORDER_TYPE_SELL'),
        
        # Property fixes
        ('property copyright', '#property copyright'),
        ('property version', '#property version'),
        ('property link', '#property link'),
    ]
    
    for old, new in fixes:
        if old in fixed_code:
            fixed_code = fixed_code.replace(old, new)
            print(f"  ✅ Fixed: {old} → {new}")
    
    print(f"Fixed code length: {len(fixed_code)} Zeichen")
    
    # Teste Fixed Code
    validator = SyncMQL5Validator()
    print("🧪 Teste Fixed Code...")
    
    result = validator.validate_syntax_sync(fixed_code)
    
    print(f"Original errors: {len(current_version.compilation_errors)}")
    print(f"Fixed errors: {result['error_count']}")
    print(f"Compilation success: {result['success']}")
    
    improvement = len(current_version.compilation_errors) - result['error_count']
    print(f"Improvement: {improvement} Fehler behoben")
    
    if improvement > 0:
        print(f"✅ SUCCESS: {improvement} Fehler wurden behoben!")
        
        # Zeige die ersten behobenen Fehler
        if result['compilation_errors']:
            print("\\nVerbleibende Fehler (erste 5):")
            for i, error in enumerate(result['compilation_errors'][:5]):
                print(f"  {i+1}. {error}")
    else:
        print("❌ Template fixing brachte keine Verbesserung")
        
        # Zeige einige der neuen Fehler
        if result['compilation_errors']:
            print("\\nAktuelle Fehler (erste 5):")
            for i, error in enumerate(result['compilation_errors'][:5]):
                print(f"  {i+1}. {error}")

if __name__ == "__main__":
    sync_template_fixing()
