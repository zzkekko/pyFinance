from pyFinanceLP import *

print('Portfolio Tickers/Token')
tk_tech = ['GOOGL', 'AMZN', 'MSFT', 'AAPL','NFLX']
print(tk_tech)
print('-------------------')

# Linear Programming Calculation
x = efficientFrontier(tk_tech, [2021, 1, 1], [2022, 12, 31], resample='W', dropnaPre=True, debug=False, min_return=[0.005, 0.006, 0.007, 0.008, 0.01])

print('Iteration & Result')
print(x[0])
print('-------------------')
print('Efficient Portfolio for each iteration - Values are the tickers distribution')
print(x[1])
