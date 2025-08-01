"""
PHASE 2: Intelligente Fehler-Kategorisierung
===========================================

Kategorisiert Fehler nach Komplexität und implementiert priorisierte Behandlung
"""

import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Tuple

class ErrorComplexity(Enum):
    """Fehler-Komplexität Kategorien"""
    SIMPLE = 1      # Einfach zu beheben (Syntax, Missing semicolon)
    MEDIUM = 2      # Mittlere Komplexität (Logic errors, wrong parameters)
    COMPLEX = 3     # Hohe Komplexität (Architecture, missing functions)

@dataclass
class CategorizedError:
    """Kategorisierter Fehler mit Lösungsstrategie"""
    original_message: str
    error_type: str
    complexity: ErrorComplexity
    fix_strategy: str
    fix_template: str
    priority: int  # 1 = höchste Priorität

class ErrorCategorizer:
    """Intelligente Fehler-Kategorisierung und Priorisierung"""
    
    # Simple Syntax Errors (Priorität 1)
    SIMPLE_PATTERNS = {
        r"';' - semicolon expected": {
            'type': 'missing_semicolon',
            'strategy': 'Add missing semicolon',
            'template': 'Line {line}: Add ; at end of statement',
            'priority': 1
        },
        r"'\)' - \) expected": {
            'type': 'missing_parenthesis',
            'strategy': 'Add missing closing parenthesis',
            'template': 'Line {line}: Add ) to close function call',
            'priority': 1
        },
        r"'\}' - \} expected": {
            'type': 'missing_brace',
            'strategy': 'Add missing closing brace',
            'template': 'Line {line}: Add } to close block',
            'priority': 1
        },
        r"undeclared identifier": {
            'type': 'undeclared_variable',
            'strategy': 'Declare variable or fix typo',
            'template': 'Line {line}: Declare {variable} or check spelling',
            'priority': 2
        },
    }
    
    # Medium Complexity Errors (Priorität 3-5)
    MEDIUM_PATTERNS = {
        r"wrong parameters count": {
            'type': 'wrong_parameters',
            'strategy': 'Fix function parameters',
            'template': 'Line {line}: Check {function} parameter count',
            'priority': 3
        },
        r"'MarketInfo' - undeclared identifier": {
            'type': 'deprecated_function',
            'strategy': 'Replace with MQL5 equivalent',
            'template': 'Line {line}: Replace MarketInfo with SymbolInfo*',
            'priority': 3
        },
        r"'Ask'|'Bid' - undeclared identifier": {
            'type': 'deprecated_variable',
            'strategy': 'Replace with SymbolInfoDouble',
            'template': 'Line {line}: Replace Ask/Bid with SymbolInfoDouble',
            'priority': 3
        },
        r"'OP_BUY'|'OP_SELL' - undeclared identifier": {
            'type': 'deprecated_constant',
            'strategy': 'Replace with ORDER_TYPE_*',
            'template': 'Line {line}: Replace OP_* with ORDER_TYPE_*',
            'priority': 4
        },
    }
    
    # Complex Architecture Errors (Priorität 6-10)
    COMPLEX_PATTERNS = {
        r"'OnInit' - function not defined": {
            'type': 'missing_function',
            'strategy': 'Add missing OnInit function',
            'template': 'Add complete OnInit() function with proper initialization',
            'priority': 6
        },
        r"'OnTick' - function not defined": {
            'type': 'missing_function',
            'strategy': 'Add missing OnTick function',
            'template': 'Add complete OnTick() function with trading logic',
            'priority': 6
        },
        r"'CTrade' - undeclared identifier": {
            'type': 'missing_include',
            'strategy': 'Add Trade.mqh include and CTrade object',
            'template': 'Add #include <Trade\\\\Trade.mqh> and CTrade trade;',
            'priority': 7
        },
    }
    
    @classmethod
    def categorize_errors(cls, compilation_errors: List[str]) -> List[CategorizedError]:
        """Kategorisiert eine Liste von Compilation-Fehlern"""
        
        categorized = []
        
        for error_msg in compilation_errors:
            category = cls._categorize_single_error(error_msg)
            if category:
                categorized.append(category)
        
        # Sortiere nach Priorität (niedrigste Zahl = höchste Priorität)
        categorized.sort(key=lambda x: x.priority)
        
        return categorized
    
    @classmethod
    def _categorize_single_error(cls, error_msg: str) -> CategorizedError:
        """Kategorisiert einen einzelnen Fehler"""
        
        # Extrahiere Zeilennummer falls vorhanden
        line_match = re.search(r'\((\d+),\d+\)', error_msg)
        line_num = line_match.group(1) if line_match else 'unknown'
        
        # Prüfe Simple Patterns zuerst
        for pattern, info in cls.SIMPLE_PATTERNS.items():
            if re.search(pattern, error_msg, re.IGNORECASE):
                return CategorizedError(
                    original_message=error_msg,
                    error_type=info['type'],
                    complexity=ErrorComplexity.SIMPLE,
                    fix_strategy=info['strategy'],
                    fix_template=info['template'].format(line=line_num, variable='?', function='?'),
                    priority=info['priority']
                )
        
        # Prüfe Medium Patterns
        for pattern, info in cls.MEDIUM_PATTERNS.items():
            if re.search(pattern, error_msg, re.IGNORECASE):
                return CategorizedError(
                    original_message=error_msg,
                    error_type=info['type'],
                    complexity=ErrorComplexity.MEDIUM,
                    fix_strategy=info['strategy'],
                    fix_template=info['template'].format(line=line_num, function='?'),
                    priority=info['priority']
                )
        
        # Prüfe Complex Patterns
        for pattern, info in cls.COMPLEX_PATTERNS.items():
            if re.search(pattern, error_msg, re.IGNORECASE):
                return CategorizedError(
                    original_message=error_msg,
                    error_type=info['type'],
                    complexity=ErrorComplexity.COMPLEX,
                    fix_strategy=info['strategy'],
                    fix_template=info['template'],
                    priority=info['priority']
                )
        
        # Fallback für unbekannte Fehler
        return CategorizedError(
            original_message=error_msg,
            error_type='unknown',
            complexity=ErrorComplexity.MEDIUM,
            fix_strategy='Manual investigation required',
            fix_template=f'Line {line_num}: Check error manually',
            priority=8
        )
    
    @classmethod
    def get_priority_fix_plan(cls, categorized_errors: List[CategorizedError]) -> Dict[str, List[CategorizedError]]:
        """Erstellt einen priorisierten Fix-Plan"""
        
        plan = {
            'immediate': [],  # Priorität 1-2 (Simple)
            'short_term': [], # Priorität 3-5 (Medium)
            'long_term': []   # Priorität 6+ (Complex)
        }
        
        for error in categorized_errors:
            if error.priority <= 2:
                plan['immediate'].append(error)
            elif error.priority <= 5:
                plan['short_term'].append(error)
            else:
                plan['long_term'].append(error)
        
        return plan
    
    @classmethod
    def generate_focused_fix_instructions(cls, priority_errors: List[CategorizedError], max_fixes: int = 5) -> str:
        """Generiert fokussierte Fix-Anweisungen für die wichtigsten Fehler"""
        
        if not priority_errors:
            return "No prioritized errors found."
        
        instructions = []
        instructions.append("🎯 FOKUSSIERTE FEHLER-BEHEBUNG (Top Priorität):")
        instructions.append("=" * 50)
        
        for i, error in enumerate(priority_errors[:max_fixes], 1):
            instructions.append(f"\n{i}. {error.complexity.name} ERROR (Priority {error.priority}):")
            instructions.append(f"   Problem: {error.error_type}")
            instructions.append(f"   Strategy: {error.fix_strategy}")
            instructions.append(f"   Template: {error.fix_template}")
        
        instructions.append(f"\n⚡ FOKUS: Behebe NUR diese {min(len(priority_errors), max_fixes)} Fehler!")
        instructions.append("⚡ ÄNDERE NICHTS ANDERES!")
        instructions.append("⚡ EINE ITERATION = EIN FEHLER-TYP!")
        
        return '\n'.join(instructions)
