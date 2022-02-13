import numpy as np
import pandas as pd
import pyDataRetriever as dr
from cvxpy import *


def efficientFrontier(tokens, init_date, end_date, resample=None, fillna=False, dropnaPre=True, infvalue=0, min_return=[0.0001], debug=False):
    try:
        # Import returns (dataframe data type)
        df = retrieveTokensValue(tokens=tokens, init_date=init_date, end_date=end_date, column='Adj Close', resample_value=resample, fillna=fillna, dropnaPre=dropnaPre, returnsCalc=True, dropnaRet=True, infvalue=infvalue)
        if debug:
            print(df)

        # Extract ticket/token names
        symbols = df.columns
        if debug:
            print('symbols')
            print(symbols)

        # Matrix Transpose of returns
        return_data = df.to_numpy().T
        if debug:
            print('return_data')
            print(return_data)

        # Mean matrix of returns
        r = np.array(np.mean(return_data, axis=1))
        if debug:
            print('r')
            print(r)

        # Covariance matrix of renturns
        C = np.matrix(np.cov(return_data))
        if debug:
            print('C')
            print(C)


        df_out = pd.DataFrame()

        # Output of expected returns and risks
        for j in range(len(symbols)):
            if debug:
                print('%s: Exp ret = %f, Risk = %f' % (symbols[j], r[j], C[j, j] ** 0.5))

            d = {'Sym': symbols[j], 'Exp_Return': r[j], 'Risk': C[j, j] ** 0.5}

            df_out = df_out.append(d, ignore_index=True)

        df_out.set_index('Sym', inplace=True)
        if debug:
            print('df_out')
            print(df_out)


        # Optimization
        pfresult_out = pd.DataFrame()
        #investment_out = pd.DataFrame()

        # Iteration for
        for mr in min_return:
            # sviluppare un contenitore di dati per avere un risultato, iterativo con le varie prove


            # Ticker/Tokens count
            n = len(symbols)
            if debug:
                print('n')
                print(n)

            # Variables vectors
            x = Variable(n)
            if debug:
                print('x')
                print(x)

            # Minimum returns request
            req_return = mr
            if debug:
                print('req_return')
                print(req_return)

            # Portfolio returns: transpose matrix of mean multiply variables
            ret = r.T * x
            # bug --> try to use matmul --> deprecated usage of *

            if debug:
                print('ret')
                print(ret)

            # Portfolio risks
            risk = quad_form(x, C)
            if debug:
                print('risk')
                print(risk)

            # Linear Programming:
            # CVXPY Problem definition --> minimal risk
            prob = Problem(Minimize(risk), [sum(x) == 1, ret >= req_return, x >= 0])
            if debug:
                print('prob')
                print(prob)

            prob.solve()

            # Export Data
            if debug:
                print('prob.status')
                print(prob.status)

            df_inv = pd.DataFrame()

            if prob.status == 'optimal':
                pfresult_out = pfresult_out.append({'Min_Returns': str(mr), 'Status Solution': str(prob.status), 'PF Expected Return': round(ret.value, 5), 'PF Expected Risk': round(risk.value ** 0.5, 5)}, ignore_index=True)

                for s in range(len(symbols)):
                    d = {'Sym': symbols[s], 'Investment': round(x.value[s], 5)}
                    df_inv = df_inv.append(d, ignore_index=True)

                df_inv.set_index('Sym', inplace=True)
                df_out[str(mr)] = df_inv['Investment']

            else:
                pfresult_out = pfresult_out.append({'Min_Returns': str(mr), 'Status Solution': str(prob.status), 'PF Expected Return': 0, 'PF Expected Risk': 0}, ignore_index=True)

                for s in range(len(symbols)):
                    d = {'Sym': symbols[s], 'Investment': 'infeasible'}
                    df_inv = df_inv.append(d, ignore_index=True)

                df_inv.set_index('Sym', inplace=True)
                df_out[str(mr)] = df_inv['Investment']

        pfresult_out.set_index(['Min_Returns'], inplace=True)

        if debug:
            print(pfresult_out)
            print('----------')
            print(df_out)

        return pfresult_out, df_out

    except Exception as err:
        return err


def retrieveTokensValue(tokens=None, init_date=None, end_date=None, column='Adj Close', resample_value=None, fillna=None, dropnaPre=True, returnsCalc=False, dropnaRet=True, infvalue=None):
    """
    Extraction from Yahoo Finance
    @ tokens: tickers/tokens list ['ticker1', 'ticker2'...]
    @ init_date: initial date ['yyyy','m','d']
    @ end_date: end date ['yyyy','m','d']
    @ column: extracting column (default 'Adj Close')
    @ resample_Value: dates resampler
    @ fillna: replace NaN with a personalized number
    @ dropnaPre: clean NaN for each iteration
    @ returnsCalc: True/False, automate the calculation of returns
    @ infvalue: replace np.inf, with a preferred number, otherwise, insert NaN value (activated only with returnsCalc = True)
    @ dropnaRet: clean NaN values after returns calc
    """
    try:

        ret_db = pd.DataFrame()

        if tokens is not None:

            # Extract Tickers/Tokens from Yahoo
            for i in tokens:
                pre_db = pd.DataFrame()
                ext_db = dr.getYahooData(i, [init_date[0], init_date[1], init_date[2]], [end_date[0], end_date[1], end_date[2]])

                # Resampling dataframe
                # W --> weekly
                # M --> monthly
                # SM --> half-month
                # Q --> trimestral
                # A --> yearly
                # WS --> week start
                # MS --> month start
                res_list = ['W', 'M', 'SM', 'Q', 'A', 'WS', 'MS']

                if resample_value in res_list:
                    pre_db[i] = ext_db[str(column)].resample(resample_value).last()
                else:
                    pre_db[i] = ext_db[str(column)]

                ret_db[i] = pre_db[i]

            # Fill NaN with a number
            if type(fillna) == float or type(fillna) == int:
                ret_db.fillna(fillna, inplace=True)

            # Clean NaN
            if dropnaPre:
                ret_db.dropna(inplace=True)

            # Calculate the returns
            if returnsCalc:
                ret_db = ret_db.pct_change()

                # Replace the inf values with infvalue, otherwise replace inf with NaN
                if type(infvalue) == float or type(infvalue) == int:
                    ret_db.replace([np.inf, -np.inf], infvalue, inplace=True)
                else:
                    ret_db.replace([np.inf, -np.inf], np.nan, inplace=True)

                # If fillna is a number, replace NaN with this number
                if type(fillna) == float or type(fillna) == int:
                    ret_db.fillna(fillna, inplace=True)

                # Delete rows with NaN
                if dropnaRet:
                    ret_db.dropna(inplace=True)

        return ret_db
    except Exception as err:
        return err
