# import selenium dependencies
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException  

import os
import pandas as pd
import numpy as np
import geopy
from geopy.geocoders import Nominatim

from sklearn.impute import KNNImputer

class Listing_Scraper:
    def __init__(self):
        self.base_url = 'http://redfin.com/'
        self.options = Options()
        self.options.headless = True
        prefs = {"download.default_directory": os.getcwd()}
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--headless')
        self.options.add_experimental_option("prefs", prefs)

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)

        # Link to NYTimes article about best cities for Gen Z: https://www.nytimes.com/2022/09/01/realestate/generation-z-best-cities.html
        self.mapper = {'Seattle': 'city/16163/WA/Seattle/', \
                        'Minneapolis': 'city/10943/MN/Minneapolis/', \
                        'Boston': 'city/1826/MA/Boston/', \
                        'New York': 'city/30749/NY/New-York', \
                        'Raleigh': 'city/35711/NC/Raleigh/'}
    
    def search(self, city, property_type, max_price):
        filter_url = 'filter/property-type='
        city_filter = self.mapper[city]
        property_filter = '+'.join(property_type)
        max_price_filter = ',max-price='+str(max_price)

        search_url = self.base_url+city_filter+filter_url+property_filter+max_price_filter
        self.driver.get(search_url)
        download_link = self.driver.find_element(By.ID, "download-and-save")
        self.driver.execute_script("arguments[0].click();", download_link)
        self.driver.close()

    def retrieve_download(self):
        #dir = '/home/aiden/Regis/Practicum II'
        dir = os.getcwd()
        filenames = os.listdir(dir)
        return [filename for filename in filenames if filename.endswith('.csv')]

    def clean_listings(self, listings):
        # Remove unwanted columns
        drop_cols = ['STATE OR PROVINCE', 'NEXT OPEN HOUSE START TIME', 'NEXT OPEN HOUSE END TIME', 'SOURCE', 'MLS#', 'FAVORITE', 'INTERESTED', \
                     'SOLD DATE', 'LOCATION', 'STATUS', 'CITY', 'LATITUDE', 'LONGITUDE']
        cols = [col for col in listings.columns if col not in drop_cols]
        data = listings[cols]
        # Rename and lowercase the columns
        data = data.rename(columns={'ZIP OR POSTAL CODE': 'zip', 'URL (SEE https://www.redfin.com/buy-a-home/comparative-market-analysis FOR INFO ON PRICING)': 'url'})
        data.columns = [col.lower() for col in data.columns]

        # Remove listings with missing addresses or URLs
        no_address_idx = data.loc[data['address'].isna()].index
        no_url_idx = data.loc[data['url'].isna()].index
        data.drop(no_address_idx, inplace=True)
        data.drop(no_url_idx, inplace=True)

        # Impute zip code uisng geopy and street address using geopy
        geolocator = Nominatim(user_agent="get_zip")

        # Get list of addresses where zip is nan and corresponding index in dataframe
        missing_zip_idx = np.where(data['zip'].isna())
        missing_zip = []
        if len(missing_zip_idx[0]) > 0:
            for i in range(len(missing_zip_idx)):
                idx = missing_zip_idx[0][i]
                missing_zip.append((idx, data.iloc[idx]['address']))

            # Iterate through rows with missing zips
            for address in missing_zip:
                # Get geolocation data and parse
                location = geolocator.geocode(address)
                loc_data = location.raw
                loc_data = loc_data['display_name'].split()
                # Isolate zip code, remove comma in final position of string
                zip = loc_data[-2][:-1]
                # Check that the zip is 5 chars long
                assert len(zip) == 5
                # Impute zip
                data.loc[idx, 'zip'] = zip

        data['zip'] = data['zip'].astype('str')
        
        # Impute missing HOA fees with $0
        data['hoa/month'] = data['hoa/month'].replace(np.nan, 0)
        # Replace nans in Year Built with 2024 for new construction
        data['year built'] = data['year built'].mask(data['sale type']=='New Construction Plan', 2024)

        # Get dummy variables for categorical features
        data_quant = data.copy()
        data_quant.drop(['url', 'address', 'zip'], axis=1, inplace=True)
        data_quant = pd.get_dummies(data_quant)

        # Call and fit imputer
        imputer = KNNImputer(n_neighbors=5, weights='uniform', metric='nan_euclidean')
        imputer.fit(data_quant)
        # Transform data
        data_trans = imputer.transform(data_quant)
        data_cleaned = pd.DataFrame(data_trans, columns = data_quant.columns)

        # Add back addresses and URLs as features 
        data_cleaned['url'] = data['url']
        data_cleaned['address'] = data['address']
        data_cleaned['zip'] = data['zip']

        # Return cleaned dataframe
        assert data_cleaned.isnull().values.any() == False   
        return data_cleaned
