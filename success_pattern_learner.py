"""
PHASE 4: Success Pattern Learning
================================

Lernt aus erfolgreichen Fixes und baut eine Template-Library auf
"""

import json
import os
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class SuccessPattern:
    """Repräsentiert ein erfolgreiches Fix-Muster"""
    pattern_id: str
    error_signature: str  # Eindeutige Signatur des Fehlers
    original_code_snippet: str
    fixed_code_snippet: str
    fix_type: str  # 'syntax', 'deprecated', 'logic'
    success_rate: float  # 0.0-1.0
    usage_count: int
    last_used: datetime
    confidence: float  # Wie sicher sind wir dass das Fix korrekt ist

class SuccessPatternLearner:
    """Lernt aus erfolgreichen Code-Fixes"""
    
    def __init__(self, pattern_file: str = "success_patterns.json"):
        self.pattern_file = pattern_file
        self.patterns: Dict[str, SuccessPattern] = {}
        self.load_patterns()
    
    def load_patterns(self):
        """Lädt gespeicherte Patterns"""
        if os.path.exists(self.pattern_file):
            try:
                with open(self.pattern_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for pattern_data in data:
                        pattern = SuccessPattern(**pattern_data)
                        self.patterns[pattern.pattern_id] = pattern
            except Exception as e:
                print(f"Fehler beim Laden der Patterns: {e}")
    
    def save_patterns(self):
        """Speichert aktuelle Patterns"""
        try:
            # Convert datetime to string for JSON serialization
            serializable_data = []
            for pattern in self.patterns.values():
                pattern_dict = asdict(pattern)
                pattern_dict['last_used'] = pattern.last_used.isoformat()
                serializable_data.append(pattern_dict)
            
            with open(self.pattern_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Fehler beim Speichern der Patterns: {e}")
    
    def learn_from_success(self, original_code: str, fixed_code: str, 
                          compilation_success: bool, error_messages: List[str]):
        """Lernt aus einem erfolgreichen Fix"""
        
        if not compilation_success:
            return  # Nur aus Erfolgen lernen
        
        # Extrahiere geänderte Bereiche
        changes = self._extract_changes(original_code, fixed_code)
        
        for change in changes:
            # Erstelle Pattern
            pattern = self._create_pattern(change, error_messages)
            if pattern:
                self._update_or_add_pattern(pattern)
        
        self.save_patterns()
    
    def _extract_changes(self, original: str, fixed: str) -> List[Dict]:
        """Extrahiert spezifische Änderungen zwischen Codes"""
        import difflib
        
        original_lines = original.split('\n')
        fixed_lines = fixed.split('\n')
        
        changes = []
        matcher = difflib.SequenceMatcher(None, original_lines, fixed_lines)
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                # Eine Zeile wurde geändert
                if i2 - i1 == 1 and j2 - j1 == 1:
                    changes.append({
                        'type': 'line_replace',
                        'original': original_lines[i1],
                        'fixed': fixed_lines[j1],
                        'line_number': i1
                    })
            elif tag == 'insert':
                # Zeilen wurden hinzugefügt
                for j in range(j1, j2):
                    changes.append({
                        'type': 'line_insert',
                        'original': '',
                        'fixed': fixed_lines[j],
                        'line_number': i1
                    })
        
        return changes
    
    def _create_pattern(self, change: Dict, error_messages: List[str]) -> Optional[SuccessPattern]:
        """Erstellt ein Pattern aus einer Änderung"""
        
        if change['type'] != 'line_replace':
            return None  # Fokus auf Line-Replacements
        
        original_line = change['original'].strip()
        fixed_line = change['fixed'].strip()
        
        if not original_line or not fixed_line:
            return None
        
        # Erstelle Error-Signatur
        error_signature = self._create_error_signature(original_line, error_messages)
        if not error_signature:
            return None
        
        pattern_id = f"{hash(error_signature)}_{hash(original_line)}"
        
        # Bestimme Fix-Type
        fix_type = self._determine_fix_type(original_line, fixed_line)
        
        return SuccessPattern(
            pattern_id=pattern_id,
            error_signature=error_signature,
            original_code_snippet=original_line,
            fixed_code_snippet=fixed_line,
            fix_type=fix_type,
            success_rate=1.0,  # Initial 100%
            usage_count=1,
            last_used=datetime.now(),
            confidence=0.8  # Initial confidence
        )
    
    def _create_error_signature(self, line: str, error_messages: List[str]) -> Optional[str]:
        """Erstellt eine eindeutige Signatur für den Fehlertyp"""
        
        # Suche nach spezifischen Fehlern in der Zeile
        signatures = []
        
        # MarketInfo Fehler
        if 'MarketInfo' in line:
            signatures.append('deprecated_marketinfo')
        
        # Order Konstanten
        if any(op in line for op in ['OP_BUY', 'OP_SELL', 'OP_BUYLIMIT']):
            signatures.append('deprecated_order_constant')
        
        # Account Variablen
        if any(var in line for var in ['Ask', 'Bid', 'Point', 'Digits']):
            signatures.append('deprecated_account_variable')
        
        # Syntax Fehler
        if any(msg in ' '.join(error_messages) for msg in ['expected', 'undeclared', 'syntax error']):
            if not line.endswith(';') and ('=' in line or 'return' in line):
                signatures.append('missing_semicolon')
            elif line.count('(') != line.count(')'):
                signatures.append('missing_parenthesis')
        
        return '_'.join(signatures) if signatures else None
    
    def _determine_fix_type(self, original: str, fixed: str) -> str:
        """Bestimmt den Typ des Fixes"""
        
        if 'MarketInfo' in original and 'SymbolInfo' in fixed:
            return 'deprecated_function'
        elif any(old in original for old in ['Ask', 'Bid', 'Point', 'Digits']):
            return 'deprecated_variable'
        elif original.rstrip() + ';' == fixed:
            return 'syntax_semicolon'
        elif original + ')' == fixed:
            return 'syntax_parenthesis'
        else:
            return 'unknown'
    
    def _update_or_add_pattern(self, new_pattern: SuccessPattern):
        """Aktualisiert existierendes Pattern oder fügt neues hinzu"""
        
        if new_pattern.pattern_id in self.patterns:
            # Aktualisiere existierendes Pattern
            existing = self.patterns[new_pattern.pattern_id]
            existing.usage_count += 1
            existing.last_used = datetime.now()
            
            # Aktualisiere Success Rate (exponential moving average)
            alpha = 0.1
            existing.success_rate = (1 - alpha) * existing.success_rate + alpha * 1.0
            
            # Erhöhe Confidence bei wiederholtem Erfolg
            existing.confidence = min(0.95, existing.confidence + 0.05)
        else:
            # Füge neues Pattern hinzu
            self.patterns[new_pattern.pattern_id] = new_pattern
    
    def get_applicable_patterns(self, error_messages: List[str], code_line: str) -> List[SuccessPattern]:
        """Gibt anwendbare Patterns für gegebene Fehler zurück"""
        
        applicable = []
        error_signature = self._create_error_signature(code_line, error_messages)
        
        if not error_signature:
            return applicable
        
        # Suche nach Patterns mit matching signature
        for pattern in self.patterns.values():
            if error_signature in pattern.error_signature:
                # Zusätzliche Ähnlichkeitsprüfung
                similarity = self._calculate_similarity(code_line, pattern.original_code_snippet)
                if similarity > 0.7:  # 70% Ähnlichkeit
                    applicable.append(pattern)
        
        # Sortiere nach Confidence und Success Rate
        applicable.sort(key=lambda p: p.confidence * p.success_rate, reverse=True)
        
        return applicable[:3]  # Top 3 Patterns
    
    def _calculate_similarity(self, line1: str, line2: str) -> float:
        """Berechnet Ähnlichkeit zwischen zwei Code-Zeilen"""
        import difflib
        
        # Normalisiere Zeilen (entferne Whitespace, Kommentare)
        norm1 = self._normalize_line(line1)
        norm2 = self._normalize_line(line2)
        
        return difflib.SequenceMatcher(None, norm1, norm2).ratio()
    
    def _normalize_line(self, line: str) -> str:
        """Normalisiert eine Code-Zeile für Vergleiche"""
        # Entferne führende/folgende Whitespaces
        normalized = line.strip()
        
        # Entferne Kommentare
        if '//' in normalized:
            normalized = normalized.split('//')[0].strip()
        
        # Entferne multiple Spaces
        import re
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return normalized
    
    def generate_learning_report(self) -> Dict:
        """Generiert einen Report über gelernte Patterns"""
        
        total_patterns = len(self.patterns)
        if total_patterns == 0:
            return {"message": "Keine Patterns gelernt"}
        
        # Statistiken
        fix_types = {}
        avg_success_rate = 0
        most_used = None
        max_usage = 0
        
        for pattern in self.patterns.values():
            # Fix Types
            fix_types[pattern.fix_type] = fix_types.get(pattern.fix_type, 0) + 1
            
            # Average Success Rate
            avg_success_rate += pattern.success_rate
            
            # Most Used
            if pattern.usage_count > max_usage:
                max_usage = pattern.usage_count
                most_used = pattern
        
        avg_success_rate /= total_patterns
        
        return {
            "total_patterns": total_patterns,
            "fix_types": fix_types,
            "average_success_rate": round(avg_success_rate, 3),
            "most_used_pattern": {
                "fix_type": most_used.fix_type if most_used else None,
                "usage_count": max_usage,
                "success_rate": round(most_used.success_rate, 3) if most_used else None
            }
        }
