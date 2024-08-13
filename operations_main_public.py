# External imports
import os
import json
import datetime as dt

# Internal imports
from bond import Bond
from operation import Operation
from operation import OperationType as OT
from investment import Investment
from dividend import Dividend
from settings import jsonDataFolder, portfolioPath, closedInvestmentsPath, dividendPath, operationsPath

# Initialize the jsondata folder
os.makedirs(jsonDataFolder, exist_ok=True)

# Initialize the jsons that are dicts
for file in [portfolioPath, closedInvestmentsPath, dividendPath]:
    if os.path.isfile(file):
        os.remove(file)
    with open(file, "w") as f:
        json.dump({}, f)

# Initialize the jsons that are lists
for file in [operationsPath]:
    if os.path.isfile(file):
        os.remove(file)
    with open(file, "w") as f:
        json.dump([], f)

# Define the total invested
invested = 23000 # somma dei bonifici

# Initialize a new investment
Investment("001", "iShares MSCI World acc", "IE00B4K48X80", "ETF", ticker="SWDA.MI", expireDate=None)
Investment("002", "IT BOND", "IT0005565400", "BOND", ticker=None, expireDate=dt.datetime(2024, 12, 10))
Investment("003", "Apple", "US0378331005", "STOCK", ticker="1AAPL.MI", expireDate=None)



# Define the operations
Operation("001", OT.BUY, 20, 50.06, dt.datetime(2021, 12, 6), commission=0)
Operation("002", OT.BUY, 1000, 100/100, dt.datetime(2023, 11, 10), commission=0)
Operation("002", OT.SELL, 5, 61.25, dt.datetime(2024, 4, 10), commission=0)
Operation("003", OT.BUY, 5, 182.35, dt.datetime(2024, 8, 10), commission=0)


Dividend("002", 10.5, dt.datetime(2023, 1, 24))

print('Done.')




