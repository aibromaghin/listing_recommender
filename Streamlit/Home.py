import streamlit as st
import pandas as pd
import numpy as np
from Redfin_Scraper import Listing_Scraper
from Census_Scraper import census_scraper
from Recommendation_Engine import User, recommend
import os
pd.set_option('display.max_columns', None)

st.write('# Home Recommendation Engine')

st.write('## Tell us a little about what you\'re looking for in a property. For each category, enter what you\'d like to have in your ideal home.')

col1, col2, col3 = st.columns(3)

city = col1.selectbox(label='Pick a city: ', options=['Boston, MA', 'Minneapolis, MN', 'Seattle, WA','Raleigh, NC', 'New York, NY'])
state = city[-2:]
city = city[:-4]
beds = col2.selectbox(label='Bedrooms: ', options=['1', '2', '3', '4', '5'])
baths = col3.selectbox(label='Bathrooms: ', options=['1', '2', '3', '4'])
square_feet = col1.number_input(label='Square footage: ', min_value=0)
property_age = col2.number_input(label='How many years old should it be?', min_value=0)
new_build = col3.selectbox(label='Are you open to new construction?', options=['Yes', 'No'])
new_build = True if 'Yes' else False
property_types = col1.multiselect(label='What property types are you open to?', options=['House', 'Multifamily', 'Townhouse', 'Condo'])
property_types = [type.lower() for type in property_types]
max_price = col2.number_input(label='What is the max price in your budget?', min_value=0)
price = col3.number_input(label='What is your ideal price? ', min_value=0)

st.write('## Next, tell us a bit about yourself. This will help us personalize your recommendations.')
col4, col5, col6 = st.columns(3)
age = col4.number_input(label='Age: ', min_value=18)
individual_income = col5.number_input(label='Your gross annual income: ', min_value=0)
household_income = col6.number_input('Your gross annual household income: ', min_value=0)

st.write('## How many recommendations would you like?')
container = st.container()
num_recs = container.number_input(label='Number of recommendations: ', min_value=0)

user = User(price=price, beds=beds, baths=baths, square_feet=square_feet, property_age=property_age, cities=city, age=age, household_income=household_income, \
            individual_income=individual_income, new_build=new_build, property_types=property_types)

# Button to generate listings
button = st.button(label='Generate Recommendations')
if button:
    # Get listing data
    listing_scraper = Listing_Scraper()
    search_url = listing_scraper.search(city=city, property_type=property_types, max_price=max_price)
    file = listing_scraper.retrieve_download()
    listing_df = pd.read_csv(file[0], dtype={'ZIP OR POSTAL CODE': 'str'})
    listing_df = listing_scraper.clean_listings(listing_df)

    census_scraper = census_scraper()
    census_df = census_scraper.get_data(listing_df['zip'].to_list())
    census_df.rename(mapper={'zip code tabulation area':'zip'}, axis=1, inplace=True)
    census_df.drop('NAME', axis=1, inplace=True)
    numeric_cols = [col for col in census_df.columns if col != 'zip']
    census_df[numeric_cols] = census_df[numeric_cols].apply(pd.to_numeric)
    df = pd.merge(listing_df, census_df, on='zip')
    df.set_index('url', inplace=True)

    # Add calculated fields
    df['poverty_rate'] = df['total_income_below_poverty'] / df['total_income_poverty']
    df['homeownership_rate'] = df['owner_occupied_units'] / df['occupied_units']
    df['vacancy_rate'] = df['vacant_units'] / df['total_units']

    # Drop columns
    drop_cols = ['$/square feet', 'hoa/month', 'lot size', 'address', 'population', 'total_units', 'occupied_units', 'vacant_units', 'owner_occupied_units', 'renter_occupied_units', \
                'total_households', 'owner_occupied_households', 'renter_occupied_households', 'total_income_poverty', 'total_income_below_poverty', 'gini_index']
    property_cols = [col for col in df.columns if col.startswith('property')]
    sale_cols = [col for col in df.columns if col.startswith('sale')]
    drop_cols.extend(property_cols)
    drop_cols.extend(sale_cols)
    df.drop(labels=drop_cols, axis=1, inplace=True)

    recs = recommend(df, user, num_recs=num_recs)
    st.write(recs)
    os.remove(file[0])
    button = False
