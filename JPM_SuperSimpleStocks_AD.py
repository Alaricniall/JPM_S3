# -*- coding: utf-8 -*-
"""
This is written in Python3
numpy version 1.13.3
datetime 3.6
"""
# %% Import
import numpy as np
import datetime

np.random.seed(42)  # Initialse random seed for reproducability.

# %% Required definitions


def GeometricMean(iterable):
    """
    Function takes an iterable and calculates the geometric mean, which is
    the nth root of the product of the iterable.
    """
    a = np.array(iterable)
    return a.prod()**(1.0/len(a))


def LastFiveMins(Array):
    """
    Extracts the last five minutes from the History array that is generated in
    the Stock class. Utilises the fact that the timestamp is stored as POSIX
    time in seconds.
    """
    LatestTime = Array[-1, 0]
    Seconds = 5 * 60
    Count = 1
    while Array[-Count, 0] != LatestTime - Seconds:
        Count += 1
    return Array[-Count:, :]


class Stock(object):
    """
    Stock class object which contains all the information regarding
    transactions and possible dividend payouts. I don't know much about the
    technicalities of stocks and so it is purely based off the PDF provided.

    Involves the Trade, DividendYield, and VolWeighted_StockPrice methods,
    which calculates the relevent statistic.
    """
    # Local class based variables which I've used just to index the History
    # array. Can be changed if it's ever required to reorder them, and when
    # writing it isn't necessary to remember what number it is, just the name.
    _Time_History = 0
    _Price_History = 1
    _Quantity_History = 2
    _BuySell_History = 3
    _Dividend_History = 4

    def __init__(self, timestamp, Name, Type,
                 ParVal, Last_Dividend, Fixed_Dividend):
        """
        Initialise the object with the relevent data using an np array to
        store.
        """
        self.History = np.array([0, 0, 0, 0, 0], ndmin=2)
        # storing it as unix epoch time for convenience
        self.History[0, 0] = datetime.datetime.timestamp(timestamp)
        self.Name = Name
        # I'm not sure what Par Value is.
        self.ParVal = ParVal
        # No real reason to have the checks for the percentage put in
        # at this point or at all, but it popped into my head at the time, and
        # there was no reason to not do it.
        if Last_Dividend < 1:
            Last_Dividend *= 100  # assuming whole % so Align to 1
            self.History[0, 4] = Last_Dividend
        else:
            self.History[0, 4] = Last_Dividend
        if Fixed_Dividend < 1:
            Fixed_Dividend *= 100
            self.Fixed_Div = Fixed_Dividend
        else:
            self.Fixed_Div = Fixed_Dividend
        # Forcing to lower case to make comparison easier,
        if Type.lower() == "preferred":
            self.Type = 1
        elif Type.lower() == "common":
            self.Type = 0
        else:
            raise Exception('Type is not "Common" or "Preferred".')

    def Trade(self, timestamp, Price, Quantity, BuySell, Dividend):
        """
        The trade method takes these inputs and stores them in an array.
        From this is is possible to reconstruct the trading for a day or
        however long it's needed. Append isn't a good way to do this, as it's
        pretty ineffiecient, but without better information about how the data
        comes in, it works in this situation.
        """
        # Converting Buy to 1 and Sell to 0
        if BuySell == 'Buy':
            BuySell = 1
        else:
            BuySell = 0
        if not Dividend:
            Dividend = self.History[-1, self._Dividend_History]
        # Appending to array.
        self.History = np.append(self.History, [[
                                     datetime.datetime.timestamp(timestamp),
                                     Price,
                                     Quantity,
                                     BuySell,
                                     Dividend]],
                                 axis=0)

    def DividendYield(self, Price=0):
        """
        Calculates the Dividend Yield for this stock for a given price. If no
        price is given, it will just used the latest known value.
        """
        if self.Type == 1:
            if Price and Price > 0:
                return self.Fixed_Div * self.ParVal / Price
            else:
                return (self.Fixed_Div * self.ParVal /
                        self.History[-1, self._Price_History])
        else:
            if Price and Price > 0:
                return self.History[-1, self._Dividend_History] / Price
            else:
                return (self.History[-1, self._Dividend_History] /
                        self.History[-1, self._Price_History])

    def PE_Ratio(self, Price=0):
        '''
        P/E ratio is calculated for a given price, using historical data, which
        uses the correct equation depending on Type.
        Similarly to the Dividend yield, if no price is supplied, it will use
        the most recent value available.
        '''
        if Price > 0:
            return self.History[-1, self._Dividend_History] / Price
        else:
            return (self.History[-1, self._Dividend_History] /
                    self.History[-1, self._Price_History])

    def VolWeighted_StockPrice(self):
        """
        The Volume weighted stock price is calculated of the last five minutes
        trading (from point of call, although it wouldn't take much to choose a
        time point).
        """
        FiveMins = LastFiveMins(self.History)
        return (np.dot(FiveMins[:, self._Quantity_History],
                       FiveMins[:, self._Price_History]) /
                sum(FiveMins[:, self._Quantity_History]))

    def getPrice(self):
        """
        Returns the most recent Price
        """
        return self.History[-1, self._Price_History]


# %% Test data
'''
This section is created just to generate a series of timestamps that can be
input into the trades to ensure that it works.
'''
start = datetime.datetime.strptime("29/04/2018 22:00:00", "%d/%m/%Y %H:%M:%S")
end = datetime.datetime.strptime("29/04/2018 22:30:00", "%d/%m/%Y %H:%M:%S")
dt = np.random.randint(0, int((end-start).total_seconds()),
                       int((end-start).total_seconds()))
dt.sort()  # sorting to make logical time series
# Generating times adding on seconds
date_generated = [start + datetime.timedelta(seconds=int(x)) for x in dt]
PriceList = np.random.randint(0, 100, len(date_generated))
BuySellList = np.random.choice(['Buy', 'Sell'], len(date_generated))
QList = np.random.randint(0, 10000, len(date_generated))

# %% Initialise stocks
'''
Using the data from the provided pdf, create the stocks required.
'''
Tea = Stock(date_generated[0],
            Name="TEA",
            Type="Common",
            ParVal=100,
            Last_Dividend=0,
            Fixed_Dividend=0)
Pop = Stock(date_generated[0],
            Name="POP",
            Type="Common",
            ParVal=100,
            Last_Dividend=8,
            Fixed_Dividend=0)
Ale = Stock(date_generated[0],
            Name="ALE",
            Type="Common",
            ParVal=60,
            Last_Dividend=23,
            Fixed_Dividend=0)
Gin = Stock(date_generated[0],
            Name="GIN",
            Type="Preferred",
            ParVal=100,
            Last_Dividend=8,
            Fixed_Dividend=0.02)
Joe = Stock(date_generated[0],
            Name="JOE",
            Type="Common",
            ParVal=250,
            Last_Dividend=13,
            Fixed_Dividend=0)
# Collecting the stocks into a dictionary. Just makes it easier to cycle
# through and access the Price of each one. Would be easy to add more.
Stocks = {'TEA': Tea, 'POP': Pop, 'ALE': Ale, 'GIN': Gin, 'JOE': Joe}
# %% Populate fictional trades
"""
All the stocks have been given identical trades... Not that realistic, but easy
"""
for i in range(len(date_generated)):
    Tea.Trade(date_generated[i], PriceList[i], QList[i], BuySellList[i], 0)
    Pop.Trade(date_generated[i], PriceList[i], QList[i], BuySellList[i], 0)
    Ale.Trade(date_generated[i], PriceList[i], QList[i], BuySellList[i], 0)
    Joe.Trade(date_generated[i], PriceList[i], QList[i], BuySellList[i], 0)
    Gin.Trade(date_generated[i], PriceList[i], QList[i], BuySellList[i], 0)

# %% Calculate the All Share Index
"""
Calculating the all share index. This could be handled a lot better by perhaps 
making an object to hold all the stocks in and then multiple operations could
be stored and accessed a lot more sensibly...
"""
AllShareIndex = GeometricMean([x.getPrice() for x in Stocks.values()])
