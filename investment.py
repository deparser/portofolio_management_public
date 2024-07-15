from enum import Enum
import json


# Internal imports
from settings import portfolioPath

class Investment():

    def __init__(self, id, name, ISIN, investmentType):
        self.name = name    
        self.ISIN = ISIN
        self.id = id
        self.investmentType = investmentType
        self.taxRate = 0.125 if self.investmentType == "BOND" else 0.26
        self.addNew()

    def addNew(self):
        with open(portfolioPath, "r") as f:
            portfolio = json.load(f)
            portfolio.update({
                self.id: {
                    "name": self.name,
                    "id": self.id,
                    "ISIN": self.ISIN,
                    "type": self.investmentType,
                    "averageBuyPrice": 0,
                    "quantity": 0,
                    "taxRate": self.taxRate,
                }
            })
            with open(portfolioPath, "w") as outputFile:
                outputFile.write(json.dumps(portfolio, indent=4))



    

