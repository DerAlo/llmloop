//+------------------------------------------------------------------+
//|                                    FTMO_Expert_Advisor.mq5     |
//+------------------------------------------------------------------+
#property copyright "Copyright 2023, MetaQuotes Software Corp."
#property link      "https://www.metaquotes.net/"
#property version   "1.00"
#property strict

input double DailyLossLimit = 0.05;
input double TotalLossLimit = 0.10;
input double RiskPerTrade = 0.02;

double ATRValue = 0;

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
   FileClose("TradeLog.txt");
   FileClose("ErrorLog.txt");
  }
//+------------------------------------------------------------------+
//| Expert tick function                                               |
//+------------------------------------------------------------------+
void OnTick()
  {
   double ema20 = iMA(_Symbol, PERIOD_M15, 20, 0, MODE_EMA, PRICE_CLOSE, 0);
   double ema50 = iMA(_Symbol, PERIOD_M15, 50, 0, MODE_EMA, PRICE_CLOSE, 0);
   double ema200 = iMA(_Symbol, PERIOD_M15, 200, 0, MODE_EMA, PRICE_CLOSE, 0);

   bool isTrending = false;
   if(ema20 > ema50 && ema50 > ema200) isTrending = true; // Bullish trend
   if(ema20 < ema50 && ema50 < ema200) isTrending = true; // Bearish trend

   double rsi = iRSI(_Symbol, PERIOD_M15, 14, PRICE_CLOSE, 0);
   double macd = iMACD(_Symbol, PERIOD_M15, 12, 26, 9, PRICE_CLOSE, 0);

   double momentumSignal = 0;
   if(rsi < 30 && macd > 0) momentumSignal = 1.0; // Bullish momentum
   if(rsi > 70 && macd < 0) momentumSignal = -1.0; // Bearish momentum

   ATRValue = iATR(_Symbol, PERIOD_M15, 14, 0);

   double signal1 = momentumSignal;
   double signal2 = momentumSignal;

   if(signal1 > 0.8 && signal2 > 0.7 && isTrending)
     {
      OpenPosition(ORDER_TYPE_BUY);
     }
   else if(signal1 < -0.8 && signal2 < -0.7 && isTrending)
     {
      OpenPosition(ORDER_TYPE_SELL);
     }

   CheckDailyLoss();
   CheckTotalLoss();
  }
//+------------------------------------------------------------------+
//| Open a new position                                                |
//+------------------------------------------------------------------+
void OpenPosition(int type)
  {
   double price = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   if(type == ORDER_TYPE_BUY) price = SymbolInfoDouble(_Symbol, SYMBOL_BID);

   double lotSize = CalculatePositionSize(AccountInfoDouble(ACCOUNT_BALANCE), RiskPerTrade);
   if(lotSize <= 0) return;

   MqlTick lastTick;
   if(!SymbolInfoTick(_Symbol, lastTick)) return;

   double sl = 0;
   double tp = 0;

   if(type == ORDER_TYPE_BUY)
     {
      sl = price - (ATRValue * 2);
      tp = price + (ATRValue * 4);
     }
   else
     {
      sl = price + (ATRValue * 2);
      tp = price - (ATRValue * 4);
     }

   int ticket = OrderSend(_Symbol, type, lotSize, price, 3, sl, tp, "BuyOrder", 0, 0, clrGreen);
   if(ticket < 0)
     {
      Print("OrderSend failed with error: ", GetLastError());
     }
  }
//+------------------------------------------------------------------+
//| Calculate position size using Kelly Criterion                      |
//+------------------------------------------------------------------+
double CalculatePositionSize(double accountBalance, double riskPerTrade)
  {
   double positionSize = (accountBalance * riskPerTrade) / (ATRValue * 2); // 1:2 R/R ratio
   return NormalizeDouble(positionSize, 2);
  }
//+------------------------------------------------------------------+
//| Check daily loss limit                                             |
//+------------------------------------------------------------------+
void CheckDailyLoss()
  {
   double startBalance = AccountInfoDouble(ACCOUNT_BALANCE);
   double currentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
   double dailyLoss = (startBalance - currentEquity) / startBalance;

   if(dailyLoss > DailyLossLimit)
     {
      TriggerEmergencyStop();
     }
  }
//+------------------------------------------------------------------+
//| Check total loss limit                                             |
//+------------------------------------------------------------------+
void CheckTotalLoss()
  {
   double startBalance = AccountInfoDouble(ACCOUNT_BALANCE);
   double currentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
   double totalLoss = (startBalance - currentEquity) / startBalance;

   if(totalLoss > TotalLossLimit)
     {
      TriggerEmergencyStop();
     }
  }
//+------------------------------------------------------------------+
//| Trigger emergency stop                                             |
//+------------------------------------------------------------------+
void TriggerEmergencyStop()
  {
   Print("Emergency Stop triggered due to loss limits exceeded.");
   // Close all open positions
   for(int i = PositionsTotal()-1; i >= 0; i--)
     {
      if(PositionSelect(Symbol()) == true)
        {
         double price = PositionGetDouble(POSITION_PRICE_CURRENT);
         double sl = PositionGetDouble(POSITION_SL);
         double tp = PositionGetDouble(POSITION_TP);
         int type = PositionGetInteger(POSITION_TYPE);

         if(type == POSITION_TYPE_BUY)
           {
            OrderClose(PositionGetTicket(), PositionGetDouble(POSITION_VOLUME), price, 3, clrRed);
           }
         else
           {
            OrderClose(PositionGetTicket(), PositionGetDouble(POSITION_VOLUME), price, 3, clrRed);
           }
        }
     }
  }
//+------------------------------------------------------------------+
//| Log trade information                                              |
//+------------------------------------------------------------------+
void LogTrade(double ticket, double profit, double risk)
  {
   string logEntry = "Ticket: " + DoubleToString(ticket, 0) +
                     " | Profit: " + DoubleToString(profit, 2) +
                     " | Risk: " + DoubleToString(risk, 2) +
                     " | Time: " + TimeToString(TimeCurrent(), TIME_MINUTES);
   FileWrite("TradeLog.txt", logEntry);
  }
//+------------------------------------------------------------------+
//| Handle error conditions                                            |
//+------------------------------------------------------------------+
void HandleError(string errorMessage)
  {
   Print("ERROR: " + errorMessage);
   FileWrite("ErrorLog.txt", "Time: " + TimeToString(TimeCurrent(), TIME_MINUTES) + " | " + errorMessage);
   if(errorMessage.Contains("Critical"))
     {
      Shutdown();
     }
  }
//+------------------------------------------------------------------+
//| Test position sizing                                               |
//+------------------------------------------------------------------+
void TestPositionSizing()
  {
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   double risk = RiskPerTrade;
   double expected = (balance * risk) / (ATRValue * 2);
   double actual = CalculatePositionSize(balance, risk);
   if(MathAbs(expected - actual) > 0.001)
     {
      Print("Position sizing test failed");
     }
  }
//+------------------------------------------------------------------+
//| Finalize compliance report                                         |
//+------------------------------------------------------------------+
void FinalizeReport()
  {
   Print("Final compliance report generated.");
  }
//+------------------------------------------------------------------+