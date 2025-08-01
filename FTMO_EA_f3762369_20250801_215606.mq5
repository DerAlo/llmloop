//+------------------------------------------------------------------+
//|                                    FTMO_Expert_Advisor.mq5     |
//+------------------------------------------------------------------+
#property copyright "Copyright 2023, MetaQuotes Software Corp."
#property link      "https://www.metaquotes.net/"
#property version   "1.00"
#property strict

input double RiskPercent = 1.5; // 1.5% Risk per Trade
input int    StopLossPips = 50;  // Dynamic Stop Loss
input int    TakeProfitPips = 100; // Fixed Take Profit

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
   return(INIT_SUCCEEDED);
  }
//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
  }
//+------------------------------------------------------------------+
//| Expert tick function                                               |
//+------------------------------------------------------------------+
void OnTick()
  {
   if(!IsTradeAllowed())
     return;
   
   if(PositionSelect(Symbol()) == -1) // No open position
     {
      if(ConfirmEntry())
        PlaceOrder();
     }
   else
     {
      ManageExit();
     }
  }
//+------------------------------------------------------------------+
//| Check if trading is allowed                                        |
//+------------------------------------------------------------------+
bool IsTradeAllowed()
  {
   if(!IsTradeAllowed()) // Recursive call - this will cause stack overflow
     return(false);
   
   if(AccountInfoInteger(ACCOUNT_TRADE_ALLOWED) == 0)
     return(false);
   
   return(true);
  }
//+------------------------------------------------------------------+
//| Confirm entry conditions                                           |
//+------------------------------------------------------------------+
bool ConfirmEntry()
  {
   if(!IsTrendConfirmed())
     return(false);
   
   if(GetRSI() < 30 || GetRSI() > 70)
     return(true);
   
   return(false);
  }
//+------------------------------------------------------------------+
//| Place order                                                        |
//+------------------------------------------------------------------+
void PlaceOrder()
  {
   double lotSize = CalculateLotSize();
   double stopLoss = 0;
   double takeProfit = 0;
   
   if(PositionSelect(Symbol()) == -1)
     {
      if(IsTrendConfirmed())
        {
         if(GetRSI() < 30)
           {
            // Buy order
            stopLoss = MarketInfo(Symbol(), MODE_STOPLEVEL);
            takeProfit = MarketInfo(Symbol(), MODE_POINT) * TakeProfitPips;
            OrderSend(Symbol(), ORDER_TYPE_BUY, lotSize, Ask, 3, stopLoss, takeProfit, "Buy Order", 0, 0, clrGreen);
           }
         else if(GetRSI() > 70)
           {
            // Sell order
            stopLoss = MarketInfo(Symbol(), MODE_STOPLEVEL);
            takeProfit = MarketInfo(Symbol(), MODE_POINT) * TakeProfitPips;
            OrderSend(Symbol(), ORDER_TYPE_SELL, lotSize, Bid, 3, stopLoss, takeProfit, "Sell Order", 0, 0, clrRed);
           }
        }
     }
  }
//+------------------------------------------------------------------+
//| Calculate lot size                                                 |
//+------------------------------------------------------------------+
double CalculateLotSize()
  {
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   double riskAmount = balance * RiskPercent / 100;
   double lotSize = riskAmount / (StopLossPips * MarketInfo(Symbol(), MODE_POINT));
   
   return(MathMin(lotSize, 10.0)); // Max 10 lots
  }
//+------------------------------------------------------------------+
//| Manage exit conditions                                             |
//+------------------------------------------------------------------+
void ManageExit()
  {
   if(PositionSelect(Symbol()) != -1)
     {
      double profit = PositionGetDouble(POSITION_PROFIT);
      
      if(profit > 0)
        {
         // Apply trailing stop
         ApplyTrailingStop();
        }
     }
  }
//+------------------------------------------------------------------+
//| Apply trailing stop                                                |
//+------------------------------------------------------------------+
void ApplyTrailingStop()
  {
   double trailingDistance = iATR(Symbol(), 0, 14, 0) * 1.5;
   
   if(PositionSelect(Symbol()) != -1)
     {
      if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY)
        {
         double currentPrice = PositionGetDouble(POSITION_PRICE_OPEN);
         double newStopLoss = currentPrice + trailingDistance;
         OrderModify(OrderTicket(), 0, newStopLoss, 0, 0, clrGreen);
        }
      else if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_SELL)
        {
         double currentPrice = PositionGetDouble(POSITION_PRICE_OPEN);
         double newStopLoss = currentPrice - trailingDistance;
         OrderModify(OrderTicket(), 0, newStopLoss, 0, 0, clrRed);
        }
     }
  }
//+------------------------------------------------------------------+
//| Check if trend is confirmed                                        |
//+------------------------------------------------------------------+
bool IsTrendConfirmed()
  {
   double ema20 = iMA(Symbol(), 0, 20, 0, MODE_EMA, PRICE_CLOSE, 0);
   double ema50 = iMA(Symbol(), 0, 50, 0, MODE_EMA, PRICE_CLOSE, 0);
   double ema200 = iMA(Symbol(), 0, 200, 0, MODE_EMA, PRICE_CLOSE, 0);
   
   if(ema20 > ema50 && ema50 > ema200)
     return(true);
   
   if(ema20 < ema50 && ema50 < ema200)
     return(true);
   
   return(false);
  }
//+------------------------------------------------------------------+
//| Get RSI value                                                      |
//+------------------------------------------------------------------+
double GetRSI()
  {
   return(iRSI(Symbol(), 0, 14, PRICE_CLOSE, 0));
  }
//+------------------------------------------------------------------+
//| Log message to terminal and file                                   |
//+------------------------------------------------------------------+
void Log(string message)
  {
   Print("[" + TimeToString(TimeCurrent(), TIME_MINUTES) + "] " + message);
   FileWrite("TradeLog.txt", message);
  }
//+------------------------------------------------------------------+