"""
Code Evolution Tracker - Intelligente Code-Versionierung
========================================================

Diese Komponente trackt:
- Code-Änderungen zwischen Iterationen  
- Erfolg/Misserfolg von Modifikationen
- Pattern von erfolgreichen Verbesserungen
- Qualitätsmetriken und Trends
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import difflib

@dataclass
class CompilationError:
    """Repräsentiert einen Kompilierungsfehler"""
    error_type: str
    error_message: str
    line_number: Optional[int]
    code_snippet: str
    solution_attempt: str
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CompilationError':
        return cls(**data)

@dataclass
class CodeVersion:
    """Repräsentiert eine Code-Version"""
    version_id: str
    code: str
    timestamp: datetime
    iteration: int
    quality_score: float
    compilation_success: bool
    review_feedback: str
    changes_from_previous: str
    improvement_areas: List[str]
    compilation_errors: List[CompilationError]  # NEU: Fehler-Memory
    fixed_errors: List[str]  # NEU: Behobene Fehler aus vorherigen Iterationen
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['compilation_errors'] = [error.to_dict() for error in self.compilation_errors]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CodeVersion':
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        # Backward compatibility
        if 'compilation_errors' not in data:
            data['compilation_errors'] = []
        if 'fixed_errors' not in data:
            data['fixed_errors'] = []
        data['compilation_errors'] = [CompilationError.from_dict(error) for error in data['compilation_errors']]
        return cls(**data)

class CodeEvolution:
    """Verwaltet die Evolution von EA-Code"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.versions: List[CodeVersion] = []
        self.current_version = 0
        self.session_file = f"evolution_{session_id}.json"
        self.load_session()
    
    def add_version(self, code: str, iteration: int, quality_score: float = 0.0, 
                   compilation_success: bool = False, review_feedback: str = "",
                   improvement_areas: List[str] = None, 
                   compilation_errors: List[CompilationError] = None,
                   fixed_errors: List[str] = None) -> str:
        """Fügt eine neue Code-Version hinzu"""
        
        if compilation_errors is None:
            compilation_errors = []
        if fixed_errors is None:
            fixed_errors = []
        
        # Version ID generieren
        code_hash = hashlib.md5(code.encode()).hexdigest()[:8]
        version_id = f"v{iteration}_{code_hash}"
        
        # Änderungen zur vorherigen Version berechnen
        changes = ""
        if self.versions:
            previous_code = self.versions[-1].code
            changes = self._calculate_diff(previous_code, code)
        
        # Neue Version erstellen
        version = CodeVersion(
            version_id=version_id,
            code=code,
            timestamp=datetime.now(),
            iteration=iteration,
            quality_score=quality_score,
            compilation_success=compilation_success,
            review_feedback=review_feedback,
            changes_from_previous=changes,
            improvement_areas=improvement_areas or [],
            compilation_errors=compilation_errors,
            fixed_errors=fixed_errors
        )
        
        self.versions.append(version)
        self.current_version = len(self.versions) - 1
        self.save_session()
        
        return version_id
    
    def _calculate_diff(self, old_code: str, new_code: str) -> str:
        """Berechnet die Unterschiede zwischen zwei Code-Versionen"""
        old_lines = old_code.splitlines()
        new_lines = new_code.splitlines()
        
        diff = list(difflib.unified_diff(
            old_lines, new_lines,
            fromfile='previous', tofile='current',
            lineterm='', n=3
        ))
        
        return '\n'.join(diff[:50])  # Ersten 50 Zeilen des Diffs
    
    def get_current_version(self) -> Optional[CodeVersion]:
        """Holt die aktuelle Code-Version"""
        if self.versions:
            return self.versions[self.current_version]
        return None
    
    def get_version_by_id(self, version_id: str) -> Optional[CodeVersion]:
        """Holt eine spezifische Version"""
        for version in self.versions:
            if version.version_id == version_id:
                return version
        return None
    
    def get_quality_trend(self) -> List[Tuple[int, float]]:
        """Berechnet den Qualitätstrend"""
        return [(v.iteration, v.quality_score) for v in self.versions]
    
    def get_compilation_success_rate(self) -> float:
        """Berechnet die Kompilierungs-Erfolgsrate"""
        if not self.versions:
            return 0.0
        
        successful = sum(1 for v in self.versions if v.compilation_success)
        return successful / len(self.versions)
    
    def get_improvement_patterns(self) -> Dict[str, int]:
        """Analysiert erfolgreiche Verbesserungs-Pattern"""
        patterns = {}
        
        for i, version in enumerate(self.versions[1:], 1):
            previous = self.versions[i-1]
            
            # Wenn die aktuelle Version besser ist
            if version.quality_score > previous.quality_score:
                for area in version.improvement_areas:
                    patterns[area] = patterns.get(area, 0) + 1
        
        return dict(sorted(patterns.items(), key=lambda x: x[1], reverse=True))
    
    def get_best_version(self) -> Optional[CodeVersion]:
        """Holt die beste Version basierend auf Qualitäts-Score"""
        if not self.versions:
            return None
        
        return max(self.versions, key=lambda v: v.quality_score)
    
    def get_evolution_summary(self) -> Dict:
        """Erstellt eine Zusammenfassung der Code-Evolution"""
        if not self.versions:
            return {
                "status": "no_versions",
                "total_versions": 0,
                "compilation_success_rate": 0.0,
                "quality_trend": [],
                "improvement_patterns": {},
                "recurring_errors": {},
                "fixed_errors_count": 0
            }
        
        # Wiederkehrende Fehler analysieren
        recurring_errors = self.get_recurring_errors()
        fixed_errors_total = sum(len(v.fixed_errors) for v in self.versions)
        
        return {
            "status": "active",
            "session_id": self.session_id,
            "total_versions": len(self.versions),
            "current_iteration": self.current_version,
            "compilation_success_rate": self.get_compilation_success_rate(),
            "quality_trend": self.get_quality_trend(),
            "improvement_patterns": self.get_improvement_patterns(),
            "best_quality_score": max(v.quality_score for v in self.versions),
            "latest_quality_score": self.versions[-1].quality_score,
            "recurring_errors": recurring_errors,
            "fixed_errors_count": fixed_errors_total,
            "most_common_error": max(recurring_errors.items(), key=lambda x: x[1])[0] if recurring_errors else None,
            "evolution_direction": self._calculate_evolution_direction()
        }
    
    def get_recurring_errors(self) -> Dict[str, int]:
        """Analysiert wiederkehrende Fehler"""
        error_patterns = {}
        
        for version in self.versions:
            for error in version.compilation_errors:
                # Normalisiere Fehlermeldung für bessere Pattern-Erkennung
                normalized_error = self._normalize_error_message(error.error_message)
                error_patterns[normalized_error] = error_patterns.get(normalized_error, 0) + 1
        
        return dict(sorted(error_patterns.items(), key=lambda x: x[1], reverse=True))
    
    def _normalize_error_message(self, error_msg: str) -> str:
        """Normalisiert Fehlermeldungen für Pattern-Erkennung"""
        # Entferne Zeilen-/Spaltennummern und spezifische Namen
        import re
        
        # Entferne Zeilen/Spalten-Referenzen
        error_msg = re.sub(r'\(\d+,\d+\)', '', error_msg)
        error_msg = re.sub(r'line \d+', 'line X', error_msg)
        
        # Entferne spezifische Variablen/Funktionsnamen (behalte Pattern)
        error_msg = re.sub(r"'[^']*'", "'IDENTIFIER'", error_msg)
        
        return error_msg.strip().lower()
    
    def get_error_learning_context(self) -> str:
        """Generiert Kontext aus früheren Fehlern für LLM"""
        if not self.versions:
            return ""
        
        context_parts = []
        
        # Wiederkehrende Fehler
        recurring = self.get_recurring_errors()
        if recurring:
            context_parts.append("🚨 WIEDERKEHRENDE FEHLER (UNBEDINGT VERMEIDEN):")
            for error, count in list(recurring.items())[:5]:  # Top 5
                context_parts.append(f"   ❌ {error} (aufgetreten {count}x)")
        
        # Erfolgreich behobene Fehler
        fixed_patterns = {}
        for version in self.versions:
            for fixed in version.fixed_errors:
                fixed_patterns[fixed] = fixed_patterns.get(fixed, 0) + 1
        
        if fixed_patterns:
            context_parts.append("\n✅ ERFOLGREICH BEHOBENE FEHLER (als Referenz):")
            for fixed, count in list(fixed_patterns.items())[:3]:  # Top 3
                context_parts.append(f"   ✓ {fixed}")
        
        # Letzte Kompilierungsfehler
        last_failed_versions = [v for v in self.versions[-5:] if not v.compilation_success]
        if last_failed_versions:
            context_parts.append("\n⚠️ LETZTE KOMPILIERUNGSFEHLER:")
            for version in last_failed_versions[-3:]:  # Letzte 3
                context_parts.append(f"   Iteration {version.iteration}:")
                for error in version.compilation_errors[:2]:  # Max 2 Fehler pro Version
                    context_parts.append(f"     - {error.error_type}: {error.error_message}")
        
        # Pattern erfolgreicher Fixes
        successful_versions = [v for v in self.versions if v.compilation_success]
        if successful_versions:
            context_parts.append(f"\n💡 ERFOLGREICHE PATTERN (aus {len(successful_versions)} erfolgreichen Versionen):")
            for version in successful_versions[-2:]:  # Letzte 2 erfolgreiche
                if version.fixed_errors:
                    context_parts.append(f"   Iteration {version.iteration} behoben: {', '.join(version.fixed_errors[:3])}")
        
        return "\n".join(context_parts)
    
    def parse_compilation_errors_from_log(self, log_content: str) -> List[CompilationError]:
        """Parst Kompilierungsfehler aus dem MetaEditor Log"""
        errors = []
        
        # Typische MetaEditor Fehlermuster
        import re
        error_patterns = [
            r"'([^']+)'\s*-\s*(.+)",  # 'identifier' - error message
            r"(\d+)\s*:\s*(.+)",       # line: error message
            r"error\s*(\d+)?\s*:\s*(.+)",  # error: message
        ]
        
        lines = log_content.split('\n')
        for line in lines:
            line = line.strip()
            if not line or 'warning' in line.lower():
                continue
                
            for pattern in error_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    if len(match.groups()) >= 2:
                        error_type = "compilation_error"
                        error_message = match.group(2).strip()
                        line_number = None
                        
                        # Versuche Zeilen-Nummer zu extrahieren
                        line_match = re.search(r'(\d+)', match.group(1))
                        if line_match:
                            line_number = int(line_match.group(1))
                        
                        errors.append(CompilationError(
                            error_type=error_type,
                            error_message=error_message,
                            line_number=line_number,
                            code_snippet=line,
                            solution_attempt=""
                        ))
                        break
        
        return errors
    
    def _calculate_evolution_direction(self) -> str:
        """Berechnet die Richtung der Evolution"""
        if len(self.versions) < 3:
            return "insufficient_data"
        
        recent_scores = [v.quality_score for v in self.versions[-3:]]
        
        if recent_scores[-1] > recent_scores[0]:
            return "improving"
        elif recent_scores[-1] < recent_scores[0]:
            return "degrading"
        else:
            return "stable"
    
    def get_targeted_feedback(self) -> str:
        """Generiert gezieltes Feedback für die nächste Iteration"""
        summary = self.get_evolution_summary()
        
        # Prüfe auf leere Session
        if summary.get("total_versions", 0) == 0:
            return "Erste Code-Version - fokussiere auf grundlegende Struktur und FTMO-Compliance."
        
        feedback = f"🔄 Evolution Status (Iteration {summary['current_iteration']}):\n\n"
        
        # Qualitätstrend
        direction = summary["evolution_direction"]
        if direction == "improving":
            feedback += "✅ Positive Entwicklung - aktuelle Richtung beibehalten!\n"
        elif direction == "degrading":
            feedback += "⚠️ Qualität verschlechtert sich - letzte erfolgreiche Änderungen analysieren!\n"
        else:
            feedback += "📊 Stabile Qualität - neue Verbesserungsansätze probieren.\n"
        
        # Kompilierungs-Erfolg
        success_rate = summary["compilation_success_rate"]
        if success_rate < 0.7:
            feedback += f"🔴 Niedrige Kompilierungs-Rate ({success_rate:.1%}) - Syntax-Fokus erforderlich!\n"
        elif success_rate > 0.9:
            feedback += f"✅ Excellent Kompilierungs-Rate ({success_rate:.1%})\n"
        
        # Verbesserungs-Pattern
        patterns = summary["improvement_patterns"]
        if patterns:
            top_pattern = list(patterns.keys())[0]
            feedback += f"🎯 Erfolgreichstes Verbesserungs-Pattern: {top_pattern}\n"
        
        # Spezifische Empfehlungen
        current = self.get_current_version()
        if current and not current.compilation_success:
            feedback += "\n🔧 PRIORITÄT: Syntax-Fehler beheben vor neuen Features!\n"
        
        if summary["latest_quality_score"] < 0.5:
            feedback += "\n📋 FOKUS: Grundlegende Code-Struktur und FTMO-Regeln implementieren.\n"
        elif summary["latest_quality_score"] < 0.8:
            feedback += "\n📈 FOKUS: Trading-Logik verbessern und Error Handling erweitern.\n"
        else:
            feedback += "\n🚀 FOKUS: Performance-Optimierung und erweiterte Features.\n"
        
        return feedback
    
    def save_session(self):
        """Speichert die Session in eine JSON-Datei"""
        data = {
            "session_id": self.session_id,
            "current_version": self.current_version,
            "versions": [v.to_dict() for v in self.versions]
        }
        
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_session(self):
        """Lädt eine gespeicherte Session"""
        try:
            if Path(self.session_file).exists():
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.current_version = data.get("current_version", 0)
                self.versions = [CodeVersion.from_dict(v) for v in data.get("versions", [])]
        except Exception as e:
            print(f"Warnung: Konnte Session nicht laden: {e}")
            self.versions = []
            self.current_version = 0
