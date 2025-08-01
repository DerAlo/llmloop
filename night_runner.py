"""
Night Production Runner
======================

Simplified runner für die nächtliche EA-Produktion
"""

import subprocess
import os
import time
from datetime import datetime, timedelta
from colorama import Fore, Style, init

init()

def run_night_production():
    """Läuft die ganze Nacht und generiert EAs"""
    
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=8)
    
    print(f"{Fore.CYAN}🌙 NIGHT PRODUCTION GESTARTET{Style.RESET_ALL}")
    print(f"Start: {start_time.strftime('%H:%M:%S')}")
    print(f"Ende: {end_time.strftime('%H:%M:%S')}")
    print("="*50)
    
    results_dir = f"night_production_{start_time.strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(results_dir, exist_ok=True)
    
    successful_eas = 0
    
    # Strategien zyklisch abarbeiten
    strategies = ["trend_following", "scalping", "breakout", "swing", "grid", "news"]
    strategy_index = 0
    
    while datetime.now() < end_time:
        try:
            current_strategy = strategies[strategy_index % len(strategies)]
            strategy_index += 1
            
            current_time = datetime.now().strftime('%H:%M:%S')
            remaining = end_time - datetime.now()
            
            print(f"\n{Fore.YELLOW}⏰ {current_time} - EA #{successful_eas + 1}: {current_strategy.upper()}{Style.RESET_ALL}")
            print(f"⏳ Verbleibend: {str(remaining).split('.')[0]}")
            
            # Starte das bewährte smart_llm_loop System
            result = subprocess.run([
                "C:/Users/snofl/llmloop/.venv/Scripts/python.exe",
                "start_smart_loop.py",
                "--strategy", current_strategy
            ], 
            timeout=1800,  # 30 min max per EA
            cwd=os.getcwd()
            )
            
            if result.returncode == 0:
                # Suche nach neuen .mq5 Dateien
                mq5_files = [f for f in os.listdir(".") if f.endswith(".mq5")]
                if mq5_files:
                    # Neueste Datei in Results verschieben
                    latest = max(mq5_files, key=os.path.getctime)
                    target = os.path.join(results_dir, f"EA_{successful_eas + 1}_{current_strategy}_{current_time.replace(':', '')}.mq5")
                    
                    import shutil
                    shutil.move(latest, target)
                    
                    successful_eas += 1
                    print(f"{Fore.GREEN}✅ EA #{successful_eas} erfolgreich: {os.path.basename(target)}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ Keine .mq5 Datei generiert{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ Fehler bei EA-Generation (Code: {result.returncode}){Style.RESET_ALL}")
            
            # Kurze Pause
            print(f"{Fore.BLUE}⏸️ Pause (60s)...{Style.RESET_ALL}")
            time.sleep(60)
            
        except subprocess.TimeoutExpired:
            print(f"{Fore.YELLOW}⏰ Timeout - nächste Strategie{Style.RESET_ALL}")
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⚠️ Production durch Benutzer gestoppt{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}❌ Fehler: {e}{Style.RESET_ALL}")
            time.sleep(120)  # 2 min bei Fehlern
    
    # Abschlussbericht
    total_time = datetime.now() - start_time
    print(f"\n{Fore.CYAN}🎯 NIGHT PRODUCTION ABGESCHLOSSEN{Style.RESET_ALL}")
    print(f"Laufzeit: {str(total_time).split('.')[0]}")
    print(f"Generierte EAs: {successful_eas}")
    print(f"Output Directory: {results_dir}")
    
    if successful_eas > 0:
        print(f"\n{Fore.GREEN}🏆 ERFOLGREICHE EAs:{Style.RESET_ALL}")
        for f in os.listdir(results_dir):
            if f.endswith('.mq5'):
                print(f"  📄 {f}")

if __name__ == "__main__":
    run_night_production()
