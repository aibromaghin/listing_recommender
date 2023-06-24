import requests 
import pandas as pd

class census_scraper:
  def __init__(self):
    # Define base URL
    self.HOST = 'https://api.census.gov/data'
    self.year = '2021'
    self.dataset = 'acs/acs5'
    self.base_url = '/'.join([self.HOST, self.year, self.dataset])
    # Define list of variables
    self.var_list = ['NAME', 'B01001_001E', 'B01002_001E', 'B19113_001E', 'B19301_001E', 'B07013_001E', 'B07013_002E', 'B07013_003E', \
                'B25001_001E', 'B25002_002E', 'B25002_003E', 'B25003_002E', 'B25003_003E', 'B17001_001E', 'B17001_002E', 'B19083_001E']
    # Define mapping of variables and descriptions
    self.var_map = {'B01001_001E':'population', 'B01002_001E':'median_age', 'B19113_001E':'median_family_income', 'B19301_001E':'per_capita_income',\
           'B07013_001E':'total_households', 'B07013_002E':'owner_occupied_households', 'B07013_003E':'renter_occupied_households', \
           'B25001_001E':'total_units', 'B25002_002E':'occupied_units', 'B25002_003E':'vacant_units', 'B25003_002E':'owner_occupied_units', \
           'B25003_003E':'renter_occupied_units', 'B17001_001E':'total_income_poverty', 'B17001_002E':'total_income_below_poverty',
           'B19083_001E': 'gini_index'}

  # Converts the list of variable names to a single string
  def get_vars(self):
    return ','.join(self.var_list)
  
  # Takes in a list of zip codes
  # Returns a pandas dataframe of census data with human-readable column names
  def get_data(self, zip_list):
    zip_string = ','.join(zip_list)
    var_str = self.get_vars()
    url = f'{self.base_url}?get={var_str}&for=zip%20code%20tabulation%20area:{zip_string}'
    response = requests.get(url)
    data_json = response.json()
    df = pd.DataFrame(data_json[1:], columns=data_json[0])
    df = df.rename(columns=self.var_map)
    return df