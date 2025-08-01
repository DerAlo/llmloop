//+------------------------------------------------------------------+
//|                                                   TestEA.mq5 |
//|                                  Copyright 2025, MetaQuotes Software Corp. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2025, MetaQuotes Software Corp."
#property link      "https://www.mql5.com"
#property version   "1.00"

input double LotSize = 0.01;
input int StopLoss = 50;

int OnInit()
{
    Print("Test EA initialisiert");
    return(INIT_SUCCEEDED);
}

void OnDeinit(const int reason)
{
    Print("Test EA beendet");
}

void OnTick()
{
    double balance = AccountInfoDouble(ACCOUNT_BALANCE);
    if(balance > 0)
    {
        Print("Balance: ", balance);
    }
}
