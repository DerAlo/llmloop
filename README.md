# LLM Loop - Ollama FTMO MQL5 Code Generator

Ein Python-Script das zwei Ollama LLMs orchestriert, um iterativ perfekten FTMO-konformen MQL5 Expert Advisor Code zu entwickeln.

## 🎯 Funktionsweise

Das Script implementiert eine intelligente Kommunikationsschleife zwischen zwei spezialisierten LLMs:

- **qwen3:latest** (Instructor/Reviewer): Gibt Anweisungen und überprüft Code-Qualität
- **qwen2.5-coder:latest** (Code Generator): Generiert und verbessert MQL5 Code

## 🔄 Prozess

1. **Initiale Anweisung**: qwen3 erstellt detaillierte Anforderungen für einen FTMO EA
2. **Code-Generierung**: qwen2.5-coder schreibt MQL5 Code basierend auf den Anweisungen
3. **Code-Review**: qwen3 bewertet den Code nach FTMO-Kriterien und Code-Qualität
4. **Iterative Verbesserung**: Bei Unzufriedenheit wird der Code überarbeitet
5. **Finale Ausgabe**: Perfekter FTMO-konformer Expert Advisor Code

## 📋 FTMO Anforderungen

Das Script berücksichtigt alle wichtigen FTMO Challenge Regeln:
- Maximum Daily Loss: 5%
- Maximum Loss: 10% 
- Profit Target: 10%
- Minimum Trading Days: 5
- Maximum Trading Days: 30
- News Trading und Expert Advisors: Erlaubt

## 🚀 Installation & Setup

### Voraussetzungen

1. **Ollama installiert**: [ollama.ai](https://ollama.ai)
2. **Python 3.8+** installiert
3. **Benötigte Modelle** in Ollama verfügbar:
   ```bash
   ollama pull qwen3:latest
   ollama pull qwen2.5-coder:latest
   ```

### Installation

1. Dependencies installieren:
   ```bash
   pip install -r requirements.txt
   ```

2. Ollama Server starten:
   ```bash
   ollama serve
   ```

3. Script ausführen:
   ```bash
   python llm_loop.py
   ```

## 📊 Output

Das Script generiert:
- **FTMO_Expert_Advisor_[timestamp].mq5**: Finaler MQL5 Code
- **conversation_log_[timestamp].json**: Vollständige Konversation
- **llm_loop.log**: Ausführliche Logs

## ⚙️ Konfiguration

Anpassbare Parameter in `llm_loop.py`:
- `max_iterations`: Maximum Anzahl Verbesserungsiterationen (Standard: 10)
- `instructor_model`: Name des Instructor Modells
- `coder_model`: Name des Coder Modells
- `base_url`: Ollama API URL (Standard: http://localhost:11434)

## 🔧 Features

- **Async/Await**: Effiziente API-Kommunikation
- **Farbiges Terminal**: Übersichtliche Ausgabe mit colorama
- **Umfassendes Logging**: Detaillierte Protokollierung aller Schritte
- **Automatische Speicherung**: Code und Konversation werden automatisch gespeichert
- **Fehlerbehandlung**: Robuste Error-Handling für API-Calls
- **FTMO-Fokus**: Spezialisiert auf FTMO Challenge Anforderungen

## 📝 Beispiel-Workflow

```
🎯 INSTRUCTOR GENERIERT ANFANGSANWEISUNG
↓
💻 CODER GENERIERT MQL5 CODE
↓
🔍 INSTRUCTOR REVIEWT CODE
↓
🔧 CODER VERBESSERT CODE (falls notwendig)
↓
🔄 Wiederholung bis Zufriedenheit
↓
✅ FINALER CODE GESPEICHERT
```

## 🛠️ Troubleshooting

**Ollama nicht erreichbar:**
- Prüfen Sie ob Ollama läuft: `ollama list`
- Server neu starten: `ollama serve`

**Modelle fehlen:**
```bash
ollama pull qwen3:latest
ollama pull qwen2.5-coder:latest
```

**Python Dependencies:**
```bash
pip install --upgrade -r requirements.txt
```

## 📄 Lizenz

Dieses Projekt ist für persönliche und kommerzielle Nutzung freigegeben.
