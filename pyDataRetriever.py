import pandas as pd
import pandas_datareader.data as web
import datetime as dt


def getYahooData(ticker, init_date, end_date, column_isolation=None, provider='yahoo'):
    """
    @ticker --> name of title
    @init_date --> [<year>,<month>,<day>]
    @end_date --> [<year>,<month>,<day>]
    @column_isolation --> ['column a', 'column b'...]
    @provider --> default 'yahoo'

    Columns:
    High, Low, Open, Close, Volume, Adj Close
    """
    try:
        yahoo_ticker = ticker
        start_date = dt.datetime(init_date[0], init_date[1], init_date[2])
        end_date = dt.datetime(end_date[0], end_date[1], end_date[2])

        df_export = pd.DataFrame()

        df = web.DataReader(yahoo_ticker, provider, start_date, end_date)

        # Extract only the preferred column(s)
        if column_isolation is not None:
            df_export[column_isolation] = df[column_isolation]
        else:
            df_export = df

        return df_export

    except Exception as err:
        return err
