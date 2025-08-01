"""
Smart LLM Loop Starter
=====================

Startet den Next-Generation FTMO EA Generator mit verschiedenen Optionen.
"""

import asyncio
import argparse
import sys
from pathlib import Path

from smart_llm_loop import SmartLLMLoop
from colorama import Fore, Style, init

init()

def print_banner():
    """Zeigt das Startup-Banner"""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║               🚀 SMART LLM LOOP - FTMO EA GENERATOR              ║
║                         Next Generation                          ║
║                                                                  ║
║  🧠 Intelligent Context & Memory                                ║
║  🎯 Structured LLM Communication                                ║
║  📈 Code Evolution Tracking                                     ║
║  🔬 Comprehensive Validation                                    ║
║  🏭 Production-Ready Pipeline                                   ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)

def print_strategies():
    """Zeigt verfügbare Strategien"""
    strategies = {
        "trend_following": "📈 Trend-Following mit EMA/MACD Confluence",
        "mean_reversion": "🔄 Mean Reversion mit RSI/Bollinger Bands", 
        "breakout": "💥 Breakout Trading mit Support/Resistance",
        "scalping": "⚡ High-Frequency Scalping M1/M5",
        "swing": "🌊 Swing Trading H4/D1 Timeframes",
        "grid": "🕸️ Grid Trading mit Risk Management",
        "martingale": "🎲 Controlled Martingale System",
        "multi_timeframe": "⏰ Multi-Timeframe Analysis EA"
    }
    
    print(f"\n{Fore.YELLOW}📋 VERFÜGBARE STRATEGIEN:{Style.RESET_ALL}")
    for key, description in strategies.items():
        print(f"  {key:<18} - {description}")

async def run_generator(strategy: str, target_quality: float, max_iterations: int):
    """Startet den EA Generator"""
    print_banner()
    
    print(f"{Fore.GREEN}🎯 Konfiguration:{Style.RESET_ALL}")
    print(f"   Strategie: {strategy.title()}")
    print(f"   Ziel-Qualität: {target_quality:.1%}")
    print(f"   Max Iterationen: {max_iterations}")
    
    try:
        # Smart LLM Loop initialisieren
        loop = SmartLLMLoop()
        
        # Generator starten
        result = await loop.run(
            strategy=strategy,
            target_quality=target_quality,
            max_iterations=max_iterations
        )
        
        if result["success"]:
            print(f"\n{Fore.GREEN}🎉 ERFOLG! Expert Advisor generiert:{Style.RESET_ALL}")
            print(f"📄 Datei: {result['ea_file']}")
            print(f"📊 Qualität: {result['final_score']:.1%}")
            print(f"📋 Session Report: {result['report_file']}")
            print(f"🆔 Session ID: {result['session_id']}")
            
            # Empfehlungen
            if result['final_score'] >= 0.9:
                print(f"\n{Fore.GREEN}⭐ EXCELLENT! Dieser EA ist produktionsreif!{Style.RESET_ALL}")
            elif result['final_score'] >= 0.8:
                print(f"\n{Fore.YELLOW}👍 GOOD! EA ist gut, kleine Verbesserungen möglich.{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.YELLOW}⚠️ ACCEPTABLE. Weitere Iterationen empfohlen.{Style.RESET_ALL}")
        
        return result
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️ Abbruch durch Benutzer{Style.RESET_ALL}")
        return None
    except Exception as e:
        print(f"\n{Fore.RED}❌ Fehler: {e}{Style.RESET_ALL}")
        return None

def main():
    """Hauptfunktion mit Argument-Parsing"""
    parser = argparse.ArgumentParser(
        description="Smart LLM Loop - Next Generation FTMO EA Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  python start_smart_loop.py --strategy trend_following
  python start_smart_loop.py --strategy scalping --quality 0.9
  python start_smart_loop.py --list-strategies
        """
    )
    
    parser.add_argument(
        "--strategy", "-s",
        default="trend_following",
        help="Trading-Strategie (default: trend_following)"
    )
    
    parser.add_argument(
        "--quality", "-q",
        type=float,
        default=0.85,
        help="Ziel-Qualität 0.0-1.0 (default: 0.85)"
    )
    
    parser.add_argument(
        "--iterations", "-i",
        type=int,
        default=20,
        help="Maximum Iterationen (default: 20)"
    )
    
    parser.add_argument(
        "--list-strategies",
        action="store_true",
        help="Zeigt verfügbare Strategien"
    )
    
    args = parser.parse_args()
    
    if args.list_strategies:
        print_strategies()
        return
    
    # Validierung
    if not 0.0 <= args.quality <= 1.0:
        print(f"{Fore.RED}❌ Qualität muss zwischen 0.0 und 1.0 liegen{Style.RESET_ALL}")
        sys.exit(1)
    
    if args.iterations < 1 or args.iterations > 100:
        print(f"{Fore.RED}❌ Iterationen müssen zwischen 1 und 100 liegen{Style.RESET_ALL}")
        sys.exit(1)
    
    # Generator starten
    asyncio.run(run_generator(
        strategy=args.strategy,
        target_quality=args.quality,
        max_iterations=args.iterations
    ))

if __name__ == "__main__":
    main()
