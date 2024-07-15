from enum import Enum
import json

# Internal imports
from investment import Investment
from settings import portfolioPath, dividendPath

class Dividend(Investment):

    def __init__(self, investmentId, dividendAmount, dividendDate):
        self.investmentId = investmentId
        self.dividendAmount = dividendAmount
        self.dividendDate = dividendDate

        self.addNew()

    def addNew(self):
        with open(dividendPath, "r") as f:
            dividend = json.load(f)

        # Get the data from the investment
        with open(portfolioPath, "r") as f:
            portfolio = json.load(f)
            investmentName = portfolio[self.investmentId]["name"]
            taxRate = portfolio[self.investmentId]["taxRate"]

        # Define dividen properties
        dividendId = len(dividend) + 1
        dividend.update({
            dividendId: {
                "id": self.investmentId,
                "name": investmentName,
                "grossDividend": self.dividendAmount,
                "netDividend": self.dividendAmount * (1 - taxRate),
            }
        })

        with open(dividendPath, "w") as outputFile:
            outputFile.write(json.dumps(dividend, indent=4))