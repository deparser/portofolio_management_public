import os
import pandas as pd
import streamlit as st
import json
import datetime as dt
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import yfinance as yf

# Internal imports
from bond import Bond
from operation import Operation
from operation import OperationType as OT
from investment import Investment
from dividend import Dividend
from settings import jsonDataFolder, portfolioPath, closedInvestmentsPath, dividendPath, operationsPath

# Create a streamlit app that shows the portfolio using the data contained in portfolio path
print(f'Start streamlit app at {dt.datetime.now()}')
st.set_page_config(layout="wide")

st.title("Portfolio Management")

# Create a dataframe with the data of the portfolio path
df = pd.read_json(portfolioPath)
st.header("Actual Portfolio")
df = pd.read_json(portfolioPath).T

# Remove the zero quantity in the dataframe
df = df[df["quantity"] != 0]

# Add the total quantity
df["total"] = df["averageBuyPrice"] * df["quantity"]


for index, row in df.iterrows():
    ticker = row["ticker"]
    if ticker is None:
        continue

    # Get stock data
    stock = yf.Ticker(ticker)
    try:
        last_price = float(stock.history(period="1d")['Close'].iloc[0])
    except Exception as e:
        print(e)
        last_price = None
    
    df.at[index, "last_price"] = last_price

    # Add the total value
    df.at[index, "actual"] = last_price * row["quantity"]

    # Add the variation percentage
    df.at[index, "delta"] = (last_price - row["averageBuyPrice"]) * row["quantity"]
    if df.at[index, "delta"] > 0:
        df.at[index, "delta_net"] = (last_price - row["averageBuyPrice"]) * row["quantity"] * (1 - row["taxRate"])
    else:
        df.at[index, "delta_net"] = (last_price - row["averageBuyPrice"]) * row["quantity"]
    df.at[index, "perc_net"] = df.at[index, "delta_net"] / (row["averageBuyPrice"] * row["quantity"]) * 100

# Fix the dataframe format
formattedDf = df[["name", "ticker", "type", "quantity", "averageBuyPrice", "last_price", "delta_net", "perc_net"]]
columnConfig = {
    'name': 'Name',
    'ticker': 'Ticker',
    'type': 'Type',
    'quantity': 'Quantity',
    'averageBuyPrice':  st.column_config.NumberColumn("averageBuyPrice", format="%.2f €"),
    'last_price': st.column_config.NumberColumn("lastPrice", format="%.2f €"),
    'delta_net': st.column_config.NumberColumn("delta_net", format="%.2f €"),
    'perc_net': st.column_config.NumberColumn("perc_net", format="%.2f %%"),
}

st.dataframe(formattedDf, hide_index=True, use_container_width=True, column_config=columnConfig)
st.session_state["df"] = formattedDf

#####################################################################
#                           Open the data
#####################################################################

# Get the total invested
with open(portfolioPath, 'r') as portfolio:
    portfolio = json.load(portfolio)
    
    
#####################################################################
#                           Plot asset allocation
#####################################################################

st.subheader("Asset allocation")

# Define asset allocation by totale invested
totalEtf = 0
totalBond = 0
totalStock = 0
totalEtfBond = 0
for investment in portfolio:
    if portfolio[investment]["type"] == "ETF":
        totalEtf += portfolio[investment]["averageBuyPrice"] * portfolio[investment]["quantity"]
    elif portfolio[investment]["type"] == "BOND":
        totalBond += portfolio[investment]["averageBuyPrice"] * portfolio[investment]["quantity"]
    elif portfolio[investment]["type"] == "STOCK":
        totalStock += portfolio[investment]["averageBuyPrice"] * portfolio[investment]["quantity"]
    elif portfolio[investment]["type"] == "ETF_BOND":
        totalEtfBond += portfolio[investment]["averageBuyPrice"] * portfolio[investment]["quantity"]

# Create a plotly pie chart
labels = ['ETF_STOCK', 'BOND', 'STOCK', 'ETF_BOND']
values = [totalEtf, totalBond, totalStock, totalEtfBond]

# Create the Plotly pie chart
fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
fig.update_traces(hoverinfo='label+value', textinfo='percent', textfont_size=20)

# Display the Plotly pie chart in Streamlit
st.plotly_chart(fig)

#####################################################################
#                           Plot invested by time
#####################################################################
# Open the file with the operation data and get the total invested by time
totalInvested = 0
invested = []
with open(operationsPath, 'r') as operations:
    operations = json.load(operations)

# Convert the operations to a df
operationDf = pd.DataFrame.from_dict(operations)
operationDf['total'] = operationDf['quantity'] * operationDf['price']
operationDf['date'] = pd.to_datetime(operationDf['date'])

investedDict = {}
with open('invested_by_times.txt', 'w') as f:
    # Sort the operations by date
    for operation in operationDf.sort_values(by='date').to_dict(orient='records'):
        if operation['operationType'] == 'BUY':
            totalInvested += operation['total']
        elif operation['operationType'] == 'SELL':
            totalInvested -= operation['total']
        investedDict.update({operation['date']: totalInvested})
        f.write(f'{operation["date"]} - {totalInvested:.2f}\n')


# Plot the total invested by time as histogram
st.subheader("Invested by time")

# Get the most recent date
lastDate = max(investedDict.keys())
todayInvested = investedDict[lastDate]

st.write('Today total invested: ' + f'{todayInvested:.2f} - sum of average buy price and quantity')
st.area_chart(investedDict, x_label='Date', y_label='Total invested', use_container_width=True)



#####################################################################
#                           Plot profit by tipe
#####################################################################

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
    
profitsDict = {
    "Capital Gain": totalFromClosed,
    "Dividends": totalFromDividend
}
st.subheader("Profit by tipe")
st.write(f'Total profit from capital gain and dividend: {totalFromClosed + totalFromDividend:.2f} €')
st.bar_chart(profitsDict, x_label="Investment type", y_label="Total profit")

#####################################################################
#                           Bonds by expire date
####################################################################

# --------------------------- BONDS --------------------------------
st.subheader("Bonds by expire date")

# Open the file with the bond data
myBondData = []
for investment in portfolio:
    if portfolio[investment]["type"] == "BOND":
        bondData = {
            "name": portfolio[investment]["name"],
            "quantity": portfolio[investment]["quantity"],
            'expire_date': portfolio[investment]["expireDate"],
        }
        myBondData.append(bondData)
myBondDf = pd.DataFrame(myBondData)

# Print the bonds order by expire date
st.write('BONDS ordered by expire date:')
for bond in sorted(myBondData, key=lambda x: dt.datetime.strptime(x['expire_date'], '%Y-%m-%d').date()):
    if bond['quantity'] > 0:
        st.write(f' > {bond["name"]}: {bond["expire_date"]} - {bond["quantity"]} €')

# Plot a bar chart of the bonds
st.bar_chart(myBondDf, x='expire_date', y='quantity', use_container_width=True)