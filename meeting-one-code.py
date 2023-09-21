import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Define ETF symbols and the backtesting time period
etf_symbols = ['SPY', 'SH']
start_date = '2010-01-01'
end_date = '2021-12-31'

# Fetch historical ETF price data
etf_data = yf.download(etf_symbols, start=start_date, end=end_date, adjusted=True)

# Initialize trading variables
position = 0  # 0: No position, 1: Long SH, -1: Short SH
trades = []

alpha = 1.05

# Implement the pairs-trading strategy
for i in range(1, len(etf_data)):
    spy_prices = etf_data['Close']['SPY']
    sh_prices = etf_data['Close']['SH']
    
    spy_price_today, sh_price_today = spy_prices[i], sh_prices[i]
    spy_price_yesterday, sh_price_yesterday = spy_prices[i - 1], sh_prices[i - 1]

    if position == 0:
        # Check entry condition: Both SPY and SH move up
        if spy_price_today > spy_price_yesterday and sh_price_today > sh_price_yesterday:
            position = -1  # Short SH
            entry_price = sh_price_today
    elif position == -1:
        # Check exit condition: SH falls below entry price
        if alpha * sh_price_today < entry_price:
            position = 0  # Close position
            exit_price = sh_price_today
            trade_profit = entry_price - exit_price
            trades.append({'Exit Date': etf_data.index[i],
                           'Entry Price': entry_price,
                           'Exit Price': exit_price,
                           'Profit': trade_profit,
                           'Percentage Profit': trade_profit / entry_price * 100})

# Calculate strategy statistics
trades_df = pd.DataFrame(trades)
trades_df.set_index('Exit Date', inplace=True)

if not trades_df.empty:
    total_profit = trades_df['Profit'].sum()
    num_trades = len(trades_df)
    average_profit_per_trade = total_profit / num_trades
    win_ratio = (trades_df['Profit'] > 0).sum() / num_trades
    cumulative_percentage_profit = (trades_df['Percentage Profit']).cumsum()
else:
    total_profit = 0
    num_trades = 0
    average_profit_per_trade = 0
    win_ratio = 0

# Print strategy statistics
print("Pairs Trading Strategy Results")
print("==============================")
print(f"Total Profit: ${total_profit:.2f}")
print(f"Number of Trades: {num_trades}")
print(f"Average Profit per Trade: ${average_profit_per_trade:.2f}")
print(f"Win Ratio: {win_ratio * 100:.2f}%")
print(f"Cumulative Percentage Profit: {cumulative_percentage_profit.iloc[-1]:.2f}%")

# Convert S&P prices to percentage returns
spy_returns = etf_data['Close']['SPY'].pct_change()

# Plot the spread and entry/exit points
plt.figure(figsize=(12, 6))
plt.plot(cumulative_percentage_profit, label='Pairs Trading Strategy')
plt.plot(spy_returns.cumsum() * 100, label='SPY')
plt.title('Pairs Trading Strategy vs. SPY')
plt.legend()
plt.show()
