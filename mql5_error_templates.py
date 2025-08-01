"""
PHASE 1: Spezifische MQL5 Syntax-Fehler Templates
================================================

Häufigste MQL5 Fehler und ihre bewährten Lösungen
"""

class MQL5ErrorTemplates:
    """Spezifische Templates für häufige MQL5 Syntax-Fehler"""
    
    # MarketInfo → SymbolInfoDouble Templates
    MARKETINFO_FIXES = {
        'MarketInfo(_Symbol, MODE_SPREAD)': 'SymbolInfoInteger(_Symbol, SYMBOL_SPREAD)',
        'MarketInfo(_Symbol, MODE_ASK)': 'SymbolInfoDouble(_Symbol, SYMBOL_ASK)',
        'MarketInfo(_Symbol, MODE_BID)': 'SymbolInfoDouble(_Symbol, SYMBOL_BID)',
        'MarketInfo(_Symbol, MODE_POINT)': 'SymbolInfoDouble(_Symbol, SYMBOL_POINT)',
        'MarketInfo(_Symbol, MODE_TICKVALUE)': 'SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE)',
        'MarketInfo(_Symbol, MODE_TICKSIZE)': 'SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE)',
        'MarketInfo(_Symbol, MODE_LOTSIZE)': 'SymbolInfoDouble(_Symbol, SYMBOL_TRADE_CONTRACT_SIZE)',
        'MarketInfo(_Symbol, MODE_MINLOT)': 'SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN)',
        'MarketInfo(_Symbol, MODE_MAXLOT)': 'SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX)',
        'MarketInfo(_Symbol, MODE_LOTSTEP)': 'SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP)',
    }
    
    # Order Management Templates  
    ORDER_FIXES = {
        'OP_BUY': 'ORDER_TYPE_BUY',
        'OP_SELL': 'ORDER_TYPE_SELL',
        'OP_BUYLIMIT': 'ORDER_TYPE_BUY_LIMIT',
        'OP_SELLLIMIT': 'ORDER_TYPE_SELL_LIMIT',
        'OP_BUYSTOP': 'ORDER_TYPE_BUY_STOP',
        'OP_SELLSTOP': 'ORDER_TYPE_SELL_STOP',
        'OrderSend(': 'trade.Buy(' if 'BUY' in 'ORDER_TYPE_BUY' else 'trade.Sell(',
        'OrderClose(': 'trade.PositionClose(',
        'OrderModify(': 'trade.PositionModify(',
        'OrdersTotal()': 'PositionsTotal()',
        'OrderSelect(': 'PositionSelect(',
    }
    
    # Account & Global Variables  
    ACCOUNT_FIXES = {
        'AccountBalance()': 'AccountInfoDouble(ACCOUNT_BALANCE)',
        'AccountEquity()': 'AccountInfoDouble(ACCOUNT_EQUITY)',
        'AccountMargin()': 'AccountInfoDouble(ACCOUNT_MARGIN)',
        'AccountFreeMargin()': 'AccountInfoDouble(ACCOUNT_MARGIN_FREE)',
        'AccountProfit()': 'AccountInfoDouble(ACCOUNT_PROFIT)',
        'Ask': 'SymbolInfoDouble(_Symbol, SYMBOL_ASK)',
        'Bid': 'SymbolInfoDouble(_Symbol, SYMBOL_BID)',
        'Point': 'SymbolInfoDouble(_Symbol, SYMBOL_POINT)',
        'Digits': 'SymbolInfoInteger(_Symbol, SYMBOL_DIGITS)',
    }
    
    # Include & Property Fixes
    HEADER_FIXES = {
        '#include <Trade\\Trade.mqh>': '#include <Trade\\\\Trade.mqh>',
        '#include <Trade/Trade.mqh>': '#include <Trade\\\\Trade.mqh>', 
        'property copyright': '#property copyright',
        'property version': '#property version',
        'property link': '#property link',
        'property description': '#property description',
        'property strict': '#property strict',
    }
    
    # Indicator Fixes
    INDICATOR_FIXES = {
        'iMA(': 'iMA(_Symbol, _Period, ',
        'iRSI(': 'iRSI(_Symbol, _Period, ',
        'iMACD(': 'iMACD(_Symbol, _Period, ',
        'iATR(': 'iATR(_Symbol, _Period, ',
        'iBands(': 'iBands(_Symbol, _Period, ',
        'iStochastic(': 'iStochastic(_Symbol, _Period, ',
    }
    
    # FTMO-spezifische Templates
    FTMO_TEMPLATES = {
        'daily_loss_check': '''
bool CheckDailyLoss() {
    double currentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
    double dailyLoss = (dailyStartBalance - currentEquity) / dailyStartBalance * 100.0;
    if(dailyLoss > MaxDailyLoss) {
        Print("Daily loss limit exceeded: ", dailyLoss, "%");
        return false;
    }
    return true;
}''',
        
        'total_loss_check': '''
bool CheckTotalLoss() {
    double currentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
    double totalLoss = (startBalance - currentEquity) / startBalance * 100.0;
    if(totalLoss > MaxTotalLoss) {
        Print("Total loss limit exceeded: ", totalLoss, "%");
        return false;
    }
    return true;
}''',
        
        'position_sizing': '''
double CalculatePositionSize(double riskAmount, double stopLossPoints) {
    double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
    double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
    double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
    
    double riskPerPoint = (tickValue / tickSize) * point;
    double lotSize = riskAmount / (stopLossPoints * riskPerPoint);
    
    double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
    double maxLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
    double stepLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
    
    lotSize = MathMax(lotSize, minLot);
    lotSize = MathMin(lotSize, maxLot);
    lotSize = NormalizeDouble(lotSize / stepLot, 0) * stepLot;
    
    return lotSize;
}'''
    }
    
    @classmethod
    def apply_all_fixes(cls, code: str) -> tuple[str, list[str]]:
        """Wendet alle Template-Fixes auf den Code an"""
        
        fixed_code = code
        applied_fixes = []
        
        # Alle Fix-Kategorien durchgehen
        fix_categories = [
            ('MarketInfo', cls.MARKETINFO_FIXES),
            ('Orders', cls.ORDER_FIXES),
            ('Account', cls.ACCOUNT_FIXES),
            ('Headers', cls.HEADER_FIXES), 
            ('Indicators', cls.INDICATOR_FIXES)
        ]
        
        for category, fixes in fix_categories:
            for old_pattern, new_pattern in fixes.items():
                if old_pattern in fixed_code:
                    fixed_code = fixed_code.replace(old_pattern, new_pattern)
                    applied_fixes.append(f"{category}: {old_pattern} → {new_pattern}")
        
        return fixed_code, applied_fixes
    
    @classmethod 
    def add_missing_ftmo_functions(cls, code: str) -> str:
        """Fügt fehlende FTMO-Funktionen hinzu"""
        
        # Prüfe welche FTMO-Funktionen fehlen
        missing_functions = []
        
        if 'CheckDailyLoss()' in code and 'bool CheckDailyLoss()' not in code:
            missing_functions.append('daily_loss_check')
            
        if 'CheckTotalLoss()' in code and 'bool CheckTotalLoss()' not in code:
            missing_functions.append('total_loss_check')
            
        if 'CalculatePositionSize(' in code and 'double CalculatePositionSize(' not in code:
            missing_functions.append('position_sizing')
        
        # Füge fehlende Funktionen vor der letzten Klammer hinzu
        if missing_functions:
            # Finde die Position vor der letzten schließenden Klammer
            last_brace_pos = code.rfind('}')
            if last_brace_pos > 0:
                # Füge die Funktionen ein
                functions_to_add = '\n\n'.join([cls.FTMO_TEMPLATES[func] for func in missing_functions])
                code = code[:last_brace_pos] + '\n\n' + functions_to_add + '\n' + code[last_brace_pos:]
        
        return code
