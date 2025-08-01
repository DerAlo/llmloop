"""
DEBUG: Warum sind Fixed errors: 0?
"""

import subprocess
import tempfile
import os

def debug_compilation():
    """Debug die tatsächliche Kompilierung"""
    
    from code_evolution import CodeEvolution
    
    evolution = CodeEvolution("f3762369")
    current_version = evolution.get_current_version()
    
    print("=== COMPILATION DEBUG ===")
    print(f"Version: {current_version.version_id}")
    print(f"Evolution reported errors: {len(current_version.compilation_errors)}")
    
    # Teste die Kompilierung direkt
    code = current_version.code
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mq5', delete=False, encoding='utf-8') as temp_file:
        temp_file.write(code)
        temp_file_path = temp_file.name
    
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        compile_script = os.path.join(script_dir, "compile.ps1")
        
        print(f"\\nCompiling: {temp_file_path}")
        
        result = subprocess.run([
            "powershell.exe",
            "-ExecutionPolicy", "Bypass",
            "-File", compile_script,
            "-FileToCompile", temp_file_path
        ], capture_output=True, text=True, timeout=120, check=False)
        
        print(f"Return Code: {result.returncode}")
        print(f"Success: {result.returncode == 0}")
        
        # Lese Log-Datei
        log_file = temp_file_path + '.log'
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                log_content = f.read()
                
                print(f"\\n=== LOG CONTENT ===")
                print(log_content[:1000] + "..." if len(log_content) > 1000 else log_content)
                
                # Count actual errors
                error_lines = [line for line in log_content.split('\\n') if ' : error ' in line]
                print(f"\\nActual error count from log: {len(error_lines)}")
                
                if error_lines:
                    print("\\nFirst 5 errors:")
                    for i, error in enumerate(error_lines[:5]):
                        print(f"  {i+1}. {error}")
        else:
            print("❌ No log file found!")
            
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
    debug_compilation()
