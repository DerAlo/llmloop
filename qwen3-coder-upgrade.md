# Qwen3-Coder Upgrade Notizen

## Warum das Upgrade?
- Nach 40 Iterationen mit qwen2.5-coder immer noch Qualitätsprobleme
- qwen3-coder:30b ist speziell für Code-Generierung optimiert
- 30B Parameter vs. 7B = deutlich bessere Code-Qualität erwartet

## Vorteile Qwen3-Coder-30B:
- Modernste Code-Generation (seit gestern verfügbar)
- Optimiert für komplexe Programming Tasks
- Besseres Verständnis von MQL5 Syntax
- Weniger Syntax-Fehler erwartet

## RTX 3090 Performance:
- 24GB VRAM sollte für 30B Modell ausreichen
- Quantisierung auf ~18GB komprimiert
- Erwartet: Deutlich bessere Ausgaben als qwen2.5-coder

## Nächste Schritte:
1. Download abwarten (~1 Minute)
2. Neuen LLM Loop mit qwen3-coder starten
3. Vergleichen: Weniger Iterationen bis perfekter Code?
4. Erwartung: Kompilierbarer Code in ersten Versuchen

## MQL5 Syntax Verbesserungen im Prompt:
- ORDER_TYPE_BUY statt OP_BUY
- AccountInfoDouble() korrekte Syntax
- SymbolInfoDouble() korrekte Parameter
- MqlTradeRequest/MqlTradeResult Strukturen
- Korrekte iMA() Parameter
