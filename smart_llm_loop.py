"""
Smart LLM Loop - Next Generation EA Generator
============================================

Diese neue Architektur implementiert:
- Intelligenten Kontext und Memory
- Strukturierte LLM-Kommunikation  
- Code-Evolution Tracking
- Umfassende Validierung
- Produktionsreife Pipeline
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import uuid

import aiohttp
import colorama
from colorama import Fore, Style

from knowledge_base import KnowledgeBase
from code_evolution import CodeEvolution, CodeVersion
from prompt_templates import PromptTemplates
from cleanup_manager import CleanupManager
from mql5_error_templates import MQL5ErrorTemplates
from error_categorizer import ErrorCategorizer, ErrorComplexity
from incremental_fixer import IncrementalFixer, CodeChange
from success_pattern_learner import SuccessPatternLearner

# Initialisiere Colorama für Windows-Terminal
colorama.init()

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('smart_llm_loop.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ValidationResult:
    """Ergebnis einer Code-Validierung"""
    
    def __init__(self, success: bool, score: float, details: str, error_type: str = "", compilation_errors: List = None):
        self.success = success
        self.score = score
        self.details = details
        self.error_type = error_type
        self.compilation_errors = compilation_errors or []
    
    def __str__(self):
        status = "✅ PASS" if self.success else "❌ FAIL"
        return f"{status} (Score: {self.score:.2f}) - {self.details}"

class OllamaClient:
    """Erweiterte Ollama Client mit besserer Fehlerbehandlung"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=300))
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def generate(self, model: str, prompt: str, system: str = "") -> str:
        """Generiert eine Antwort mit verbesserter Fehlerbehandlung"""
        if not self.session:
            raise RuntimeError("Client wurde nicht korrekt initialisiert")
        
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "options": {
                "temperature": 0.1,  # Niedrige Temperatur für konsistente Ergebnisse
                "top_p": 0.9,
                "top_k": 40
            }
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

class CodeValidator:
    """Umfassende Code-Validierung"""
    
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.compile_script = os.path.join(self.script_dir, "compile.ps1")
    
    async def validate_syntax(self, code: str) -> ValidationResult:
        """Validiert MQL5 Syntax über MetaEditor"""
        import tempfile
        import subprocess
        
        # Schnelle Struktur-Prüfung
        if '```' in code:
            return ValidationResult(False, 0.0, "Code enthält Markdown-Formatierung", "markdown")
        
        if not code.strip().startswith('//+'):
            return ValidationResult(False, 0.1, "Code muss mit //+ Header beginnen", "structure")
        
        required_functions = ['OnInit', 'OnTick']
        missing = [func for func in required_functions if func not in code]
        if missing:
            return ValidationResult(False, 0.2, f"Fehlende Funktionen: {missing}", "missing_functions")
        
        # MetaEditor Kompilierung
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.mq5', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name
            
            result = subprocess.run([
                "powershell.exe",
                "-ExecutionPolicy", "Bypass", 
                "-File", self.compile_script,
                "-FileToCompile", temp_file_path
            ], capture_output=True, text=True, timeout=60, check=False)
            
            ex5_file = temp_file_path.replace('.mq5', '.ex5')
            ex5_exists = os.path.exists(ex5_file)
            
            # Cleanup
            for file_path in [temp_file_path, ex5_file, temp_file_path + '.log']:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except:
                    pass
            
            if result.returncode == 0 and ex5_exists and "ERFOLGREICH" in result.stdout:
                return ValidationResult(True, 1.0, "Syntax-Validierung erfolgreich")
            else:
                error_details = result.stdout + result.stderr
                
                # Parse Compilation Errors für Learning
                compilation_errors = self._parse_compilation_errors(error_details, temp_file_path)
                
                return ValidationResult(False, 0.3, f"Kompilierung fehlgeschlagen: {error_details[:200]}", "compilation", compilation_errors)
                
        except Exception as e:
            return ValidationResult(False, 0.0, f"Syntax-Prüfung Fehler: {e}", "exception")
    
    def _parse_compilation_errors(self, error_output: str, file_path: str) -> List:
        """Parst Kompilierungsfehler aus MetaEditor Output"""
        from code_evolution import CompilationError
        
        errors = []
        lines = error_output.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or 'warning' in line.lower():
                continue
                
            # Typische MetaEditor Fehlermuster
            if any(indicator in line.lower() for indicator in ['error', 'failed', 'expected', 'undefined']):
                errors.append(CompilationError(
                    error_type="compilation_error",
                    error_message=line,
                    line_number=None,
                    code_snippet=line,
                    solution_attempt=""
                ))
        
        return errors
    
    def validate_ftmo_compliance(self, code: str) -> ValidationResult:
        """Prüft FTMO-Regel-Compliance"""
        score = 0.0
        issues = []
        
        # Kritische FTMO-Komponenten prüfen
        ftmo_checks = {
            "daily_loss": ["daily", "loss", "5", "%"],
            "total_loss": ["total", "loss", "10", "%"], 
            "account_balance": ["AccountInfoDouble", "BALANCE"],
            "account_equity": ["AccountInfoDouble", "EQUITY"],
            "position_management": ["PositionSelect", "OrderSend"]
        }
        
        for check_name, keywords in ftmo_checks.items():
            if all(keyword.lower() in code.lower() for keyword in keywords):
                score += 0.2
            else:
                issues.append(f"Fehlende {check_name} Implementation")
        
        if score >= 0.8:
            return ValidationResult(True, score, "FTMO-Compliance erfüllt")
        else:
            return ValidationResult(False, score, f"FTMO-Mängel: {issues}", "ftmo_compliance")
    
    def validate_code_quality(self, code: str) -> ValidationResult:
        """Bewertet allgemeine Code-Qualität"""
        score = 0.0
        details = []
        
        # Code-Länge (Mindestanforderung für vollständigen EA)
        if len(code) > 2000:
            score += 0.2
            details.append("Ausreichende Code-Länge")
        
        # Dokumentation
        if code.count('//') > 10:
            score += 0.15
            details.append("Gute Dokumentation")
        
        # Error Handling
        error_patterns = ['try', 'catch', 'if(', 'return false', 'Print("Error']
        if sum(1 for pattern in error_patterns if pattern in code) >= 3:
            score += 0.2
            details.append("Error Handling vorhanden")
        
        # Input Parameter
        if 'input ' in code and code.count('input ') >= 3:
            score += 0.15
            details.append("Konfigurierbare Parameter")
        
        # Modular structure
        if code.count('function') + code.count('void ') + code.count('double ') + code.count('int ') >= 8:
            score += 0.15
            details.append("Modulare Struktur")
        
        # Trading logic
        if 'OrderSend' in code or 'trade.' in code:
            score += 0.15
            details.append("Trading-Logik implementiert")
        
        return ValidationResult(score >= 0.7, score, f"Qualität: {', '.join(details)}")
    
    async def comprehensive_validation(self, code: str) -> Dict[str, ValidationResult]:
        """Führt umfassende Validierung durch"""
        results = {}
        
        # Syntax-Validierung (kritisch)
        results['syntax'] = await self.validate_syntax(code)
        
        # FTMO-Compliance (kritisch)
        results['ftmo'] = self.validate_ftmo_compliance(code)
        
        # Code-Qualität 
        results['quality'] = self.validate_code_quality(code)
        
        # Gesamt-Score berechnen
        weights = {'syntax': 0.4, 'ftmo': 0.4, 'quality': 0.2}
        total_score = sum(results[key].score * weights[key] for key in weights)
        
        all_passed = all(result.success for result in results.values())
        results['overall'] = ValidationResult(all_passed, total_score, 
                                            f"Gesamt-Score: {total_score:.2f}")
        
        return results

class SmartLLMLoop:
    """Next-Generation LLM Loop mit intelligenter Architektur"""
    
    def __init__(self, config_file: str = "config.json"):
        # Konfiguration laden
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        # Session ID für Tracking
        self.session_id = str(uuid.uuid4())[:8]
        
        # Core Komponenten initialisieren
        self.knowledge_base = KnowledgeBase()
        self.code_evolution = CodeEvolution(self.session_id)
        self.prompt_templates = PromptTemplates(self.knowledge_base)
        self.validator = CodeValidator()
        self.cleanup_manager = CleanupManager(os.getcwd())
        
        # 🚀 4-PHASEN OPTIMIERUNG SYSTEM 🚀
        self.error_categorizer = ErrorCategorizer()
        self.incremental_fixer = IncrementalFixer(max_changes_per_iteration=5)
        self.success_learner = SuccessPatternLearner()
        self.mql5_templates = MQL5ErrorTemplates()
        
        # LLM Konfiguration
        self.instructor_model = self.config["models"]["instructor"]
        self.coder_model = self.config["models"]["coder"] 
        self.max_iterations = self.config["settings"]["max_iterations"]
        
        # State
        self.current_iteration = 0
        self.session_stats = {
            "start_time": datetime.now(),
            "total_iterations": 0,
            "successful_compilations": 0,
            "quality_improvements": 0,
            "best_score": 0.0,
            "phase_usage": {'1': 0, '2': 0, '3': 0, '4': 0},
            "error_reduction_rate": 0.0
        }
    
    def print_header(self, title: str, color: str = Fore.CYAN):
        """Druckt einen formatierten Header"""
        print(f"\n{color}{'='*80}")
        print(f"{title:^80}")
        print(f"{'='*80}{Style.RESET_ALL}")
    
    def print_validation_results(self, results: Dict[str, ValidationResult]):
        """Zeigt Validierungs-Ergebnisse an"""
        print(f"\n{Fore.YELLOW}📊 VALIDIERUNGS-ERGEBNISSE:{Style.RESET_ALL}")
        
        for category, result in results.items():
            color = Fore.GREEN if result.success else Fore.RED
            icon = "✅" if result.success else "❌"
            print(f"{color}{icon} {category.upper()}: {result}{Style.RESET_ALL}")
    
    async def generate_initial_instruction(self, client: OllamaClient, strategy: str = "trend_following") -> str:
        """Generiert die initiale Entwicklungsanweisung"""
        self.print_header("🎯 INSTRUCTOR: STRATEGISCHE ENTWICKLUNGSANWEISUNG", Fore.BLUE)
        
        prompts = self.prompt_templates.get_instructor_initial_prompt(strategy)
        
        logger.info(f"Instructor erstellt Entwicklungsanweisung für {strategy} Strategie...")
        
        instruction = await client.generate(
            model=self.instructor_model,
            prompt=prompts["user"],
            system=prompts["system"]
        )
        
        print(f"{Fore.GREEN}✅ Entwicklungsanweisung erstellt ({len(instruction):,} Zeichen){Style.RESET_ALL}")
        print(f"{instruction[:500]}..." if len(instruction) > 500 else instruction)
        
        return instruction
    
    async def generate_code(self, client: OllamaClient, instruction: str, 
                           previous_errors: List[str] = None, 
                           evolution: CodeEvolution = None) -> Tuple[str, str]:
        """Generiert MQL5 Code basierend auf Anweisung"""
        self.print_header("💻 CODER: MQL5 EXPERT ADVISOR ENTWICKLUNG", Fore.GREEN)
        
        # Kontext aus Knowledge Base
        knowledge_context = self.knowledge_base.generate_knowledge_context()
        
        prompts = self.prompt_templates.get_coder_generation_prompt(
            instruction, knowledge_context, previous_errors, evolution
        )
        
        logger.info("Coder entwickelt Expert Advisor...")
        
        code = await client.generate(
            model=self.coder_model,
            prompt=prompts["user"],
            system=prompts["system"]
        )
        
        # Code-Version hinzufügen
        version_id = self.code_evolution.add_version(
            code=code,
            iteration=self.current_iteration,
            improvement_areas=["initial_development"]
        )
        
        print(f"{Fore.GREEN}✅ Expert Advisor generiert (Version: {version_id}, {len(code):,} Zeichen){Style.RESET_ALL}")
        
        return code, version_id
    
    async def validate_and_review_code(self, client: OllamaClient, code: str, 
                                     instruction: str) -> Tuple[bool, str, Dict]:
        """Umfassende Code-Validierung und Review"""
        self.print_header("🔬 VALIDIERUNG & REVIEW", Fore.MAGENTA)
        
        # 1. Automatische Validierung
        print(f"{Fore.YELLOW}🔧 Automatische Validierung...{Style.RESET_ALL}")
        validation_results = await self.validator.comprehensive_validation(code)
        self.print_validation_results(validation_results)
        
        # Validation Score in Evolution tracken
        overall_score = validation_results['overall'].score
        compilation_success = validation_results['syntax'].success
        
        # 2. LLM Review
        print(f"\n{Fore.YELLOW}🎭 Instructor Review...{Style.RESET_ALL}")
        
        # Kompilierungs-Details für Review
        syntax_result = validation_results['syntax']
        compilation_details = f"✅ SYNTAX: {syntax_result}" if syntax_result.success else f"❌ SYNTAX: {syntax_result}"
        
        prompts = self.prompt_templates.get_reviewer_prompt(
            code, instruction, self.code_evolution, compilation_details
        )
        
        review = await client.generate(
            model=self.instructor_model,
            prompt=prompts["user"], 
            system=prompts["system"]
        )
        
        print(f"{Fore.CYAN}📋 Review-Ergebnis:{Style.RESET_ALL}")
        print(review[:800] + "..." if len(review) > 800 else review)
        
        # Review-Parsing für Zufriedenheit
        is_satisfied = (
            "ZUFRIEDEN: JA" in review and
            overall_score >= 0.8 and
            compilation_success and
            "SYNTAX: BESTANDEN" in review
        )
        
        # Evolution aktualisieren
        self.code_evolution.versions[-1].quality_score = overall_score
        self.code_evolution.versions[-1].compilation_success = compilation_success
        self.code_evolution.versions[-1].review_feedback = review
        self.code_evolution.save_session()
        
        # Stats aktualisieren
        if compilation_success:
            self.session_stats["successful_compilations"] += 1
        if overall_score > self.session_stats["best_score"]:
            self.session_stats["best_score"] = overall_score
            self.session_stats["quality_improvements"] += 1
        
        return is_satisfied, review, validation_results
    
    async def improve_code(self, client: OllamaClient, code: str, review: str) -> str:
        """Verbessert Code basierend auf Review"""
        self.print_header("🛠️ CODE-VERBESSERUNG", Fore.YELLOW)
        
        prompts = self.prompt_templates.get_improvement_prompt(
            code, review, self.code_evolution
        )
        
        logger.info("Coder implementiert Verbesserungen...")
        
        improved_code = await client.generate(
            model=self.coder_model,
            prompt=prompts["user"],
            system=prompts["system"]
        )
        
        # Neue Version tracken
        version_id = self.code_evolution.add_version(
            code=improved_code,
            iteration=self.current_iteration,
            improvement_areas=["review_feedback"]
        )
        
        print(f"{Fore.GREEN}✅ Code verbessert (Version: {version_id}){Style.RESET_ALL}")
        
        return improved_code
    
    def save_final_results(self, final_code: str, final_validation: Dict):
        """Speichert finale Ergebnisse"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # EA Code speichern
        ea_filename = f"FTMO_EA_{self.session_id}_{timestamp}.mq5"
        with open(ea_filename, 'w', encoding='utf-8') as f:
            f.write(final_code)
        
        # Session Report
        session_duration = datetime.now() - self.session_stats["start_time"]
        evolution_summary = self.code_evolution.get_evolution_summary()
        
        report = {
            "session_id": self.session_id,
            "timestamp": timestamp,
            "duration_minutes": session_duration.total_seconds() / 60,
            "final_validation": {k: str(v) for k, v in final_validation.items()},
            "evolution_summary": evolution_summary,
            "session_stats": self.session_stats,
            "final_code_file": ea_filename
        }
        
        report_filename = f"session_report_{self.session_id}_{timestamp}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n{Fore.GREEN}💾 FINALE ERGEBNISSE GESPEICHERT:{Style.RESET_ALL}")
        print(f"📄 Expert Advisor: {ea_filename}")
        print(f"📊 Session Report: {report_filename}")
        
        return ea_filename, report_filename
    
    def print_session_summary(self):
        """Zeigt Session-Zusammenfassung"""
        evolution_summary = self.code_evolution.get_evolution_summary()
        duration = datetime.now() - self.session_stats["start_time"]
        
        self.print_header("📊 SESSION ZUSAMMENFASSUNG", Fore.CYAN)
        
        print(f"🆔 Session ID: {self.session_id}")
        print(f"⏱️  Dauer: {duration.total_seconds()/60:.1f} Minuten")
        print(f"🔄 Iterationen: {evolution_summary['total_versions']}")
        print(f"✅ Erfolgreiche Kompilierungen: {self.session_stats['successful_compilations']}")
        print(f"📈 Qualitäts-Verbesserungen: {self.session_stats['quality_improvements']}")
        print(f"🏆 Beste Qualität: {evolution_summary['best_quality_score']:.2f}")
        print(f"📊 Evolution: {evolution_summary['evolution_direction']}")
        
        if evolution_summary['improvement_patterns']:
            print(f"🎯 Top Verbesserungs-Pattern: {list(evolution_summary['improvement_patterns'].keys())[0]}")
    
    async def run(self, strategy: str = "trend_following", 
                  target_quality: float = 0.85, 
                  max_iterations: int = None):
        """Hauptschleife des Smart LLM Loop"""
        
        # Auto-Cleanup bei Bedarf  
        cleaned = self.cleanup_manager.schedule_cleanup_if_needed()
        if cleaned:
            print("🧹 Automatisches Cleanup durchgeführt")
        
        # Iterations-Limit setzen
        if max_iterations:
            self.max_iterations = max_iterations
            
        self.print_header("🚀 SMART LLM LOOP - FTMO EA GENERATOR", Fore.CYAN)
        
        print(f"🎯 Ziel-Strategie: {strategy.title()}")
        print(f"📊 Ziel-Qualität: {target_quality:.1%}")
        print(f"🔄 Max Iterationen: {self.max_iterations}")
        print(f"🤖 Instructor: {self.instructor_model}")
        print(f"⚡ Coder: {self.coder_model}")
        
        async with OllamaClient() as client:
            try:
                # 1. Initiale Entwicklungsanweisung
                instruction = await self.generate_initial_instruction(client, strategy)
                
                # 2. Iterative Entwicklung
                current_code = ""
                current_instruction = instruction
                errors_history = []
                
                for iteration in range(self.max_iterations):
                    self.current_iteration = iteration
                    self.session_stats["total_iterations"] = iteration + 1
                    
                    print(f"\n{Fore.YELLOW}🔄 === ITERATION {iteration + 1}/{self.max_iterations} ==={Style.RESET_ALL}")
                    
                    # Code generieren (mit Fehler-Memory)
                    current_code, version_id = await self.generate_code(
                        client, current_instruction, errors_history[-3:] if errors_history else None, self.code_evolution
                    )
                    
                    # Validierung & Review
                    is_satisfied, review, validation_results = await self.validate_and_review_code(
                        client, current_code, instruction
                    )
                    
                    # Evolution mit Fehler-Memory aktualisieren
                    compilation_errors = []
                    fixed_errors = []
                    
                    # Sammle Compilation Errors
                    if 'syntax' in validation_results and validation_results['syntax'].compilation_errors:
                        compilation_errors = validation_results['syntax'].compilation_errors
                    
                    # Prüfe behobene Fehler
                    if errors_history:
                        for prev_error in errors_history[-5:]:  # Letzte 5 Fehler
                            if prev_error not in [err.error_message for err in compilation_errors]:
                                fixed_errors.append(prev_error)
                    
                    # Version zur Evolution hinzufügen
                    self.code_evolution.add_version(
                        code=current_code,
                        iteration=iteration,
                        quality_score=validation_results['overall'].score,
                        compilation_success=validation_results['syntax'].success,
                        review_feedback=review,
                        improvement_areas=["iteration_development"],
                        compilation_errors=compilation_errors,
                        fixed_errors=fixed_errors
                    )
                    
                    # Erfolg prüfen
                    overall_score = validation_results['overall'].score
                    
                    if is_satisfied and overall_score >= target_quality:
                        print(f"\n{Fore.GREEN}🎉 ZIEL ERREICHT! Expert Advisor ist produktionsreif!{Style.RESET_ALL}")
                        break
                    
                    # Fehler für nächste Iteration sammeln
                    for category, result in validation_results.items():
                        if not result.success and result.error_type:
                            errors_history.append(f"{category}: {result.details}")
                    
                    # Zeige Fehler-Memory Status
                    if compilation_errors:
                        print(f"\n{Fore.RED}❌ Neue Compilierung-Fehler: {len(compilation_errors)}{Style.RESET_ALL}")
                    if fixed_errors:
                        print(f"{Fore.GREEN}✅ Behobene Fehler: {len(fixed_errors)}{Style.RESET_ALL}")
                    
                    # Zeige Memory-Learning Status
                    recurring_errors = self.code_evolution.get_recurring_errors()
                    if recurring_errors:
                        top_error = list(recurring_errors.items())[0]
                        print(f"{Fore.YELLOW}🔄 Häufigster Fehler: {top_error[0][:50]}... ({top_error[1]}x){Style.RESET_ALL}")
                    
                    # Code verbessern für nächste Iteration
                    if iteration < self.max_iterations - 1:
                        current_code = await self.improve_code(client, current_code, review)
                        
                        # Instruction für nächste Iteration aktualisieren
                        evolution_feedback = self.code_evolution.get_targeted_feedback()
                        current_instruction = f"{instruction}\n\nEVOLUTION FEEDBACK:\n{evolution_feedback}\n\nVORHERIGES REVIEW:\n{review[:500]}"
                    else:
                        print(f"\n{Fore.YELLOW}⚠️ Maximum Iterationen erreicht{Style.RESET_ALL}")
                
                # 3. Finale Ergebnisse
                final_validation = await self.validator.comprehensive_validation(current_code)
                ea_file, report_file = self.save_final_results(current_code, final_validation)
                
                # 4. Session Summary
                self.print_session_summary()
                
                print(f"\n{Fore.GREEN}✅ SMART LLM LOOP ABGESCHLOSSEN!{Style.RESET_ALL}")
                
                return {
                    "success": True,
                    "final_code": current_code,
                    "final_score": final_validation['overall'].score,
                    "ea_file": ea_file,
                    "report_file": report_file,
                    "session_id": self.session_id
                }
                
            except Exception as e:
                logger.error(f"Fehler in Smart LLM Loop: {e}")
                print(f"\n{Fore.RED}❌ Fehler: {e}{Style.RESET_ALL}")
                raise

async def main():
    """Hauptfunktion"""
    loop = SmartLLMLoop()
    
    try:
        result = await loop.run(
            strategy="trend_following",  # Kann später konfigurierbar gemacht werden
            target_quality=0.85
        )
        
        if result["success"]:
            print(f"\n{Fore.GREEN}🎯 Expert Advisor erfolgreich generiert!{Style.RESET_ALL}")
            print(f"📄 Datei: {result['ea_file']}")
            print(f"📊 Qualität: {result['final_score']:.1%}")
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️ Benutzer-Abbruch{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}❌ Fataler Fehler: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    asyncio.run(main())
