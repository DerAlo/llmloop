"""
Utility Script für Ollama Model Management
==========================================

Überprüft die Verfügbarkeit der benötigten Ollama Modelle
und hilft beim Setup.
"""

import asyncio
import json
import subprocess
import sys
from typing import List, Dict

import aiohttp
import colorama
from colorama import Fore, Style

colorama.init()

class OllamaChecker:
    """Überprüft Ollama Installation und Modelle"""
    
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.required_models = ["qwen3:latest", "qwen2.5-coder:latest"]
    
    def check_ollama_installation(self) -> bool:
        """Überprüft ob Ollama installiert ist"""
        try:
            result = subprocess.run(["ollama", "--version"], 
                                 capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"{Fore.GREEN}✅ Ollama ist installiert: {result.stdout.strip()}{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}❌ Ollama nicht gefunden{Style.RESET_ALL}")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print(f"{Fore.RED}❌ Ollama nicht installiert oder nicht im PATH{Style.RESET_ALL}")
            return False
    
    async def check_ollama_server(self) -> bool:
        """Überprüft ob Ollama Server läuft"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/version", timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"{Fore.GREEN}✅ Ollama Server läuft (Version: {data.get('version', 'unknown')}){Style.RESET_ALL}")
                        return True
                    else:
                        print(f"{Fore.RED}❌ Ollama Server antwortet nicht korrekt{Style.RESET_ALL}")
                        return False
        except Exception as e:
            print(f"{Fore.RED}❌ Ollama Server nicht erreichbar: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}💡 Starte Ollama mit: ollama serve{Style.RESET_ALL}")
            return False
    
    async def list_available_models(self) -> List[str]:
        """Listet verfügbare Ollama Modelle auf"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        models = [model["name"] for model in data.get("models", [])]
                        return models
                    else:
                        print(f"{Fore.RED}❌ Kann Modelle nicht abrufen{Style.RESET_ALL}")
                        return []
        except Exception as e:
            print(f"{Fore.RED}❌ Fehler beim Abrufen der Modelle: {e}{Style.RESET_ALL}")
            return []
    
    def check_required_models(self, available_models: List[str]) -> Dict[str, bool]:
        """Überprüft ob alle benötigten Modelle verfügbar sind"""
        model_status = {}
        
        print(f"\n{Fore.CYAN}Überprüfe benötigte Modelle:{Style.RESET_ALL}")
        
        for model in self.required_models:
            is_available = model in available_models
            status = "✅" if is_available else "❌"
            color = Fore.GREEN if is_available else Fore.RED
            print(f"{color}{status} {model}{Style.RESET_ALL}")
            model_status[model] = is_available
        
        return model_status
    
    def suggest_missing_models(self, model_status: Dict[str, bool]):
        """Schlägt Befehle vor, um fehlende Modelle zu installieren"""
        missing_models = [model for model, available in model_status.items() if not available]
        
        if missing_models:
            print(f"\n{Fore.YELLOW}Fehlende Modelle installieren:{Style.RESET_ALL}")
            for model in missing_models:
                print(f"{Fore.CYAN}ollama pull {model}{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.GREEN}🎉 Alle benötigten Modelle sind verfügbar!{Style.RESET_ALL}")
    
    async def run_diagnostics(self):
        """Führt eine vollständige Diagnose durch"""
        print(f"{Fore.CYAN}🔍 LLM Loop - Ollama Diagnose{Style.RESET_ALL}")
        print("=" * 50)
        
        # 1. Ollama Installation prüfen
        print(f"\n{Fore.YELLOW}1. Ollama Installation prüfen:{Style.RESET_ALL}")
        if not self.check_ollama_installation():
            print(f"{Fore.RED}❌ Bitte installiere Ollama von: https://ollama.ai{Style.RESET_ALL}")
            return False
        
        # 2. Ollama Server prüfen
        print(f"\n{Fore.YELLOW}2. Ollama Server prüfen:{Style.RESET_ALL}")
        if not await self.check_ollama_server():
            return False
        
        # 3. Verfügbare Modelle abrufen
        print(f"\n{Fore.YELLOW}3. Verfügbare Modelle abrufen:{Style.RESET_ALL}")
        available_models = await self.list_available_models()
        
        if available_models:
            print(f"{Fore.GREEN}Verfügbare Modelle ({len(available_models)}):{Style.RESET_ALL}")
            for model in available_models:
                print(f"  - {model}")
        else:
            print(f"{Fore.RED}❌ Keine Modelle gefunden{Style.RESET_ALL}")
            return False
        
        # 4. Benötigte Modelle prüfen
        print(f"\n{Fore.YELLOW}4. Benötigte Modelle prüfen:{Style.RESET_ALL}")
        model_status = self.check_required_models(available_models)
        self.suggest_missing_models(model_status)
        
        # 5. Fazit
        all_available = all(model_status.values())
        if all_available:
            print(f"\n{Fore.GREEN}🎉 System ist bereit für LLM Loop!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Starte das Script mit: python llm_loop.py{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.YELLOW}⚠️ Bitte installiere die fehlenden Modelle vor dem Start{Style.RESET_ALL}")
        
        return all_available

async def main():
    """Hauptfunktion"""
    checker = OllamaChecker()
    await checker.run_diagnostics()

if __name__ == "__main__":
    asyncio.run(main())
