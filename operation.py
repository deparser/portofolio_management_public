from enum import Enum
import json
import os
import datetime as dt

# Internal imports
from investment import Investment
from settings import portfolioPath, closedInvestmentsPath, operationsPath

class OperationType(Enum):
    BUY = 1
    SELL = 2


class Operation():
    def __init__(self, investmentId, operationType, quantity, price, date, commission):
        self.investmentId = investmentId
        self.operationType = operationType
        self.operationQuantity = quantity
        self.operationPrice = price
        self.date = date
        self.commission = commission
        self.portfolio = self.getPortfolio()
        self.closedInvestments = self.getClosedInvestments()
        
        self.updatePortofolio()
        self.updateOperationsFile()

    
    def getPortfolio(self):
        with open(portfolioPath, "r") as f:
            portfolio = json.load(f)
            return portfolio
        
    def savePortfolio(self):
        with open(portfolioPath, "w") as f:
            json.dump(self.portfolio, f, indent=4)

    def getClosedInvestments(self):
        with open(closedInvestmentsPath, "r") as f:
            closedInvestments = json.load(f)
            return closedInvestments
        
    def saveClosedInvestments(self):
        with open(closedInvestmentsPath, "w") as f:
            json.dump(self.closedInvestments, f, indent=4)
    
    def updatePortofolio(self):
        """
        Updates the portfolio and closed investments based on the operation type.

        This function updates the portfolio and closed investments based on the operation type.
        If the operation type is BUY, it calculates the new quantity and average buy price
        and updates the portfolio accordingly.
        If the operation type is SELL, it updates the portfolio by subtracting the sold quantity
        and updates the closed investments with the sold details.

        Parameters:
            self (Operation): The Operation object.

        Returns:
            None
        """

        if self.operationType == OperationType.BUY:
            currentQuantity = self.portfolio[self.investmentId]["quantity"]
            currentAveragePrice = self.portfolio[self.investmentId]["averageBuyPrice"]

            newQuantity = currentQuantity + self.operationQuantity
            newValue = currentQuantity * currentAveragePrice + self.operationQuantity * self.operationPrice + self.commission
            newPrice = (newValue) / newQuantity

            self.portfolio[self.investmentId]["quantity"] = newQuantity
            self.portfolio[self.investmentId]["averageBuyPrice"] = newPrice

        if self.operationType == OperationType.SELL:
            # Update the portfolio
            currentQuantity = self.portfolio[self.investmentId]["quantity"]
            currentAveragePrice = self.portfolio[self.investmentId]["averageBuyPrice"]
            self.portfolio[self.investmentId]["quantity"] = currentQuantity - self.operationQuantity

            # Update the closed investments
            # Note that the average buy price is the average price at the moment of this operation (and it is correct!)
            soldValue = self.operationQuantity * self.operationPrice - self.commission
            startValue = self.operationQuantity * currentAveragePrice
            grossProfit = soldValue - startValue
            netProfit = (soldValue - startValue) * (1 - self.portfolio[self.investmentId]["taxRate"])
            self.closedInvestments[self.investmentId] = {
                "name": self.portfolio[self.investmentId]["name"],
                "investmentId": self.investmentId,
                "averageBuyPrice": self.portfolio[self.investmentId]["averageBuyPrice"],
                "soldQuantity": self.operationQuantity,
                "averageSoldPrice": self.operationPrice,
                "grossProfit": grossProfit,
                "netProfit": netProfit
            }

        self.savePortfolio()
        self.saveClosedInvestments()

    def updateOperationsFile(self):

        # Create the dictionary with the data
        operationData = {
            'investmentId': self.investmentId,
            'operationType': "BUY" if self.operationType == OperationType.BUY else "SELL",
            'quantity': self.operationQuantity,
            'price': self.operationPrice,
            'date': self.date.strftime("%Y-%m-%d"),
        }

        # Check if the file exists, otherwise create it
        if not os.path.exists(operationsPath):
            with open(operationsPath, "w") as f:
                json.dump([operationData], f)
                exit()
        else:
            with open(operationsPath, "r") as f:
                operationsList = json.load(f)
            with open(operationsPath, "w") as f:
                operationsList.append(operationData)
                json.dump(operationsList, f, indent=4)


                
            

    