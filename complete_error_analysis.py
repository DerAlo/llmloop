"""
COMPLETE ERROR ANALYSIS - Vollständige Fehler-Analyse
"""

import subprocess
import tempfile
import os

def complete_error_analysis():
    """Vollständige Analyse aller Fehler"""
    
    from code_evolution import CodeEvolution
    
    evolution = CodeEvolution("f3762369")
    current_version = evolution.get_current_version()
    
    print("=== COMPLETE ERROR ANALYSIS ===")
    print(f"Version: {current_version.version_id}")
    print(f"Code length: {len(current_version.code)} chars")
    
    # Zeige die Evolution-Fehler
    print(f"\\n=== EVOLUTION REPORTED ERRORS ({len(current_version.compilation_errors)}) ===")
    for i, error in enumerate(current_version.compilation_errors[:10]):
        print(f"{i+1:2}. Type: {error.error_type}")
        print(f"    Message: {error.error_message}")
        print(f"    Line: {error.line_number}")
        print(f"    Snippet: {error.code_snippet[:50]}...")
        print()
    
    # Teste aktuelle Kompilierung
    print("=== ACTUAL COMPILATION TEST ===")
    code = current_version.code
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mq5', delete=False, encoding='utf-8') as temp_file:
        temp_file.write(code)
        temp_file_path = temp_file.name
    
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        compile_script = os.path.join(script_dir, "compile.ps1")
        
        result = subprocess.run([
            "powershell.exe",
            "-ExecutionPolicy", "Bypass",
            "-File", compile_script,
            "-FileToCompile", temp_file_path
        ], capture_output=True, text=True, timeout=120, check=False)
        
        print(f"Return Code: {result.returncode}")
        
        # Vollständige Log-Analyse
        log_file = temp_file_path + '.log'
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                log_content = f.read()
                
                print(f"\\nLog length: {len(log_content)} chars")
                
                # Alle Log-Zeilen analysieren
                log_lines = log_content.split('\\n')
                
                errors = []
                warnings = []
                info = []
                
                for line in log_lines:
                    line = line.strip()
                    if not line:
                        continue
                        
                    if ' : error ' in line:
                        errors.append(line)
                    elif ' : warning ' in line:
                        warnings.append(line)
                    elif ' : information' in line:
                        info.append(line)
                
                print(f"\\nParsed from log:")
                print(f"  Errors: {len(errors)}")
                print(f"  Warnings: {len(warnings)}")
                print(f"  Info: {len(info)}")
                
                if errors:
                    print(f"\\nActual errors found:")
                    for i, error in enumerate(errors[:10]):
                        print(f"  {i+1}. {error}")
                
                if warnings:
                    print(f"\\nWarnings found:")
                    for i, warning in enumerate(warnings[:5]):
                        print(f"  {i+1}. {warning}")
                
                # Show result summary
                print(f"\\n=== RESULT SUMMARY ===")
                success = (result.returncode == 0)
                ex5_exists = os.path.exists(temp_file_path.replace('.mq5', '.ex5'))
                
                print(f"Compilation success: {success}")
                print(f"EX5 file created: {ex5_exists}")
                print(f"Total actual errors: {len(errors)}")
                print(f"Evolution thinks: {len(current_version.compilation_errors)} errors")
                
                discrepancy = len(current_version.compilation_errors) - len(errors)
                print(f"ERROR DISCREPANCY: {discrepancy}")
                
                if discrepancy > 40:
                    print("🚨 MAJOR DISCREPANCY! Evolution error count is wrong!")
                
        # Cleanup
        try:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            ex5_file = temp_file_path.replace('.mq5', '.ex5')
            if os.path.exists(ex5_file):
                os.remove(ex5_file)
            if os.path.exists(log_file):
                os.remove(log_file)
        except Exception:
            pass
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    complete_error_analysis()
