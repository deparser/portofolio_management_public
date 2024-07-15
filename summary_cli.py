import os
import json
import datetime as dt
import investpy
import pandas as pd

# Internal imports
from bond import Bond
from operation import Operation
from operation import OperationType as OT
from investment import Investment
from dividend import Dividend
from settings import portfolioPath, closedInvestmentsPath, dividendPath, operationsPath

# Settings
updateBonds = False

# Create the images folder
os.makedirs('images', exist_ok=True)

# Create a dataframe with the data of the portfolio path
df = pd.read_json(portfolioPath)
df = df.T
df.to_csv('portfolio.csv', index=False)

# Get the total invested
with open(portfolioPath, 'r') as portfolio:
    portfolio = json.load(portfolio)
    totalInvested = 0
    for investment in portfolio:
        totalInvested += portfolio[investment]["averageBuyPrice"] * portfolio[investment]["quantity"]
print('Today total invested: ' + f'{totalInvested:.2f} - sum of average buy price and quantity')

# Get the profit from capital gain
with open(closedInvestmentsPath, 'r') as closed:
    closedInvestments = json.load(closed)
totalFromClosed = 0
for investment in closedInvestments:
    totalFromClosed += closedInvestments[investment]["netProfit"]

# Get the profit from dividends
with open(dividendPath, 'r') as dividend:
    dividend = json.load(dividend)
totalFromDividend = 0
for investment in dividend:
    totalFromDividend += dividend[investment]["netDividend"]

# Get actual price from investpy by investingpy
skipThis = True
if not skipThis:
    for investment in portfolio:
        isin = portfolio[investment]["ISIN"]
        try:
            search_result = investpy.stocks.search_stocks(by='isin', value=isin)
        except:
            continue
        print(search_result)

# Define asset allocation by totale invested
totalEtf = 0
totalBond = 0
totalStock = 0
for investment in portfolio:
    if portfolio[investment]["type"] == "ETF":
        totalEtf += portfolio[investment]["averageBuyPrice"] * portfolio[investment]["quantity"]
    elif portfolio[investment]["type"] == "BOND":
        totalBond += portfolio[investment]["averageBuyPrice"] * portfolio[investment]["quantity"]
    elif portfolio[investment]["type"] == "STOCK":
        totalStock += portfolio[investment]["averageBuyPrice"] * portfolio[investment]["quantity"]

print(' > Total ETF: ' + f'{totalEtf:.2f} perc: ' + f'{totalEtf / totalInvested * 100:.2f}%')
print(' > Total Bond: ' + f'{totalBond:.2f} perc: ' + f'{totalBond / totalInvested * 100:.2f}%')
print(' > Total Stock: ' + f'{totalStock:.2f} perc: ' + f'{totalStock / totalInvested * 100:.2f}%')

print('-' * 40)
print('RESULTS')
print(' > Total net from capital gain: ' + f'{totalFromClosed:.2f}')
print(' > Total net from dividends: ' + f'{totalFromDividend:.2f}')
print(' > Total net profit: ' + f'{totalFromClosed + totalFromDividend:.2f}')

# Use matplotlib to plot staticis about the portfolio
import matplotlib.pyplot as plt

# Plot a pie chart of asset allocation
plt.pie([totalEtf, totalBond, totalStock], labels=['ETF', 'Bond', 'Stock'])
plt.savefig('images/pie.png')
plt.close()

# --------------------------- INVESTED BY TIME --------------------
# Open the file with the operation data and get the total invested by time
totalInvested = 0
invested = []
with open(operationsPath, 'r') as operations:
    operations = json.load(operations)

# Convert the operations to a df
operationDf = pd.DataFrame.from_dict(operations)
operationDf['total'] = operationDf['quantity'] * operationDf['price']
operationDf['date'] = pd.to_datetime(operationDf['date'])

with open('invested_by_times.txt', 'w') as f:
    # Sort the operations by date
    for operation in operationDf.sort_values(by='date').to_dict(orient='records'):
        if operation['operationType'] == 'BUY':
            totalInvested += operation['total']
        elif operation['operationType'] == 'SELL':
            totalInvested -= operation['total']
        invested.append((operation['date'], totalInvested))
        f.write(f'{operation["date"]} - {totalInvested:.2f}\n')

# Plot the total invested by time as histogram
plt.figure(figsize=(10, 7))
plt.bar([dt.datetime.strftime(x[0], '%Y-%m-%d') for x in invested], [x[1] for x in invested])
plt.xticks(rotation=45)
plt.xlabel('Date')
plt.ylabel('Total invested')
plt.title(f'Total invested by time - final value: {totalInvested:.2f}')
plt.savefig('images/invested_by_time.png')
plt.close()


# --------------------------- BONDS --------------------------------
# Open the file with the bond data
if updateBonds:
    df = Bond.getdata(updateBonds)

    # Get the list of ISIN in portfolio
    myBondData = []
    for investment in portfolio:
        if portfolio[investment]["type"] == "BOND":
            bondData = {
                "name": portfolio[investment]["name"],
                "ISIN": portfolio[investment]["ISIN"],
                "quantity": portfolio[investment]["quantity"],
            }

            # get the expire date from the df 
            for index, row in df.iterrows():
                if row["Codice ISIN"] == portfolio[investment]["ISIN"]:
                    bondData.update({
                        "expire_date": row["Data rimborso"],
                    })

            myBondData.append(bondData)

    # Print the bonds order by expire date
    print('-----------------------------------------------------')
    print('BONDS ordered by expire date:')
    for bond in sorted(myBondData, key=lambda x: dt.datetime.strptime(x['expire_date'], '%Y-%m-%d').date()):
        if bond['quantity'] > 0:
            print(f' > {bond["name"]}: {bond["expire_date"]} - {bond["quantity"]} €')

    # Plot a bar chart of the bonds
    dates = [dt.datetime.strptime(bond['expire_date'], '%Y-%m-%d').date() for bond in myBondData]
    values = [bond['quantity'] for bond in myBondData]
    plt.hist(dates, bins=50, weights=values)

    # Move the x-axis labels to the 45 degree angle
    plt.xticks(rotation=45)
    plt.savefig('images/bonds.png')




