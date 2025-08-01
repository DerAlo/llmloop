"""
Production Batch EA Generator
============================

Automatisierte Batch-Generierung von Premium Expert Advisors
mit dem 4-Phasen Optimierungssystem für FTMO Trading
"""

import asyncio
import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict
import uuid

from smart_llm_loop import SmartLLMLoop
from llm_loop import main as run_original_loop  # Fallback
from colorama import Fore, Style, init

# Initialisiere Colorama
init()

class ProductionBatchGenerator:
    """Generiert automatisiert multiple Top-Quality EAs"""
    
    def __init__(self):
        self.session_id = str(uuid.uuid4())[:8]
        self.results_dir = f"production_batch_{self.session_id}"
        self.successful_eas = []
        self.failed_attempts = []
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'{self.results_dir}_batch.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Erstelle Results Directory
        os.makedirs(self.results_dir, exist_ok=True)
    
    async def run_production_batch(self, hours_to_run: int = 8):
        """Läuft für X Stunden und generiert kontinuierlich Top EAs"""
        
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=hours_to_run)
        
        print(f"{Fore.CYAN}🚀 PRODUCTION BATCH GESTARTET{Style.RESET_ALL}")
        print(f"⏰ Laufzeit: {hours_to_run} Stunden (bis {end_time.strftime('%H:%M:%S')})")
        print(f"📁 Output Directory: {self.results_dir}")
        print(f"🎯 Ziel: Maximum Top-Quality FTMO EAs generieren")
        print("="*80)
        
        # EA Strategien für verschiedene Märkte
        strategies = [
            {
                "name": "FTMO_ScalpingPro_EURUSD",
                "strategy": "scalping_pro",
                "symbol": "EURUSD",
                "timeframe": "M1",
                "description": "High-frequency scalping for EURUSD with FTMO risk management"
            },
            {
                "name": "FTMO_TrendFollower_GBPUSD", 
                "strategy": "trend_following",
                "symbol": "GBPUSD",
                "timeframe": "H1",
                "description": "Robust trend following system for GBPUSD with smart entry/exit"
            },
            {
                "name": "FTMO_BreakoutHunter_USDJPY",
                "strategy": "breakout_trading",
                "symbol": "USDJPY", 
                "timeframe": "H4",
                "description": "Breakout strategy for USDJPY with volatility filtering"
            },
            {
                "name": "FTMO_SwingMaster_AUDUSD",
                "strategy": "swing_trading",
                "symbol": "AUDUSD",
                "timeframe": "D1",
                "description": "Daily swing trading with momentum indicators"
            },
            {
                "name": "FTMO_GridRecovery_EURGBP",
                "strategy": "smart_grid",
                "symbol": "EURGBP",
                "timeframe": "H1", 
                "description": "Intelligent grid system with recovery mechanisms"
            },
            {
                "name": "FTMO_NewsTrader_USDCAD",
                "strategy": "news_trading",
                "symbol": "USDCAD",
                "timeframe": "M5",
                "description": "News-based trading with volatility spike detection"
            },
            {
                "name": "FTMO_MartingaleSuper_NZDUSD",
                "strategy": "adaptive_martingale",
                "symbol": "NZDUSD", 
                "timeframe": "M15",
                "description": "Adaptive martingale with dynamic lot sizing"
            },
            {
                "name": "FTMO_AIPredictor_GOLD",
                "strategy": "ai_prediction",
                "symbol": "XAUUSD",
                "timeframe": "H1",
                "description": "AI-based price prediction for Gold trading"
            }
        ]
        
        ea_count = 0
        strategy_index = 0
        
        while datetime.now() < end_time:
            try:
                current_strategy = strategies[strategy_index % len(strategies)]
                strategy_index += 1
                
                print(f"\n{Fore.YELLOW}🎯 GENERIERE EA #{ea_count + 1}: {current_strategy['name']}{Style.RESET_ALL}")
                print(f"Strategie: {current_strategy['strategy']} | Symbol: {current_strategy['symbol']} | Timeframe: {current_strategy['timeframe']}")
                
                # Generiere EA mit dem optimierten System
                success = await self.generate_single_ea(current_strategy, ea_count + 1)
                
                if success:
                    ea_count += 1
                    print(f"{Fore.GREEN}✅ EA #{ea_count} ERFOLGREICH GENERIERT!{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ EA-Generation fehlgeschlagen{Style.RESET_ALL}")
                
                # Status Update
                elapsed = datetime.now() - start_time
                remaining = end_time - datetime.now()
                print(f"📊 Status: {ea_count} EAs | ⏱️ Laufzeit: {elapsed} | ⏳ Verbleibend: {remaining}")
                
                # Kurze Pause zwischen EAs
                await asyncio.sleep(30)
                
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}⚠️ Batch-Generation durch Benutzer unterbrochen{Style.RESET_ALL}")
                break
            except Exception as e:
                self.logger.error(f"Fehler in Batch-Generation: {e}")
                await asyncio.sleep(60)  # Längere Pause bei Fehlern
        
        # Abschlussbericht
        await self.generate_final_report(start_time, ea_count)
    
    async def generate_single_ea(self, strategy_config: Dict, ea_number: int) -> bool:
        """Generiert einen einzelnen EA mit dem 4-Phasen System"""
        
        try:
            # Erstelle detaillierte Anweisung
            instruction = f"""
FTMO-CHALLENGE EXPERT ADVISOR ENTWICKLUNG
========================================

EA Name: {strategy_config['name']}
Strategie: {strategy_config['strategy']} 
Symbol: {strategy_config['symbol']}
Timeframe: {strategy_config['timeframe']}

BESCHREIBUNG:
{strategy_config['description']}

FTMO COMPLIANCE ANFORDERUNGEN:
✅ Maximum 2% Risiko pro Trade
✅ Maximum 5% Daily Loss Limit
✅ Maximum 10% Overall Loss Limit  
✅ Profit Target: 10% (Challenge), 5% (Verification)
✅ Minimum Trading Days: 10
✅ Maximum 30 Day Trading Period

TECHNISCHE SPEZIFIKATIONEN:
- Vollständige MQL5 Implementierung
- Dynamisches Risk Management
- Stop Loss & Take Profit obligatorisch
- Trail Stop für Profit Protection
- News Filter Integration
- Market Hours Filter
- Spread Protection
- Slippage Control

PERFORMANCE OPTIMIERUNG:
- Backtesting-kompatibel
- Multi-Symbol fähig
- Low Latency Execution
- Memory-effizient
- CPU-optimiert

ERZEUGEN SIE EINEN PROFESSIONELLEN, FTMO-KONFORMEN EXPERT ADVISOR!
"""
            
            # Smart LLM Loop initialisieren
            smart_loop = SmartLLMLoop()
            
            # EA generieren mit vollständiger 4-Phasen Optimierung
            final_code, stats = await smart_loop.run(
                strategy=strategy_config['strategy'],
                custom_instruction=instruction,
                max_iterations=20,  # Mehr Iterationen für bessere Qualität
                success_threshold=0.85  # Höhere Qualitätsanforderung
            )
            
            if final_code and stats.get('best_score', 0) >= 0.85:
                # Speichere erfolgreichen EA
                ea_filename = f"{strategy_config['name']}_v{ea_number}.mq5"
                ea_path = os.path.join(self.results_dir, ea_filename)
                
                with open(ea_path, 'w', encoding='utf-8') as f:
                    f.write(final_code)
                
                # Speichere Metadaten
                meta_data = {
                    "ea_name": strategy_config['name'],
                    "strategy": strategy_config['strategy'],
                    "symbol": strategy_config['symbol'],
                    "timeframe": strategy_config['timeframe'],
                    "quality_score": stats.get('best_score', 0),
                    "iterations_needed": stats.get('total_iterations', 0),
                    "generation_time": datetime.now().isoformat(),
                    "code_length": len(final_code),
                    "phase_usage": stats.get('phase_usage', {}),
                    "final_compilation": stats.get('successful_compilations', 0) > 0
                }
                
                meta_path = os.path.join(self.results_dir, f"{strategy_config['name']}_meta.json")
                with open(meta_path, 'w', encoding='utf-8') as f:
                    json.dump(meta_data, f, indent=2)
                
                self.successful_eas.append(meta_data)
                
                print(f"💾 EA gespeichert: {ea_filename}")
                print(f"📊 Qualität: {stats.get('best_score', 0):.1%}")
                print(f"🔄 Iterationen: {stats.get('total_iterations', 0)}")
                
                return True
            else:
                self.failed_attempts.append({
                    "ea_name": strategy_config['name'],
                    "reason": "Quality threshold not met",
                    "achieved_score": stats.get('best_score', 0),
                    "timestamp": datetime.now().isoformat()
                })
                return False
                
        except Exception as e:
            self.logger.error(f"Fehler bei EA-Generation {strategy_config['name']}: {e}")
            self.failed_attempts.append({
                "ea_name": strategy_config['name'],
                "reason": str(e),
                "timestamp": datetime.now().isoformat()
            })
            return False
    
    async def generate_final_report(self, start_time: datetime, ea_count: int):
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
            "average_quality": sum(ea['quality_score'] for ea in self.successful_eas) / len(self.successful_eas) if self.successful_eas else 0,
            "eas_per_hour": len(self.successful_eas) / (runtime.total_seconds() / 3600),
            "successful_eas_details": self.successful_eas,
            "failed_attempts_details": self.failed_attempts
        }
        
        report_path = os.path.join(self.results_dir, "batch_report.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n{Fore.CYAN}📊 BATCH-GENERATION ABGESCHLOSSEN{Style.RESET_ALL}")
        print("="*80)
        print(f"⏱️  Laufzeit: {runtime}")
        print(f"✅ Erfolgreiche EAs: {len(self.successful_eas)}")
        print(f"❌ Fehlgeschlagene Versuche: {len(self.failed_attempts)}")
        print(f"📈 Erfolgsrate: {report['success_rate']:.1%}")
        print(f"⭐ Durchschnittliche Qualität: {report['average_quality']:.1%}")
        print(f"🚀 EAs pro Stunde: {report['eas_per_hour']:.1f}")
        print(f"📁 Alle Dateien in: {self.results_dir}")
        print(f"📋 Detailbericht: {report_path}")
        
        if self.successful_eas:
            print(f"\n{Fore.GREEN}🏆 TOP EXPERT ADVISORS GENERIERT:{Style.RESET_ALL}")
            for ea in sorted(self.successful_eas, key=lambda x: x['quality_score'], reverse=True)[:5]:
                print(f"  ⭐ {ea['ea_name']} - Qualität: {ea['quality_score']:.1%}")

async def main():
    """Hauptfunktion für Batch-Generation"""
    
    print(f"{Fore.MAGENTA}🎯 FTMO EA BATCH GENERATOR{Style.RESET_ALL}")
    print("Generiert automatisiert Premium Expert Advisors mit 4-Phasen Optimierung")
    print("="*80)
    
    generator = ProductionBatchGenerator()
    
    # Laufe 8 Stunden (bis morgen früh)
    await generator.run_production_batch(hours_to_run=8)

if __name__ == "__main__":
    asyncio.run(main())
