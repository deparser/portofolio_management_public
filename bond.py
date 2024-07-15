import os
import pandas as pd
import requests
import zipfile


# Internal imports
from investment import Investment

class Bond(Investment):

    def __init__(self, name, ISIN, expirePrice, expireDate):
        self.name = name
        self.ISIN = ISIN
        self.expirePrice = expirePrice
        self.expireDate = expireDate
        
        super().__init__(self.name)


    @staticmethod
    def getdata(update):
        if not update:
            try:
                csv_file_path = os.path.join(os.getcwd(), "bond_data", "dailymonitor.csv")
                df = pd.read_csv(csv_file_path, encoding="utf-8", sep=";")
            except Exception as e:
                print(f'Error: {e} - update file')
                update = True
                
        if update:
            url = "https://www.simpletoolsforinvestors.eu/data/download/dailymonitor.csv.zip"
            target_folder = os.path.join(os.getcwd(), "bond_data")
            
            # Create the target folder if it doesn't exist
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)
            
            # Extract the filename from the URL
            file_name = os.path.join(target_folder, url.split('/')[-1])
            
            # Download the zip file
            response = requests.get(url)
            with open(file_name, 'wb') as f:
                f.write(response.content)
            
            # Extract the zip file
            with zipfile.ZipFile(file_name, 'r') as zip_ref:
                zip_ref.extractall(target_folder)
            
            # Return the path to the extracted CSV file
            csv_file_path = os.path.join(target_folder, os.path.splitext(zip_ref.namelist()[0])[0] + '.csv')

            # Read the CSV file using pandas with utf - 8
            df = pd.read_csv(csv_file_path, encoding="utf-8", sep=";")

        return df

    