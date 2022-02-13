# pyFinance
Data extract, transform and Markowitz Efficient Frontier calculation

This tool, lets the people to retrieve data from yahoo finance and lets to calculate the efficient frontier, after a targeted minimal return expected.

Usage:

```
from pyFinanceLP import *

portfoliotk = ['GOOGL', 'AMZN', 'MSFT', 'AAPL','NFLX']
init_date = [2021,1,1]
end_date = [2022,1,31]
trials = [0.005, 0.006, 0.007, 0.008, 0.01]

x = efficientFrontier(portfoliotk, init_date, end_date, resample='W', fillna=False, dropnaPre=True, infvalue=0, min_return=trials, debug=False)

print(x[0])
print(x[1])
```

