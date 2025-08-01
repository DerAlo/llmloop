"""
PHASE 3: Incremental Code-Fixing
===============================

Implementiert minimal-invasive Code-Änderungen mit Rollback-Funktionalität
"""

import difflib
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class CodeChange:
    """Repräsentiert eine einzelne Code-Änderung"""
    line_number: int
    old_content: str
    new_content: str
    change_type: str  # 'fix', 'add', 'remove'
    confidence: float  # 0.0-1.0

class IncrementalFixer:
    """Implementiert incremental code fixing mit minimalen Änderungen"""
    
    def __init__(self, max_changes_per_iteration: int = 5):
        self.max_changes_per_iteration = max_changes_per_iteration
        self.change_history = []
    
    def apply_minimal_fixes(self, original_code: str, priority_errors: List, templates: dict) -> tuple[str, List[CodeChange]]:
        """Wendet minimale Fixes basierend auf Prioritäts-Fehlern an"""
        
        lines = original_code.split('\n')
        changes = []
        
        # Fokussiere auf die top 3 Fehler
        for error in priority_errors[:3]:
            if len(changes) >= self.max_changes_per_iteration:
                break
                
            change = self._fix_single_error(lines, error, templates)
            if change:
                changes.append(change)
                # Wende die Änderung sofort an für folgende Fixes
                if change.change_type == 'fix':
                    lines[change.line_number] = change.new_content
                elif change.change_type == 'add':
                    lines.insert(change.line_number, change.new_content)
        
        # Rekonstruiere Code
        modified_code = '\n'.join(lines)
        
        return modified_code, changes
    
    def _fix_single_error(self, lines: List[str], error, templates: dict) -> Optional[CodeChange]:
        """Behebt einen einzelnen Fehler mit minimaler Änderung"""
        
        # Extrahiere Zeilennummer aus Fehlermeldung
        line_num = self._extract_line_number(error.original_message)
        if line_num is None or line_num >= len(lines):
            return None
        
        original_line = lines[line_num]
        
        # Spezifische Fixes basierend auf Fehler-Typ
        if error.error_type == 'missing_semicolon':
            return self._fix_missing_semicolon(line_num, original_line)
        elif error.error_type == 'missing_parenthesis':
            return self._fix_missing_parenthesis(line_num, original_line)
        elif error.error_type == 'deprecated_function':
            return self._fix_deprecated_function(line_num, original_line, templates)
        elif error.error_type == 'deprecated_variable':
            return self._fix_deprecated_variable(line_num, original_line, templates)
        elif error.error_type == 'wrong_parameters':
            return self._fix_wrong_parameters(line_num, original_line)
        
        return None
    
    def _extract_line_number(self, error_message: str) -> Optional[int]:
        """Extrahiert Zeilennummer aus Fehlermeldung"""
        import re
        match = re.search(r'\((\d+),\d+\)', error_message)
        if match:
            return int(match.group(1)) - 1  # Convert to 0-based index
        return None
    
    def _fix_missing_semicolon(self, line_num: int, original_line: str) -> CodeChange:
        """Behebt fehlende Semikolons"""
        new_line = original_line.rstrip() + ';'
        return CodeChange(
            line_number=line_num,
            old_content=original_line,
            new_content=new_line,
            change_type='fix',
            confidence=0.95
        )
    
    def _fix_missing_parenthesis(self, line_num: int, original_line: str) -> CodeChange:
        """Behebt fehlende Klammern"""
        # Simple heuristic: add ) at end if missing
        if original_line.count('(') > original_line.count(')'):
            new_line = original_line.rstrip() + ')'
            return CodeChange(
                line_number=line_num,
                old_content=original_line,
                new_content=new_line,
                change_type='fix',
                confidence=0.90
            )
        return None
    
    def _fix_deprecated_function(self, line_num: int, original_line: str, templates: dict) -> Optional[CodeChange]:
        """Behebt deprecated functions mit Templates"""
        
        from mql5_error_templates import MQL5ErrorTemplates
        
        new_line = original_line
        applied = False
        
        # Wende MarketInfo fixes an
        for old_func, new_func in MQL5ErrorTemplates.MARKETINFO_FIXES.items():
            if old_func in original_line:
                new_line = new_line.replace(old_func, new_func)
                applied = True
                break
        
        if applied:
            return CodeChange(
                line_number=line_num,
                old_content=original_line,
                new_content=new_line,
                change_type='fix',
                confidence=0.85
            )
        
        return None
    
    def _fix_deprecated_variable(self, line_num: int, original_line: str, templates: dict) -> Optional[CodeChange]:
        """Behebt deprecated variables (Ask, Bid, etc.)"""
        
        from mql5_error_templates import MQL5ErrorTemplates
        
        new_line = original_line
        applied = False
        
        # Wende Account fixes an
        for old_var, new_var in MQL5ErrorTemplates.ACCOUNT_FIXES.items():
            if old_var in original_line:
                new_line = new_line.replace(old_var, new_var)
                applied = True
                break
        
        if applied:
            return CodeChange(
                line_number=line_num,
                old_content=original_line,
                new_content=new_line,
                change_type='fix',
                confidence=0.80
            )
        
        return None
    
    def _fix_wrong_parameters(self, line_num: int, original_line: str) -> Optional[CodeChange]:
        """Behebt falsche Parameter-Anzahl (heuristic)"""
        
        # Simple heuristic für häufige Fälle
        if 'iMA(' in original_line and original_line.count(',') < 5:
            # iMA braucht 6 Parameter in MQL5
            new_line = original_line.replace('iMA(', 'iMA(_Symbol, _Period, ')
            return CodeChange(
                line_number=line_num,
                old_content=original_line,
                new_content=new_line,
                change_type='fix',
                confidence=0.70
            )
        
        return None
    
    def calculate_change_impact(self, original_code: str, modified_code: str) -> Dict[str, float]:
        """Berechnet den Impact der Änderungen"""
        
        original_lines = original_code.split('\n')
        modified_lines = modified_code.split('\n')
        
        # Berechne Ähnlichkeit
        matcher = difflib.SequenceMatcher(None, original_lines, modified_lines)
        similarity = matcher.ratio()
        
        # Zähle Änderungen
        changes = 0
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag != 'equal':
                changes += 1
        
        return {
            'similarity': similarity,
            'total_changes': changes,
            'change_ratio': changes / len(original_lines) if original_lines else 0,
            'lines_changed': len(modified_lines) - len(original_lines)
        }
    
    def should_rollback(self, impact: Dict[str, float], error_improvement: float) -> bool:
        """Entscheidet ob ein Rollback nötig ist"""
        
        # Rollback wenn:
        # 1. Zu viele Änderungen (>10% der Zeilen)
        # 2. Keine Fehler-Verbesserung trotz Änderungen
        # 3. Similarity zu niedrig (<95%)
        
        if impact['change_ratio'] > 0.10:
            return True
        
        if impact['similarity'] < 0.95 and error_improvement <= 0:
            return True
        
        return False
