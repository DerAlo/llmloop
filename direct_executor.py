"""
Direct LLM Loop Executor
=======================

Direkte Ausführung des bewährten Systems ohne komplexe Dependencies
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from colorama import Fore, Style, init

init()

class DirectLLMExecutor:
    """Führt LLM Loop direkt aus"""
    
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results_dir = f"night_batch_{self.session_id}"
        os.makedirs(self.results_dir, exist_ok=True)
        
    def run_single_ea_generation(self, strategy_name: str):
        """Startet eine EA-Generation"""
        
        print(f"{Fore.YELLOW}🎯 Generiere {strategy_name} EA...{Style.RESET_ALL}")
        
        try:
            # Verwende das Task System für die Ausführung
            result = subprocess.run([
                "C:/Users/snofl/llmloop/.venv/Scripts/python.exe",
                "start_smart_loop.py",
                "--strategy", strategy_name,
                "--iterations", "15"
            ], 
            capture_output=True, 
            text=True, 
            timeout=1800,
            cwd=os.getcwd()
            )
            
            print(f"Return Code: {result.returncode}")
            if result.stdout:
                print(f"Output: {result.stdout[-1000:]}")
            if result.stderr and result.stderr.strip():
                print(f"Errors: {result.stderr[-500:]}")
            
            # Check für generierte Dateien
            mq5_files = [f for f in os.listdir(".") if f.endswith(".mq5") and strategy_name.lower() in f.lower()]
            
            if mq5_files and result.returncode == 0:
                # Verschiebe in Results Directory
                latest_file = max(mq5_files, key=os.path.getctime)
                target_path = os.path.join(self.results_dir, f"{strategy_name}_{self.session_id}.mq5")
                
                import shutil
                shutil.move(latest_file, target_path)
                
                print(f"{Fore.GREEN}✅ EA erfolgreich generiert: {target_path}{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}❌ EA-Generation fehlgeschlagen{Style.RESET_ALL}")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}❌ Fehler: {e}{Style.RESET_ALL}")
            return False
    
    def run_batch_generation(self, hours: int = 8):
        """Startet Batch-Generierung"""
        
        strategies = [
            "scalping_pro",
            "trend_following", 
            "breakout_trading",
            "swing_trading",
            "news_trading",
            "grid_trading"
        ]
        
        print(f"{Fore.CYAN}🚀 NIGHT BATCH GENERATION GESTARTET{Style.RESET_ALL}")
        print(f"Laufzeit: {hours} Stunden")
        print(f"Strategien: {len(strategies)}")
        print(f"Output: {self.results_dir}")
        print("="*70)
        
        start_time = datetime.now()
        successful_eas = 0
        
        # Zyklic durch Strategien für 8 Stunden
        import time
        strategy_index = 0
        
        while (datetime.now() - start_time).total_seconds() < hours * 3600:
            try:
                current_strategy = strategies[strategy_index % len(strategies)]
                strategy_index += 1
                
                print(f"\n{Fore.BLUE}⏰ {datetime.now().strftime('%H:%M:%S')} - Starte {current_strategy}{Style.RESET_ALL}")
                
                if self.run_single_ea_generation(current_strategy):
                    successful_eas += 1
                    print(f"{Fore.GREEN}🎉 Gesamt EAs: {successful_eas}{Style.RESET_ALL}")
                
                # 2 Minuten Pause zwischen EAs
                print(f"{Fore.BLUE}⏸️ Pause (2 min)...{Style.RESET_ALL}")
                time.sleep(120)
                
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}⚠️ Batch unterbrochen durch Benutzer{Style.RESET_ALL}")
                break
            except Exception as e:
                print(f"{Fore.RED}❌ Fehler in Batch: {e}{Style.RESET_ALL}")
                time.sleep(300)  # 5 Minuten bei Fehlern
        
        # Abschlussbericht
        total_time = datetime.now() - start_time
        print(f"\n{Fore.CYAN}📊 BATCH ABGESCHLOSSEN{Style.RESET_ALL}")
        print(f"Laufzeit: {total_time}")
        print(f"Erfolgreiche EAs: {successful_eas}")
        print(f"Results: {self.results_dir}")

def main():
    """Hauptfunktion"""
    executor = DirectLLMExecutor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "batch":
        # Batch-Modus für nächtliche Generierung
        executor.run_batch_generation(8)
    else:
        # Einzelner EA
        strategy = sys.argv[1] if len(sys.argv) > 1 else "trend_following"
        executor.run_single_ea_generation(strategy)

if __name__ == "__main__":
    main()
