"""
Simplified Production EA Generator
=================================

Nutzt das bewährte llm_loop.py System für nächtliche EA-Generierung
"""

import asyncio
import os
import sys
import subprocess
import json
import logging
from datetime import datetime, timedelta
from typing import Dict
import uuid
from colorama import Fore, Style, init

# Initialisiere Colorama
init()

class SimplifiedBatchGenerator:
    """Nutzt llm_loop.py für Batch-Generierung"""
    
    def __init__(self):
        self.session_id = str(uuid.uuid4())[:8]
        self.results_dir = f"production_eas_{self.session_id}"
        self.successful_eas = []
        self.failed_attempts = []
        
        # Erstelle Results Directory
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Setup logging
        log_file = os.path.join(self.results_dir, "batch_generation.log")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def run_production_batch(self, hours_to_run: int = 8):
        """Läuft für X Stunden und generiert kontinuierlich EAs"""
        
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=hours_to_run)
        
        print(f"{Fore.CYAN}🚀 FTMO EA PRODUCTION BATCH GESTARTET{Style.RESET_ALL}")
        print(f"⏰ Laufzeit: {hours_to_run} Stunden (bis {end_time.strftime('%H:%M:%S')})")
        print(f"📁 Output Directory: {self.results_dir}")
        print("🎯 Ziel: Maximum Top-Quality FTMO EAs generieren")
        print("="*80)
        
        # FTMO EA Strategien
        strategies = [
            "scalping_pro",
            "trend_following", 
            "breakout_trading",
            "swing_trading",
            "smart_grid",
            "news_trading",
            "adaptive_martingale",
            "ai_prediction"
        ]
        
        ea_count = 0
        strategy_index = 0
        
        try:
            while datetime.now() < end_time:
                current_strategy = strategies[strategy_index % len(strategies)]
                strategy_index += 1
                
                print(f"\n{Fore.YELLOW}🎯 GENERIERE EA #{ea_count + 1}: {current_strategy.upper()}{Style.RESET_ALL}")
                
                # Generiere EA mit llm_loop.py
                success = self.generate_single_ea_with_llm_loop(current_strategy, ea_count + 1)
                
                if success:
                    ea_count += 1
                    print(f"{Fore.GREEN}✅ EA #{ea_count} ERFOLGREICH GENERIERT!{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ EA-Generation fehlgeschlagen{Style.RESET_ALL}")
                
                # Status Update
                elapsed = datetime.now() - start_time
                remaining = end_time - datetime.now()
                print(f"📊 Status: {ea_count} EAs | ⏱️ Laufzeit: {str(elapsed).split('.')[0]} | ⏳ Verbleibend: {str(remaining).split('.')[0]}")
                
                # Pause zwischen EAs (30 Sekunden)
                if datetime.now() < end_time:
                    print(f"{Fore.BLUE}⏸️ Kurze Pause (30s)...{Style.RESET_ALL}")
                    import time
                    time.sleep(30)
                
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⚠️ Batch-Generation durch Benutzer unterbrochen{Style.RESET_ALL}")
        
        # Abschlussbericht
        self.generate_final_report(start_time, ea_count)
    
    def generate_single_ea_with_llm_loop(self, strategy: str, ea_number: int) -> bool:
        """Generiert einen EA mit dem bewährten llm_loop.py"""
        
        try:
            print(f"🔧 Starte llm_loop.py für {strategy}...")
            
            # Führe llm_loop.py aus - aber start_smart_loop.py existiert
            result = subprocess.run([
                sys.executable, "start_smart_loop.py"
            ], 
            capture_output=True, 
            text=True, 
            timeout=1800,  # 30 Minuten timeout pro EA
            cwd=os.getcwd()
            )
            
            print(f"Return Code: {result.returncode}")
            if result.stdout:
                print(f"STDOUT: {result.stdout[-500:]}")  # Letzte 500 Zeichen
            if result.stderr:
                print(f"STDERR: {result.stderr[-500:]}")
            
            # Check if EA was generated
            if result.returncode == 0:
                # Suche nach generierten .mq5 Dateien
                generated_files = [f for f in os.listdir(".") if f.endswith(".mq5") and "temp" not in f.lower()]
                
                if generated_files:
                    # Nimm die neueste Datei
                    latest_file = max(generated_files, key=os.path.getctime)
                    
                    # Erstelle neuen Namen
                    ea_name = f"FTMO_{strategy}_{ea_number}.mq5"
                    ea_path = os.path.join(self.results_dir, ea_name)
                    
                    # Kopiere und benenne um
                    import shutil
                    shutil.copy2(latest_file, ea_path)
                    
                    # Lese Code für Analyse
                    with open(ea_path, 'r', encoding='utf-8') as f:
                        code_content = f.read()
                    
                    # Speichere Metadaten
                    meta_data = {
                        "ea_name": ea_name,
                        "strategy": strategy,
                        "generation_time": datetime.now().isoformat(),
                        "code_length": len(code_content),
                        "source_file": latest_file,
                        "generation_successful": True
                    }
                    
                    meta_path = os.path.join(self.results_dir, f"FTMO_{strategy}_{ea_number}_meta.json")
                    with open(meta_path, 'w', encoding='utf-8') as f:
                        json.dump(meta_data, f, indent=2)
                    
                    self.successful_eas.append(meta_data)
                    
                    print(f"💾 EA gespeichert: {ea_name}")
                    print(f"📏 Code-Länge: {len(code_content):,} Zeichen")
                    
                    # Cleanup original file
                    try:
                        os.remove(latest_file)
                    except:
                        pass
                    
                    return True
                else:
                    print("❌ Keine .mq5 Datei generiert")
                    return False
            else:
                print(f"❌ llm_loop.py failed with code {result.returncode}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ Timeout bei EA-Generation (30 min)")
            return False
        except Exception as e:
            print(f"❌ Fehler bei EA-Generation: {e}")
            self.logger.error(f"EA Generation Error: {e}")
            return False
    
    def generate_final_report(self, start_time: datetime, ea_count: int):
        """Generiert Abschlussbericht"""
        
        end_time = datetime.now()
        runtime = end_time - start_time
        
        report = {
            "batch_session": self.session_id,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "total_runtime_hours": runtime.total_seconds() / 3600,
            "successful_eas": len(self.successful_eas),
            "failed_attempts": len(self.failed_attempts),
            "success_rate": len(self.successful_eas) / (len(self.successful_eas) + len(self.failed_attempts)) if (len(self.successful_eas) + len(self.failed_attempts)) > 0 else 0,
            "eas_per_hour": len(self.successful_eas) / (runtime.total_seconds() / 3600),
            "successful_eas_details": self.successful_eas
        }
        
        report_path = os.path.join(self.results_dir, "batch_report.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n{Fore.CYAN}📊 BATCH-GENERATION ABGESCHLOSSEN{Style.RESET_ALL}")
        print("="*80)
        print(f"⏱️  Laufzeit: {str(runtime).split('.')[0]}")
        print(f"✅ Erfolgreiche EAs: {len(self.successful_eas)}")
        print(f"❌ Fehlgeschlagene Versuche: {len(self.failed_attempts)}")
        if len(self.successful_eas) + len(self.failed_attempts) > 0:
            print(f"📈 Erfolgsrate: {report['success_rate']:.1%}")
        print(f"🚀 EAs pro Stunde: {report['eas_per_hour']:.1f}")
        print(f"📁 Alle EAs in: {self.results_dir}")
        print(f"📋 Detailbericht: {report_path}")
        
        if self.successful_eas:
            print(f"\n{Fore.GREEN}🏆 GENERIERTE EXPERT ADVISORS:{Style.RESET_ALL}")
            for i, ea in enumerate(self.successful_eas, 1):
                print(f"  {i}. {ea['ea_name']} - {ea['code_length']:,} Zeichen")

def main():
    """Hauptfunktion"""
    
    print(f"{Fore.MAGENTA}🎯 FTMO EA BATCH GENERATOR (Simplified){Style.RESET_ALL}")
    print("Nutzt das bewährte llm_loop.py für kontinuierliche EA-Generierung")
    print("="*80)
    
    generator = SimplifiedBatchGenerator()
    
    # Laufe 8 Stunden (bis morgen früh)
    generator.run_production_batch(hours_to_run=8)

if __name__ == "__main__":
    main()
