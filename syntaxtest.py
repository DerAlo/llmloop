"""
MetaEditor Syntax Test
=====================

Testet die MetaEditor Syntax-Prüfung isoliert um sicherzustellen,
dass die Kompilierung korrekt funktioniert.
"""

import os
import subprocess
import tempfile
from colorama import Fore, Style, init

# Initialisiere Colorama
init()

def test_metaeditor_syntax():
    """Testet die MetaEditor Syntax-Prüfung mit verschiedenen MQL5 Code-Beispielen"""
    
    metaeditor_path = r"C:\Program Files\MetaTrader 5\MetaEditor64.exe"
    
    if not os.path.exists(metaeditor_path):
        print(f"{Fore.RED}❌ MetaEditor64.exe nicht gefunden: {metaeditor_path}{Style.RESET_ALL}")
        return False
    
    print(f"{Fore.CYAN}🧪 MetaEditor Syntax-Test gestartet{Style.RESET_ALL}")
    print(f"MetaEditor Pfad: {metaeditor_path}")
    
    # Test 1: Gültiger MQL5 Code (sollte kompilieren)
    valid_code = """
//+------------------------------------------------------------------+
//|                                                   TestEA_Valid.mq5 |
//|                                  Copyright 2025, MetaQuotes Software Corp. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2025, MetaQuotes Software Corp."
#property link      "https://www.mql5.com"
#property version   "1.00"

input double LotSize = 0.01;
input int StopLoss = 50;

int OnInit()
{
    Print("Test EA initialisiert");
    return(INIT_SUCCEEDED);
}

void OnDeinit(const int reason)
{
    Print("Test EA beendet");
}

void OnTick()
{
    double balance = AccountInfoDouble(ACCOUNT_BALANCE);
    if(balance > 0)
    {
        Print("Balance: ", balance);
    }
}
"""
    
    # Test 2: Ungültiger MQL5 Code (sollte NICHT kompilieren)
    invalid_code = """
//+------------------------------------------------------------------+
//|                                                 TestEA_Invalid.mq5 |
//+------------------------------------------------------------------+
#property copyright "Test"
#property version   "1.00"

// Absichtliche Syntax-Fehler:
int OnInit()
{
    Print("Test EA initialisiert"  // Fehlende schließende Klammer
    return(INIT_SUCCEEDED);
}

void OnTick()
{
    undefined_function();  // Nicht existierende Funktion
    int x = "string";      // Typ-Fehler
}
"""
    
    print(f"\n{Fore.YELLOW}Test 1: Gültiger MQL5 Code{Style.RESET_ALL}")
    result1 = test_single_code(valid_code, "Valid", metaeditor_path)
    
    print(f"\n{Fore.YELLOW}Test 2: Ungültiger MQL5 Code{Style.RESET_ALL}")
    result2 = test_single_code(invalid_code, "Invalid", metaeditor_path)
    
    print(f"\n{Fore.CYAN}📊 Test-Ergebnisse:{Style.RESET_ALL}")
    print(f"Gültiger Code: {'✅ BESTANDEN' if result1 else '❌ FEHLGESCHLAGEN'}")
    print(f"Ungültiger Code: {'✅ BESTANDEN (korrekt abgelehnt)' if not result2 else '❌ FEHLGESCHLAGEN (fälschlicherweise akzeptiert)'}")
    
    overall_success = result1 and not result2
    print(f"\n{Fore.GREEN if overall_success else Fore.RED}Gesamt-Test: {'✅ ERFOLGREICH' if overall_success else '❌ FEHLGESCHLAGEN'}{Style.RESET_ALL}")
    
    return overall_success

def test_single_code(code: str, name: str, metaeditor_path: str) -> bool:
    """Testet einen einzelnen MQL5 Code"""
    
    # Temporäre MQL5 Datei erstellen
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mq5', delete=False, encoding='utf-8') as temp_file:
        temp_file.write(code)
        temp_file_path = temp_file.name
    
    print(f"Temporäre Datei: {temp_file_path}")
    
    try:
        # Verwende das PowerShell Compile-Skript für bessere Handhabung
        script_dir = os.path.dirname(os.path.abspath(__file__))
        compile_script = os.path.join(script_dir, "compile.ps1")
        
        print("Führe PowerShell Compile-Skript aus...")
        result = subprocess.run([
            "powershell.exe",
            "-ExecutionPolicy", "Bypass",
            "-File", compile_script,
            "-FileToCompile", temp_file_path
        ], capture_output=True, text=True, timeout=120, check=False)
        
        print(f"Return Code: {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        
        # Das PowerShell-Skript gibt 0 bei Erfolg zurück
        compilation_successful = (result.returncode == 0)
        print(f"Kompilierung erfolgreich (Return Code 0): {compilation_successful}")
        
        # Prüfe zusätzlich auf spezifische Fehlermeldungen im Output
        success_indicators = ["KOMPILIERUNG ERFOLGREICH", "ERFOLGREICH"]
        error_indicators = ["KOMPILIERUNG FEHLGESCHLAGEN", "FEHLGESCHLAGEN", "error", "Error", "ERROR"]
        
        has_success = any(indicator in result.stdout for indicator in success_indicators)
        has_errors = any(indicator in result.stderr for indicator in error_indicators)
        print(f"Erfolgs-Indikatoren gefunden: {has_success}")
        print(f"Explizite Fehler im STDERR: {has_errors}")
        
        # Prüfe .ex5 Datei (bei erfolgreichem Build)
        ex5_file = temp_file_path.replace('.mq5', '.ex5')
        ex5_exists = os.path.exists(ex5_file)
        print(f"EX5 Datei erstellt: {ex5_exists}")
        
        # Prüfe log Datei (das PowerShell-Skript zeigt den Log-Inhalt bereits an)
        log_file = temp_file_path + '.log'
        log_exists = os.path.exists(log_file)
        print(f"LOG Datei erstellt: {log_exists}")
        
        if log_exists:
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    log_content = f.read()
                    print(f"LOG Inhalt: {log_content[:200]}...")
                    has_log_errors = any(indicator in log_content.lower() for indicator in ["error", "failed"])
                    print(f"Fehler in LOG: {has_log_errors}")
            except Exception as e:
                print(f"Kann LOG nicht lesen: {e}")
        
        # Cleanup
        try:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                print("Temporäre .mq5 Datei gelöscht")
            if os.path.exists(ex5_file):
                os.remove(ex5_file)
                print("Temporäre .ex5 Datei gelöscht")
            if log_exists and os.path.exists(log_file):
                os.remove(log_file)
                print("Temporäre .log Datei gelöscht")
        except Exception as e:
            print(f"Cleanup Warnung: {e}")
        
        # Endgültige Bewertung - das PowerShell-Skript liefert zuverlässigere Ergebnisse
        # Ein Code ist syntaktisch korrekt wenn:
        # 1. Return Code 0 (erfolgreich)
        # 2. EX5 Datei wurde erstellt
        # 3. Keine Fehler im STDERR
        # 4. PowerShell-Skript zeigt "ERFOLGREICH" an
        syntax_ok = (compilation_successful and ex5_exists and not has_errors and has_success)
        
        color = Fore.GREEN if syntax_ok else Fore.RED
        print(f"{color}Endergebnis für {name}: {'✅ SYNTAX OK' if syntax_ok else '❌ SYNTAX FEHLER'}{Style.RESET_ALL}")
        
        return syntax_ok
        
    except subprocess.TimeoutExpired:
        print(f"{Fore.RED}❌ PowerShell Compile-Skript Timeout{Style.RESET_ALL}")
        try:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        except Exception:
            pass
        return False
        
    except Exception as e:
        print(f"{Fore.RED}❌ Fehler bei PowerShell Kompilierung: {e}{Style.RESET_ALL}")
        try:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        except Exception:
            pass
        return False

if __name__ == "__main__":
    test_metaeditor_syntax()
