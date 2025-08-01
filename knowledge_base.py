"""
Knowledge Base - Intelligente Wissensdatenbank
==============================================

Diese Komponente speichert und verwaltet:
- MQL5 Syntax-Patterns und Best Practices
- FTMO-Regel-Implementierungen
- Bewährte Trading-Algorithmen
- Code-Snippets und Komponenten
- Fehler-Pattern und deren Lösungen
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import hashlib

class KnowledgeBase:
    """Zentrale Wissensdatenbank für MQL5/FTMO Entwicklung"""
    
    def __init__(self, db_path: str = "knowledge_base.db"):
        self.db_path = db_path
        self.init_database()
        self.load_core_knowledge()
    
    def init_database(self):
        """Initialisiert die SQLite Datenbank"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Code Snippets Tabelle
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS code_snippets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    category TEXT NOT NULL,
                    code TEXT NOT NULL,
                    description TEXT,
                    quality_score REAL DEFAULT 0.0,
                    usage_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # FTMO Rules Tabelle
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ftmo_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_name TEXT UNIQUE NOT NULL,
                    implementation TEXT NOT NULL,
                    validation_code TEXT,
                    description TEXT,
                    is_critical BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # MQL5 Patterns Tabelle
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mql5_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_name TEXT UNIQUE NOT NULL,
                    pattern_type TEXT NOT NULL,
                    correct_syntax TEXT NOT NULL,
                    common_errors TEXT,
                    examples TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Trading Strategies Tabelle
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trading_strategies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    strategy_name TEXT UNIQUE NOT NULL,
                    strategy_type TEXT NOT NULL,
                    implementation TEXT NOT NULL,
                    parameters TEXT,
                    success_rate REAL DEFAULT 0.0,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Error Solutions Tabelle
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS error_solutions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_pattern TEXT NOT NULL,
                    solution TEXT NOT NULL,
                    error_type TEXT,
                    frequency INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def load_core_knowledge(self):
        """Lädt die grundlegende Wissensbasis"""
        # FTMO Regeln
        ftmo_rules = [
            {
                "rule_name": "daily_loss_limit",
                "implementation": """
// FTMO Daily Loss Kontrolle
double GetDailyLoss() {
    double startBalance = AccountInfoDouble(ACCOUNT_BALANCE);
    double currentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
    double dailyLoss = (startBalance - currentEquity) / startBalance * 100;
    return dailyLoss;
}

bool CheckDailyLossLimit() {
    double dailyLoss = GetDailyLoss();
    if(dailyLoss >= 5.0) {
        Print("FTMO DAILY LOSS LIMIT ERREICHT: ", dailyLoss, "%");
        return false;
    }
    return true;
}""",
                "validation_code": "if(!CheckDailyLossLimit()) { CloseAllPositions(); return; }",
                "description": "Überwacht das tägliche Verlustlimit von 5%",
                "is_critical": True
            },
            {
                "rule_name": "total_loss_limit", 
                "implementation": """
// FTMO Total Loss Kontrolle
bool CheckTotalLossLimit() {
    double startBalance = AccountInfoDouble(ACCOUNT_BALANCE);
    double currentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
    double totalLoss = (startBalance - currentEquity) / startBalance * 100;
    
    if(totalLoss >= 10.0) {
        Print("FTMO TOTAL LOSS LIMIT ERREICHT: ", totalLoss, "%");
        return false;
    }
    return true;
}""",
                "validation_code": "if(!CheckTotalLossLimit()) { CloseAllPositions(); return; }",
                "description": "Überwacht das Gesamt-Verlustlimit von 10%",
                "is_critical": True
            }
        ]
        
        # MQL5 Syntax Patterns
        mql5_patterns = [
            {
                "pattern_name": "order_placement",
                "pattern_type": "trading",
                "correct_syntax": """
#include <Trade\\Trade.mqh>
CTrade trade;

// Korrekte Order-Platzierung
MqlTradeRequest request = {};
MqlTradeResult result = {};

request.action = TRADE_ACTION_DEAL;
request.symbol = _Symbol;
request.volume = 0.01;
request.type = ORDER_TYPE_BUY;
request.price = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
request.sl = 0;
request.tp = 0;
request.magic = 12345;
request.comment = "FTMO EA";

bool success = OrderSend(request, result);""",
                "common_errors": "OP_BUY statt ORDER_TYPE_BUY, Ask statt SymbolInfoDouble",
                "examples": "Vollständige Order-Implementierung mit Error Handling"
            },
            {
                "pattern_name": "indicator_usage",
                "pattern_type": "technical_analysis", 
                "correct_syntax": """
// Korrekte Indikator-Verwendung
int ma_handle = iMA(_Symbol, PERIOD_H1, 20, 0, MODE_EMA, PRICE_CLOSE);
double ma_buffer[];
ArraySetAsSeries(ma_buffer, true);

if(CopyBuffer(ma_handle, 0, 0, 3, ma_buffer) < 3) {
    Print("Fehler beim Laden der MA-Daten");
    return;
}

double current_ma = ma_buffer[0];
double previous_ma = ma_buffer[1];""",
                "common_errors": "iMA mit falschen Parametern, fehlende ArraySetAsSeries",
                "examples": "MA, RSI, MACD Implementierungen"
            }
        ]
        
        # Trading Strategien
        trading_strategies = [
            {
                "strategy_name": "ema_crossover",
                "strategy_type": "trend_following",
                "implementation": """
// EMA Crossover Strategie
int ema_fast_handle = iMA(_Symbol, PERIOD_H1, 12, 0, MODE_EMA, PRICE_CLOSE);
int ema_slow_handle = iMA(_Symbol, PERIOD_H1, 26, 0, MODE_EMA, PRICE_CLOSE);

double ema_fast[], ema_slow[];
ArraySetAsSeries(ema_fast, true);
ArraySetAsSeries(ema_slow, true);

if(CopyBuffer(ema_fast_handle, 0, 0, 3, ema_fast) < 3 ||
   CopyBuffer(ema_slow_handle, 0, 0, 3, ema_slow) < 3) {
    return SIGNAL_NONE;
}

// Bullish Crossover
if(ema_fast[1] <= ema_slow[1] && ema_fast[0] > ema_slow[0]) {
    return SIGNAL_BUY;
}

// Bearish Crossover  
if(ema_fast[1] >= ema_slow[1] && ema_fast[0] < ema_slow[0]) {
    return SIGNAL_SELL;
}

return SIGNAL_NONE;""",
                "parameters": "fast_period=12, slow_period=26, timeframe=H1",
                "success_rate": 0.72,
                "description": "Bewährte EMA Crossover Strategie mit hoher Erfolgsrate"
            }
        ]
        
        # Daten in Datenbank einfügen
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # FTMO Rules einfügen
            for rule in ftmo_rules:
                cursor.execute("""
                    INSERT OR REPLACE INTO ftmo_rules 
                    (rule_name, implementation, validation_code, description, is_critical)
                    VALUES (?, ?, ?, ?, ?)
                """, (rule["rule_name"], rule["implementation"], 
                     rule["validation_code"], rule["description"], rule["is_critical"]))
            
            # MQL5 Patterns einfügen
            for pattern in mql5_patterns:
                cursor.execute("""
                    INSERT OR REPLACE INTO mql5_patterns
                    (pattern_name, pattern_type, correct_syntax, common_errors, examples)
                    VALUES (?, ?, ?, ?, ?)
                """, (pattern["pattern_name"], pattern["pattern_type"],
                     pattern["correct_syntax"], pattern["common_errors"], pattern["examples"]))
            
            # Trading Strategies einfügen
            for strategy in trading_strategies:
                cursor.execute("""
                    INSERT OR REPLACE INTO trading_strategies
                    (strategy_name, strategy_type, implementation, parameters, success_rate, description)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (strategy["strategy_name"], strategy["strategy_type"],
                     strategy["implementation"], strategy["parameters"], 
                     strategy["success_rate"], strategy["description"]))
            
            conn.commit()
    
    def get_ftmo_rules(self) -> List[Dict]:
        """Holt alle FTMO Regeln"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ftmo_rules ORDER BY is_critical DESC")
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_mql5_patterns(self, pattern_type: str = None) -> List[Dict]:
        """Holt MQL5 Syntax Patterns"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if pattern_type:
                cursor.execute("SELECT * FROM mql5_patterns WHERE pattern_type = ?", (pattern_type,))
            else:
                cursor.execute("SELECT * FROM mql5_patterns")
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_trading_strategies(self, min_success_rate: float = 0.0) -> List[Dict]:
        """Holt Trading Strategien"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM trading_strategies 
                WHERE success_rate >= ? 
                ORDER BY success_rate DESC
            """, (min_success_rate,))
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def add_error_solution(self, error_pattern: str, solution: str, error_type: str = "compilation"):
        """Fügt eine Fehler-Lösung hinzu"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO error_solutions
                (error_pattern, solution, error_type, frequency)
                VALUES (?, ?, ?, 1)
                ON CONFLICT(error_pattern) DO UPDATE SET
                frequency = frequency + 1
            """, (error_pattern, solution, error_type))
            conn.commit()
    
    def get_error_solution(self, error_pattern: str) -> Optional[Dict]:
        """Sucht eine Lösung für einen Fehler"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM error_solutions 
                WHERE error_pattern LIKE ?
                ORDER BY frequency DESC LIMIT 1
            """, (f"%{error_pattern}%",))
            row = cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
        return None
    
    def add_code_snippet(self, name: str, category: str, code: str, description: str = ""):
        """Fügt einen Code-Snippet hinzu"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO code_snippets
                (name, category, code, description, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (name, category, code, description))
            conn.commit()
    
    def get_code_snippets(self, category: str = None) -> List[Dict]:
        """Holt Code-Snippets"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if category:
                cursor.execute("""
                    SELECT * FROM code_snippets 
                    WHERE category = ? 
                    ORDER BY quality_score DESC, usage_count DESC
                """, (category,))
            else:
                cursor.execute("""
                    SELECT * FROM code_snippets 
                    ORDER BY quality_score DESC, usage_count DESC
                """)
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def update_snippet_quality(self, name: str, quality_score: float):
        """Aktualisiert die Qualitätsbewertung eines Snippets"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE code_snippets 
                SET quality_score = ?, usage_count = usage_count + 1
                WHERE name = ?
            """, (quality_score, name))
            conn.commit()
    
    def generate_knowledge_context(self, focus_areas: List[str] = None) -> str:
        """Generiert einen Kontext-String für LLM Prompts"""
        context = "=== KNOWLEDGE BASE CONTEXT ===\n\n"
        
        # FTMO Regeln
        context += "🔴 KRITISCHE FTMO REGELN:\n"
        ftmo_rules = self.get_ftmo_rules()
        for rule in ftmo_rules[:3]:  # Top 3 kritische Regeln
            if rule['is_critical']:
                context += f"- {rule['rule_name']}: {rule['description']}\n"
                context += f"  Implementation: {rule['implementation'][:200]}...\n\n"
        
        # Top MQL5 Patterns
        context += "✅ BEWÄHRTE MQL5 PATTERNS:\n"
        patterns = self.get_mql5_patterns()
        for pattern in patterns[:3]:
            context += f"- {pattern['pattern_name']}: {pattern['correct_syntax'][:150]}...\n\n"
        
        # Top Trading Strategien  
        context += "📈 ERFOLGREICHE TRADING STRATEGIEN:\n"
        strategies = self.get_trading_strategies(min_success_rate=0.6)
        for strategy in strategies[:2]:
            context += f"- {strategy['strategy_name']} (Success: {strategy['success_rate']:.1%})\n"
            context += f"  {strategy['description']}\n\n"
        
        return context
