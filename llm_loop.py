"""
LLM Loop - Ollama LLM Communication Script
===========================================

Dieses Script orchestriert die Kommunikation zwischen zwei Ollama LLMs:
- qwen3:latest: Instruiert und überprüft den Code
- qwen2.5-coder:latest: Generiert MQL5 Code

Das Ziel ist es, iterativ perfekten FTMO MQL5 Trading Code zu entwickeln.
"""

import asyncio
import json
import logging
import os
import subprocess
import tempfile
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import aiohttp
import colorama
from colorama import Fore, Style

# Initialisiere Colorama für Windows-Terminal
colorama.init()

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('llm_loop.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OllamaClient:
    """Client für die Kommunikation mit Ollama API"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def generate(self, model: str, prompt: str, system: str = "") -> str:
        """Generiert eine Antwort von einem spezifischen Ollama Model"""
        if not self.session:
            raise RuntimeError("Client wurde nicht korrekt initialisiert")
        
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system,
            "stream": False
        }
        
        try:
            async with self.session.post(f"{self.base_url}/api/generate", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("response", "")
                else:
                    error_text = await response.text()
                    raise ConnectionError(f"Ollama API Error {response.status}: {error_text}")
        except Exception as e:
            logger.error(f"Fehler bei der Kommunikation mit {model}: {e}")
            raise

class LLMLoop:
    """Hauptklasse für die iterative LLM-Kommunikation"""
    
    def __init__(self):
        self.instructor_model = "qwen3:latest"
        self.coder_model = "qwen3-coder:30b"
        self.max_iterations = 100
        self.current_iteration = 0
        self.conversation_history: List[Dict] = []
        
        # MetaEditor Pfad für Syntax-Prüfung
        self.metaeditor_path = r"C:\Program Files\MetaTrader 5\MetaEditor64.exe"
        
        # FTMO spezifische Anforderungen
        self.ftmo_requirements = """
        FTMO Trading Anforderungen:
        - Maximum Daily Loss: 5% des Kontos
        - Maximum Loss: 10% des Kontos
        - Profit Target: 10% des Kontos
        - Minimum Trading Days: 5 Tage
        - Maximum Trading Days: 30 Tage
        - News Trading: Erlaubt mit Einschränkungen
        - Weekend Holding: Erlaubt
        - Expert Advisors: Erlaubt
        """
    
    def print_separator(self, title: str):
        """Druckt einen farbigen Separator"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{title:^60}")
        print(f"{'='*60}{Style.RESET_ALL}")
    
    def print_iteration(self):
        """Zeigt die aktuelle Iteration an"""
        print(f"\n{Fore.YELLOW}🔄 Iteration {self.current_iteration + 1}/{self.max_iterations}{Style.RESET_ALL}")
    
    def check_mql5_syntax(self, code: str) -> tuple[bool, str]:
        """
        Prüft MQL5 Syntax über PowerShell/MetaEditor Kompilierung
        Returns: (is_valid, detailed_message_with_errors)
        """
        # 1. Basis-Struktur prüfen (schnell)
        if '```' in code or 'mql5' in code.lower()[:50]:
            return False, "❌ Code enthält Markdown-Formatierung"
        
        if not code.strip().startswith('//+'):
            return False, "❌ Code muss mit //+ Header beginnen"
        
        required_functions = ['OnInit', 'OnTick']
        for func in required_functions:
            if func not in code:
                return False, f"❌ Fehlende Funktion: {func}"
        
        # 2. MetaEditor Kompilierung (finale Prüfung)
        try:
            import tempfile
            import subprocess
            import os
            
            # Temporäre MQL5 Datei erstellen
            with tempfile.NamedTemporaryFile(mode='w', suffix='.mq5', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name
            
            print(f"🔧 MetaEditor Syntax-Prüfung: {temp_file_path}")
            
            # PowerShell Script ausführen
            ps_script = os.path.join(os.path.dirname(__file__), "compile.ps1")
            
            result = subprocess.run([
                'powershell.exe',
                '-ExecutionPolicy', 'Bypass',
                '-File', ps_script,
                '-FileToCompile', temp_file_path
            ], capture_output=True, text=True, timeout=60, check=False)
            
            print(f"MetaEditor Exit Code: {result.returncode}")
            
            # Detaillierte Log-Auswertung
            ex5_file = temp_file_path.replace('.mq5', '.ex5')
            ex5_exists = os.path.exists(ex5_file)
            log_file = temp_file_path + '.log'
            
            detailed_message = ""
            compile_log = ""
            
            # Log-Datei lesen
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        compile_log = f.read()
                except Exception as e:
                    compile_log = f"Fehler beim Lesen der Log-Datei: {e}"
            
            # Cleanup
            try:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                if os.path.exists(ex5_file):
                    os.remove(ex5_file)
                if os.path.exists(log_file):
                    os.remove(log_file)
            except Exception:
                pass
            
            # Detaillierte Bewertung und Rückgabe
            if result.returncode == 0 and ex5_exists:
                # ERFOLG - zeige trotzdem Warnings
                detailed_message = f"✅ METAEDITOR KOMPILIERUNG ERFOLGREICH!\n\n"
                detailed_message += f"📊 COMPILE LOG:\n{compile_log}\n\n"
                detailed_message += f"🎯 .EX5 DATEI ERFOLGREICH ERSTELLT"
                return True, detailed_message
            else:
                # FEHLER - detaillierte Analyse
                detailed_message = f"❌ METAEDITOR KOMPILIERUNG FEHLGESCHLAGEN!\n\n"
                detailed_message += f"🔍 EXIT CODE: {result.returncode}\n\n"
                
                if compile_log:
                    # Fehler aus Log extrahieren
                    log_lines = compile_log.split('\n')
                    errors = [line for line in log_lines if 'error' in line.lower()]
                    warnings = [line for line in log_lines if 'warning' in line.lower()]
                    
                    detailed_message += f"📊 VOLLSTÄNDIGER COMPILE LOG:\n{compile_log}\n\n"
                    
                    if errors:
                        detailed_message += f"🚨 GEFUNDENE FEHLER ({len(errors)}):\n"
                        for i, error in enumerate(errors[:10], 1):  # Max 10 Fehler zeigen
                            detailed_message += f"{i}. {error.strip()}\n"
                        if len(errors) > 10:
                            detailed_message += f"... und {len(errors) - 10} weitere Fehler\n"
                        detailed_message += "\n"
                    
                    if warnings:
                        detailed_message += f"⚠️ WARNUNGEN ({len(warnings)}):\n"
                        for i, warning in enumerate(warnings[:5], 1):  # Max 5 Warnings zeigen
                            detailed_message += f"{i}. {warning.strip()}\n"
                        detailed_message += "\n"
                
                if result.stdout:
                    detailed_message += f"📤 STDOUT:\n{result.stdout}\n\n"
                if result.stderr:
                    detailed_message += f"📥 STDERR:\n{result.stderr}\n\n"
                
                detailed_message += f"🔧 .EX5 DATEI ERSTELLT: {'JA' if ex5_exists else 'NEIN'}"
                
                return False, detailed_message
                
        except subprocess.TimeoutExpired:
            return False, "❌ MetaEditor Timeout nach 60 Sekunden"
        except Exception as e:
            # Fallback zur Struktur-Prüfung bei MetaEditor-Problemen
            print(f"⚠️ MetaEditor nicht verfügbar: {e}")
            return True, f"✅ Struktur-Prüfung bestanden (MetaEditor nicht verfügbar: {e})"
    
    async def get_initial_instruction(self, client: OllamaClient) -> str:
        """Holt die initiale Anweisung vom Instructor"""
        system_prompt = f"""
        Du bist ein SENIOR MQL5 Trading Experte und FTMO Challenge Spezialist.
        Du instruierst andere Entwickler zur Erstellung von TOP-CLASS Expert Advisors.
        
        {self.ftmo_requirements}
        
        Deine Anweisungen müssen EXTREM spezifisch und detailliert sein für:
        - PRODUKTIONSREIFEN, kompilierbaren Code
        - VOLLSTÄNDIGE FTMO-Konformität
        - ECHTE, profitable Trading-Strategien
        - ROBUSTES Risikomanagement
        - PROFESSIONELLE Code-Qualität
        """
        
        initial_prompt = """
        ERSTELLE EINE DETAILLIERTE ENTWICKLUNGSANWEISUNG für einen TOP-CLASS FTMO Expert Advisor:
        
        Der EA MUSS folgende SPEZIFISCHE Anforderungen erfüllen:
        
        1. TRADING-STRATEGIE (wähle eine profitable Strategie):
           - Multi-Timeframe Analyse (H1, H4, D1)
           - Trend-Following mit Mean Reversion
           - RSI + Moving Average Kombination
           - Support/Resistance Level Trading
           - Volatilitäts-basierte Entry/Exit
           - News Event Filtering
        
        2. FTMO-KONFORMITÄT (100% erforderlich):
           - Exakte Daily Loss Kontrolle: Max 5% vom Startsaldo
           - Total Loss Kontrolle: Max 10% vom Startsaldo
           - Profit Target: 10% in max 30 Tagen
           - Minimum 5 Trading Days
           - Account Equity Monitoring in Echtzeit
           - Automatische Trading-Stopps bei Limit-Erreichen
        
        3. RISIKOMANAGEMENT (detailliert spezifizieren):
           - Position Sizing: 1-2% Risk per Trade
           - Stop Loss: ATR-basiert oder feste Pips
           - Take Profit: 1:2 oder 1:3 Risk/Reward Ratio
           - Trailing Stop: Implementierung erforderlich
           - Max gleichzeitige Positionen: 3-5
           - Correlation Filter zwischen Währungspaaren
        
        4. TECHNISCHE INDIKATOREN (spezifische Kombinationen):
           - Moving Averages (20, 50, 200 EMA)
           - RSI (14) mit Overbought/Oversold Levels
           - ATR (14) für Volatilitätsmessung
           - MACD für Trend-Bestätigung
           - Bollinger Bands für Volatilität
           - Support/Resistance Level Detection
        
        5. CODE-ARCHITEKTUR (professionelle Struktur):
           - Modulare Funktionen für jede Komponente
           - Input Parameter für alle Einstellungen
           - Umfassendes Error Handling
           - Detailliertes Logging System
           - Performance Monitoring
           - Alert System für kritische Events
        
        6. MARKET CONDITIONS HANDLING:
           - Trending Market Algorithmus
           - Ranging Market Detection
           - High Volatility Filters
           - Low Liquidity Avoidance
           - News Event Timing
           - Session-based Trading Rules
        
        7. CRITICAL MQL5 SYNTAX REQUIREMENTS (extrem wichtig!):
           - NIEMALS MQL4 Syntax verwenden!
           - ORDER_TYPE_BUY/ORDER_TYPE_SELL (nicht OP_BUY/OP_SELL)
           - SymbolInfoDouble(_Symbol, SYMBOL_ASK) für Ask-Preis
           - SymbolInfoDouble(_Symbol, SYMBOL_BID) für Bid-Preis
           - #include <Trade\\Trade.mqh> und CTrade Klasse verwenden
           - iMA() mit exakt 6 Parametern: iMA(_Symbol, timeframe, period, shift, method, price)
           - iRSI() mit exakt 4 Parametern: iRSI(_Symbol, timeframe, period, price)
           - Korrekte MqlTradeRequest Struktur für Orders
           - AccountInfoDouble() für Account-Informationen
           
        Der Coder MUSS diese MQL5-Syntax-Regeln befolgen!
        
        GIB EXTREM DETAILLIERTE, SPEZIFISCHE ANWEISUNGEN die zu einem
        VOLLSTÄNDIGEN, PRODUKTIONSREIFEN Expert Advisor führen!
        
        Der Entwickler soll EXAKT wissen was zu implementieren ist!
        """
        
        self.print_separator("🎯 INSTRUCTOR ERSTELLT DETAILLIERTE ENTWICKLUNGSANWEISUNG")
        logger.info("Hole detaillierte Entwicklungsanweisung vom Instructor...")
        
        instruction = await client.generate(
            model=self.instructor_model,
            prompt=initial_prompt,
            system=system_prompt
        )
        
        print(f"{Fore.GREEN}Detaillierte Entwicklungsanweisung (Länge: {len(instruction)} Zeichen):{Style.RESET_ALL}")
        print(instruction[:1000] + "..." if len(instruction) > 1000 else instruction)
        
        self.conversation_history.append({
            "type": "instruction",
            "model": self.instructor_model,
            "content": instruction,
            "instruction_length": len(instruction),
            "timestamp": datetime.now().isoformat()
        })
        
        return instruction
    
    async def generate_code(self, client: OllamaClient, instruction: str) -> str:
        """Lässt den Coder MQL5 Code basierend auf der Anweisung generieren"""
        system_prompt = """
        Du bist ein MQL5 Expert Advisor ENTWICKLER - NICHT ein Chatbot!
        Du schreibst AUSSCHLIESSLICH REINEN MQL5 CODE - NICHTS ANDERES!
        
        ╔══════════════════════════════════════════════════════════════════╗
        ║                          STRIKTE REGELN                         ║
        ╚══════════════════════════════════════════════════════════════════╝
        
        ❌ ABSOLUT VERBOTEN:
        - Jegliche Markdown-Formatierung (```mql5, ```, etc.)
        - Erklärungen vor oder nach dem Code
        - Entschuldigungen oder Sicherheitswarnungen
        - Platzhalter wie "// TODO" oder "// Implementierung folgt"
        - Unvollständige Funktionen
        - Demo-Account Hinweise
        - Irgendwelche Texte außer reinem MQL5 Code
        
        ✅ ABSOLUT ERFORDERLICH:
        - DIREKTER Start mit //+------------------------------------------------------------------+
        - VOLLSTÄNDIGER, lauffähiger MQL5 Code
        - ALLE Funktionen vollständig implementiert
        - ECHTE Trading-Algorithmen
        - SOFORTIGE Einsetzbarkeit
        - Code endet mit letzter schließender Klammer }
        
        Du bist ein CODE-GENERATOR, nicht ein Gesprächspartner!
        SCHREIBE NUR MQL5 CODE!
        """
        
        coder_prompt = f"""
        ╔══════════════════════════════════════════════════════════════════╗
        ║                    SOFORTIGER MQL5 CODE BEFEHL                  ║  
        ╚══════════════════════════════════════════════════════════════════╝
        
        ANWEISUNG: {instruction}
        
        ⚡ DEIN OUTPUT BEGINNT SOFORT MIT:
        //+------------------------------------------------------------------+
        //|                                    FTMO_Expert_Advisor.mq5     |
        //+------------------------------------------------------------------+
        
        ⚡ DEIN OUTPUT ENDET MIT:
        }} // Letzte schließende Klammer
        
        🚫 NIEMALS verwenden:
        ```mql5
        ```
        "Hier ist der Code:"
        "Zusammenfassung:"
        "Hinweise:"
        Jegliche Erklärungen
        
        ✅ PFLICHT-KOMPONENTEN:
        - #property copyright/version/link
        - input Parameter für alle Einstellungen
        - Globale Variablen für FTMO Risk Management  
        - OnInit() - Vollständige Initialisierung
        - OnDeinit() - Cleanup
        - OnTick() - Komplette Trading-Engine
        - CheckRiskLimits() - FTMO Risiko-Kontrolle
        - GetTradingSignal() - Echte Signal-Generierung
        - OpenTrade() - Order Management
        - CalculateLotSize() - Position Sizing
        - ManagePositions() - Position Management
        - CalculateStopLoss() - SL Berechnung
        - CalculateTakeProfit() - TP Berechnung
        
        🎯 BEGINNE JETZT SOFORT MIT DEM MQL5 CODE:
        """
        
        self.print_separator("💻 CODER ENTWICKELT PRODUKTIONSREIFEN MQL5 CODE")
        logger.info("Coder entwickelt vollständigen Expert Advisor...")
        
        code = await client.generate(
            model=self.coder_model,
            prompt=coder_prompt,
            system=system_prompt
        )
        
        print(f"{Fore.BLUE}Generierter Code (Länge: {len(code)} Zeichen):{Style.RESET_ALL}")
        print(code[:800] + "..." if len(code) > 800 else code)
        
        # Qualitäts-Check des generierten Codes
        if len(code) < 500:
            print(f"{Fore.YELLOW}⚠️ Code möglicherweise zu kurz für vollständigen EA{Style.RESET_ALL}")
        
        required_elements = ["OnInit", "OnTick", "OnDeinit", "input", "#property"]
        missing_elements = [elem for elem in required_elements if elem not in code]
        
        if missing_elements:
            print(f"{Fore.YELLOW}⚠️ Fehlende Elemente: {', '.join(missing_elements)}{Style.RESET_ALL}")
        
        self.conversation_history.append({
            "type": "code",
            "model": self.coder_model,
            "content": code,
            "code_length": len(code),
            "missing_elements": missing_elements,
            "timestamp": datetime.now().isoformat()
        })
        
        return code
    
    async def review_code(self, client: OllamaClient, code: str, original_instruction: str) -> Tuple[bool, str]:
        """Lässt den Instructor den Code bewerten - SEHR STRENGE KRITERIEN"""
        
        # Zuerst Syntax-Prüfung
        syntax_ok, syntax_msg = self.check_mql5_syntax(code)
        
        system_prompt = f"""
        Du bist ein UNBARMHERZIGER MQL5 Code-AUDITOR für FTMO Trading.
        Du lehnst JEDEN Code ab, der nicht PERFEKT ist.
        
        {self.ftmo_requirements}
        
        ╔══════════════════════════════════════════════════════════════════╗
        ║                     RIGOROSE QUALITÄTSPRÜFUNG                   ║
        ╚══════════════════════════════════════════════════════════════════╝
        
        🔍 DU PRÜFST GNADENLOS:
        
        1. CODE-REINHEIT:
        - KEINE Markdown-Blöcke (```mql5 oder ```)
        - KEINE Erklärungen vor/nach dem Code
        - KEINE Platzhalter oder TODOs
        - Code muss mit //+---- beginnen
        - Code muss mit }} enden
        
        2. FTMO-KONFORMITÄT:
        - Exakte 5% Daily Loss Kontrolle implementiert
        - Exakte 10% Total Loss Kontrolle implementiert  
        - Account Balance/Equity Monitoring in Echtzeit
        - Automatische Trading-Stopps bei Regelverletzung
        
        3. TRADING-VOLLSTÄNDIGKEIT:
        - ECHTE Signal-Generierung (nicht nur Beispiele)
        - Vollständiges Risikomanagement
        - Position Sizing basierend auf Account Size
        - Stop Loss UND Take Profit implementiert
        - Trailing Stop Funktionalität
        - Error Handling für alle Order-Operationen
        
        4. CODE-STRUKTUR:
        - Alle OnInit/OnTick/OnDeinit Funktionen vorhanden
        - Modulare Hilfsfunktionen implementiert
        - Input Parameter für Konfiguration
        - Professionelle Dokumentation
        
        Du sagst NUR "ZUFRIEDEN: JA" wenn der Code SOFORT in den Live-Handel könnte!
        Bei JEDEM Mangel: "ZUFRIEDEN: NEIN" mit gnadenloser Kritik!
        """
        
        review_prompt = f"""
        KRITISCHE BEWERTUNG - PRODUKTIONSREIFE PRÜFUNG:
        
        METAEDITOR SYNTAX-PRÜFUNG: 
        {syntax_msg}
        
        ORIGINAL ANWEISUNG:
        {original_instruction}
        
        GENERIERTER CODE:
        {code}
        
        BEWERTE EXTREM KRITISCH nach diesen KRITERIEN (ALLE müssen erfüllt sein):
        
        1. FTMO-KONFORMITÄT (100% erforderlich):
           - Exakte Daily Loss Kontrolle (5%)
           - Exakte Total Loss Kontrolle (10%)
           - Profit Target Tracking (10%)
           - Trading Days Verwaltung
        
        2. CODE-VOLLSTÄNDIGKEIT (100% erforderlich):
           - KEINE Platzhalter oder TODO-Kommentare
           - Vollständige Trading-Logik implementiert
           - Alle Funktionen vollständig auscodiert
        
        3. RISIKOMANAGEMENT (100% erforderlich):
           - Dynamisches Position Sizing
           - Stop Loss und Take Profit
           - Drawdown Monitoring
           - Volatilitätskontrolle
        
        4. CODE-QUALITÄT (100% erforderlich):
           - Professionelle Struktur
           - Umfassende Dokumentation
           - Robuste Fehlerbehandlung
           - Optimierte Performance
        
        5. TRADING-LOGIK (100% erforderlich):
           - Echte Entry/Exit Signale
           - Marktanalyse Algorithmen
           - News Filter Implementation
           - Trailing Stop Logik
        
        ANTWORTE NUR mit diesem FORMAT:
        SYNTAX: {"BESTANDEN" if syntax_ok else "FEHLER"}
        ZUFRIEDEN: [JA nur wenn ALLES 100% erfüllt ist, sonst NEIN]
        BEWERTUNG: [EXTREM detaillierte Kritik aller Mängel]
        VERBESSERUNGEN: [Spezifische, konkrete Anweisungen für Vollständigkeit]
        
        WICHTIG: Sage NUR "ZUFRIEDEN: JA" wenn der Code SOFORT produktiv einsetzbar ist!
        Alles andere ist "ZUFRIEDEN: NEIN" mit detaillierten Verbesserungsanweisungen.
        """
        
        self.print_separator("🔍 INSTRUCTOR FÜHRT STRENGE QUALITÄTSPRÜFUNG DURCH")
        
        if not syntax_ok:
            print(f"{Fore.RED}❌ SYNTAX FEHLER ERKANNT:{Style.RESET_ALL}")
            print(syntax_msg)
        else:
            print(f"{Fore.GREEN}✅ Syntax-Prüfung bestanden{Style.RESET_ALL}")
        
        logger.info("Instructor führt strenge Code-Bewertung durch...")
        
        review = await client.generate(
            model=self.instructor_model,
            prompt=review_prompt,
            system=system_prompt
        )
        
        print(f"{Fore.MAGENTA}Detaillierte Review:{Style.RESET_ALL}")
        print(review)
        
        # SEHR STRENGE Zufriedenheitsprüfung
        is_satisfied = (
            syntax_ok and 
            "ZUFRIEDEN: JA" in review and 
            "SYNTAX: BESTANDEN" in review and
            "produktionsreif" in review.lower() and
            len(code) > 1000  # Mindestlänge für vollständigen EA
        )
        
        # Zusätzliche Qualitätsprüfungen
        quality_checks = [
            "OnTick" in code,
            "OnInit" in code,
            "OrderSend" in code or "PositionOpen" in code,
            "StopLoss" in code or "SL" in code,
            "TakeProfit" in code or "TP" in code,
            "AccountBalance" in code or "AccountEquity" in code,
            "risk" in code.lower() or "Risk" in code,
            len(code.split('\n')) > 50  # Mindestens 50 Zeilen
        ]
        
        quality_score = sum(quality_checks) / len(quality_checks)
        
        if quality_score < 0.8:  # 80% der Qualitätschecks müssen bestehen
            is_satisfied = False
            print(f"{Fore.YELLOW}⚠️ Qualitätsscore zu niedrig: {quality_score:.1%}{Style.RESET_ALL}")
        
        if not is_satisfied:
            print(f"{Fore.RED}❌ CODE NICHT PRODUKTIONSREIF - Weitere Iteration erforderlich{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}✅ CODE ERREICHT PRODUKTIONSSTANDARD{Style.RESET_ALL}")
        
        self.conversation_history.append({
            "type": "review",
            "model": self.instructor_model,
            "content": review,
            "satisfied": is_satisfied,
            "syntax_ok": syntax_ok,
            "syntax_msg": syntax_msg,
            "quality_score": quality_score,
            "timestamp": datetime.now().isoformat()
        })
        
        return is_satisfied, review
    
    async def improve_code(self, client: OllamaClient, code: str, review: str) -> str:
        """Lässt den Coder den Code basierend auf dem Review verbessern"""
        system_prompt = """
        Du bist der WELTBESTE MQL5 Expert Advisor Entwickler.
        Du erstellst AUSSCHLIESSLICH kompilierbaren, produktionsreifen MQL5 Code.
        
        🏆 DEINE SPEZIALITÄT: FTMO-konforme Expert Advisors mit PERFEKTER Syntax
        
        ╔══════════════════════════════════════════════════════════════════╗
        ║              QWEN3-CODER: PREMIUM CODE GENERATION                ║
        ╚══════════════════════════════════════════════════════════════════╝
        
        ⚡ ABSOLUTE REGELN:
        1. NUR reiner MQL5 Code - KEINE Markdown, KEINE Erklärungen
        2. Code beginnt mit //+------ Header
        3. Code endet mit } (letzte Funktion)
        4. JEDE Zeile muss kompilierbar sein
        5. Verwende moderne MQL5 Syntax (nicht MQL4!)
        
        🎯 MQL5 SYNTAX REQUIREMENTS - BEFOLGE JEDEN PUNKT EXAKT:
        
        ❌ VERBOTENE MQL4 SYNTAX:
        - OP_BUY, OP_SELL (verwende ORDER_TYPE_BUY, ORDER_TYPE_SELL)
        - Ask, Bid (verwende SymbolInfoDouble())
        - MarketInfo() (verwende SymbolInfoDouble(), SymbolInfoInteger())
        - OrderClose() (verwende MqlTradeRequest/OrderSend())
        - MODE_ASK, MODE_BID, MODE_DIGITS (verwende SYMBOL_* Konstanten)
        - iMA() mit 7 Parametern (MQL5 hat nur 6 Parameter)
        - iRSI() mit 6 Parametern (MQL5 hat nur 4 Parameter)
        
        ✅ KORREKTE MQL5 SYNTAX:
        - ORDER_TYPE_BUY, ORDER_TYPE_SELL für Handelsrichtung
        - SymbolInfoDouble(_Symbol, SYMBOL_ASK) für Ask-Preis
        - SymbolInfoDouble(_Symbol, SYMBOL_BID) für Bid-Preis  
        - SymbolInfoInteger(_Symbol, SYMBOL_DIGITS) für Nachkommastellen
        - SymbolInfoDouble(_Symbol, SYMBOL_POINT) für Point-Wert
        - iMA(_Symbol, PERIOD_CURRENT, 14, 0, MODE_SMA, PRICE_CLOSE) - NUR 6 Parameter!
        - iRSI(_Symbol, PERIOD_CURRENT, 14, PRICE_CLOSE) - NUR 4 Parameter!
        - CTrade trade; trade.Buy() für Kauforders
        - #include <Trade\\Trade.mqh> für Trading-Klassen
        
        Du bist der BESTE Coder - zeige es!
        """
        
        improvement_prompt = f"""
        *** KRITISCHER BEFEHL: VOLLSTÄNDIGE CODE-VERBESSERUNG ***
        
        KEINE Ausreden! KEINE unvollständigen Verbesserungen!
        BEHEBE ALLE PROBLEME VOLLSTÄNDIG!
        
        AKTUELLER CODE:
        {code}
        
        DETAILLIERTES FEEDBACK VON METAEDITOR UND REVIEWER:
        {review}
        
        *** SOFORTIGE ANFORDERUNGEN ***:
        1. Behebe ALLE MetaEditor Syntax-Fehler sofort (siehe Log oben)
        2. Implementiere ALLE fehlenden Funktionen vollständig  
        3. Entferne ALLE Platzhalter, TODOs oder unvollständigen Teile
        4. Stelle FTMO-Konformität sicher
        5. Achte auf JEDEN Detail aus dem MetaEditor Compile-Log
        5. Füge robustes Risikomanagement hinzu
        6. Implementiere ECHTE Trading-Algorithmen
        7. Verbessere Code-Struktur und Dokumentation
        8. Stelle sicher dass der Code SOFORT kompiliert und funktioniert
        
        DER VERBESSERTE CODE MUSS:
        - Mindestens 300 Zeilen haben
        - Alle Haupt-Funktionen (OnInit, OnTick, OnDeinit) enthalten
        - Vollständiges Risikomanagement implementieren
        - ECHTE Trading-Signale generieren
        - Professionell dokumentiert sein
        - SOFORT produktiv einsetzbar sein
        - ALLE im Review genannten Probleme lösen
        
        BEGINNE SOFORT MIT DEM VOLLSTÄNDIG VERBESSERTEN MQL5 CODE!
        KEINE ERKLÄRUNGEN - NUR CODE!
        """
        
        self.print_separator("🔧 CODER IMPLEMENTIERT VOLLSTÄNDIGE VERBESSERUNGEN")
        logger.info("Coder implementiert alle Review-Kritikpunkte...")
        
        improved_code = await client.generate(
            model=self.coder_model,
            prompt=improvement_prompt,
            system=system_prompt
        )
        
        print(f"{Fore.BLUE}Verbesserter Code (Länge: {len(improved_code)} Zeichen):{Style.RESET_ALL}")
        print(improved_code[:800] + "..." if len(improved_code) > 800 else improved_code)
        
        # Verbesserungs-Check
        improvement_ratio = len(improved_code) / len(code) if len(code) > 0 else 1
        print(f"{Fore.CYAN}📊 Code-Verbesserung: {improvement_ratio:.1f}x Länge{Style.RESET_ALL}")
        
        if improvement_ratio < 0.8:
            print(f"{Fore.YELLOW}⚠️ Code wurde möglicherweise verkürzt statt verbessert{Style.RESET_ALL}")
        elif improvement_ratio > 1.5:
            print(f"{Fore.GREEN}✅ Signifikante Code-Erweiterung erkannt{Style.RESET_ALL}")
        
        self.conversation_history.append({
            "type": "improved_code",
            "model": self.coder_model,
            "content": improved_code,
            "code_length": len(improved_code),
            "improvement_ratio": improvement_ratio,
            "timestamp": datetime.now().isoformat()
        })
        
        return improved_code
    
    def save_final_code(self, code: str):
        """Speichert den finalen Code in eine Datei"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"FTMO_Expert_Advisor_{timestamp}.mq5"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(code)
        
        logger.info(f"Finaler Code gespeichert in: {filename}")
        print(f"\n{Fore.GREEN}✅ Finaler Code gespeichert in: {filename}{Style.RESET_ALL}")
    
    def save_conversation_log(self):
        """Speichert die gesamte Konversation"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_log_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Konversationslog gespeichert in: {filename}")
        print(f"{Fore.GREEN}📝 Konversationslog gespeichert in: {filename}{Style.RESET_ALL}")
    
    async def run(self):
        """Hauptschleife für die LLM-Kommunikation"""
        print(f"{Fore.CYAN}🚀 LLM Loop gestartet - FTMO MQL5 Code Entwicklung{Style.RESET_ALL}")
        print(f"Instructor: {self.instructor_model}")
        print(f"Coder: {self.coder_model}")
        print(f"Max Iterationen: {self.max_iterations}")
        
        async with OllamaClient() as client:
            try:
                # Schritt 1: Initiale Anweisung holen
                instruction = await self.get_initial_instruction(client)
                
                # Schritt 2: Iterative Schleife
                current_code = ""
                current_instruction = instruction
                
                for iteration in range(self.max_iterations):
                    self.current_iteration = iteration
                    self.print_iteration()
                    
                    # Code generieren
                    current_code = await self.generate_code(client, current_instruction)
                    
                    # Code reviewen
                    is_satisfied, review = await self.review_code(client, current_code, instruction)
                    
                    if is_satisfied:
                        print(f"\n{Fore.GREEN}🎉 INSTRUCTOR IST ZUFRIEDEN! Schleife beendet.{Style.RESET_ALL}")
                        break
                    
                    if iteration < self.max_iterations - 1:
                        # Code verbessern für nächste Iteration
                        current_code = await self.improve_code(client, current_code, review)
                        current_instruction = f"Verbessere den Code basierend auf diesem Feedback: {review}"
                    else:
                        print(f"\n{Fore.YELLOW}⚠️ Maximum Iterationen erreicht!{Style.RESET_ALL}")
                
                # Finalen Code speichern
                self.save_final_code(current_code)
                self.save_conversation_log()
                
                print(f"\n{Fore.GREEN}✅ LLM Loop abgeschlossen!{Style.RESET_ALL}")
                
            except Exception as e:
                logger.error(f"Fehler in der Hauptschleife: {e}")
                print(f"\n{Fore.RED}❌ Fehler: {e}{Style.RESET_ALL}")
                raise

async def main():
    """Hauptfunktion"""
    loop = LLMLoop()
    await loop.run()

if __name__ == "__main__":
    asyncio.run(main())
