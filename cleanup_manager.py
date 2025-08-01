"""
Automatic Cleanup System für Smart LLM Loop
==========================================

Räumt automatisch alte Dateien, temporäre Dateien und 
veraltete Evolution-Sessions auf.
"""

import os
import glob
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict
import logging

class CleanupManager:
    """Verwaltet automatische Aufräum-Operationen"""
    
    def __init__(self, workspace_dir: str):
        self.workspace_dir = workspace_dir
        self.logger = logging.getLogger(__name__)
        
    def cleanup_old_evolution_files(self, max_age_hours: int = 24) -> int:
        """Entfernt alte Evolution-JSON Dateien"""
        cutoff_time = time.time() - (max_age_hours * 3600)
        removed_count = 0
        
        evolution_files = glob.glob(os.path.join(self.workspace_dir, "evolution_*.json"))
        
        for file_path in evolution_files:
            try:
                file_age = os.path.getmtime(file_path)
                if file_age < cutoff_time:
                    os.remove(file_path)
                    removed_count += 1
                    self.logger.info(f"Entfernt alte Evolution-Datei: {os.path.basename(file_path)}")
            except Exception as e:
                self.logger.warning(f"Konnte Datei nicht entfernen {file_path}: {e}")
                
        return removed_count
    
    def cleanup_old_ea_files(self, max_age_hours: int = 48) -> int:
        """Entfernt alte generierte EA-Dateien"""
        cutoff_time = time.time() - (max_age_hours * 3600)
        removed_count = 0
        
        ea_files = glob.glob(os.path.join(self.workspace_dir, "FTMO_EA_*.mq5"))
        
        for file_path in ea_files:
            try:
                file_age = os.path.getmtime(file_path)
                if file_age < cutoff_time:
                    os.remove(file_path)
                    removed_count += 1
                    self.logger.info(f"Entfernt alte EA-Datei: {os.path.basename(file_path)}")
            except Exception as e:
                self.logger.warning(f"Konnte EA-Datei nicht entfernen {file_path}: {e}")
                
        return removed_count
    
    def cleanup_old_session_reports(self, max_age_hours: int = 72) -> int:
        """Entfernt alte Session-Reports"""
        cutoff_time = time.time() - (max_age_hours * 3600)
        removed_count = 0
        
        report_files = glob.glob(os.path.join(self.workspace_dir, "session_report_*.json"))
        
        for file_path in report_files:
            try:
                file_age = os.path.getmtime(file_path)
                if file_age < cutoff_time:
                    os.remove(file_path)
                    removed_count += 1
                    self.logger.info(f"Entfernt alten Session-Report: {os.path.basename(file_path)}")
            except Exception as e:
                self.logger.warning(f"Konnte Report nicht entfernen {file_path}: {e}")
                
        return removed_count
    
    def cleanup_temp_files(self) -> int:
        """Entfernt temporäre Dateien"""
        temp_patterns = [
            "tmp*.mq5",
            "tmp*.ex5", 
            "tmp*.log",
            "*.tmp"
        ]
        
        removed_count = 0
        import tempfile
        temp_dir = tempfile.gettempdir()
        
        for pattern in temp_patterns:
            temp_files = glob.glob(os.path.join(temp_dir, pattern))
            for file_path in temp_files:
                try:
                    # Nur Dateien älter als 1 Stunde entfernen
                    file_age = os.path.getmtime(file_path)
                    if time.time() - file_age > 3600:
                        os.remove(file_path)
                        removed_count += 1
                except Exception:
                    pass  # Ignoriere Fehler bei temp-Dateien
                    
        return removed_count
    
    def get_session_statistics(self) -> Dict:
        """Sammelt Statistiken über Sessions"""
        evolution_files = glob.glob(os.path.join(self.workspace_dir, "evolution_*.json"))
        ea_files = glob.glob(os.path.join(self.workspace_dir, "FTMO_EA_*.mq5"))
        report_files = glob.glob(os.path.join(self.workspace_dir, "session_report_*.json"))
        
        total_iterations = 0
        total_sessions = len(evolution_files)
        
        for evo_file in evolution_files:
            try:
                with open(evo_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'versions' in data:
                        total_iterations += len(data['versions'])
            except Exception:
                pass
                
        return {
            "total_sessions": total_sessions,
            "total_iterations": total_iterations,
            "total_ea_files": len(ea_files),
            "total_reports": len(report_files),
            "avg_iterations_per_session": total_iterations / max(total_sessions, 1)
        }
    
    def full_cleanup(self) -> Dict[str, int]:
        """Führt eine vollständige Aufräumung durch"""
        print("🧹 AUTOMATISCHES CLEANUP GESTARTET...")
        
        results = {
            "evolution_files": self.cleanup_old_evolution_files(24),
            "ea_files": self.cleanup_old_ea_files(48),
            "session_reports": self.cleanup_old_session_reports(72),
            "temp_files": self.cleanup_temp_files()
        }
        
        total_removed = sum(results.values())
        
        print(f"✅ Cleanup abgeschlossen: {total_removed} Dateien entfernt")
        print(f"   📊 Evolution Files: {results['evolution_files']}")
        print(f"   📄 EA Files: {results['ea_files']}")
        print(f"   📋 Session Reports: {results['session_reports']}")
        print(f"   🗂️ Temp Files: {results['temp_files']}")
        
        return results
    
    def schedule_cleanup_if_needed(self) -> bool:
        """Führt Cleanup durch wenn nötig (> 50 Dateien)"""
        evolution_files = len(glob.glob(os.path.join(self.workspace_dir, "evolution_*.json")))
        ea_files = len(glob.glob(os.path.join(self.workspace_dir, "FTMO_EA_*.mq5")))
        
        if evolution_files + ea_files > 50:
            self.full_cleanup()
            return True
        return False
