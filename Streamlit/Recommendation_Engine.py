import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
class User:
    def __init__(self, price, beds, baths, square_feet, property_age, age, household_income, individual_income, property_types, cities, new_build):
        self.price = price
        self.beds = beds
        self.baths = baths
        self.square_feet = square_feet
        self.year_built = 2023-property_age
        self.age = age
        self.household_income = household_income
        self.individual_income = individual_income
        self.property_types = property_types
        self.cities = cities
        self.new_build = new_build

    def get_array(self):
        arr = np.array([self.price, self.beds, self.baths, self.square_feet, self.year_built, self.age, self.household_income, self.individual_income])
        return arr
    

def recommend(data, user, num_recs):
    # Drop categorical columns and columns not used to make recommendations
    drop_cols = ['days on market', 'poverty_rate', 'homeownership_rate', 'vacancy_rate', 'zip']
    rec_data = data.drop(drop_cols, axis=1)  

    # Get np.array of user info and calculate cosine similarity with listings matrix
    user_arr = user.get_array()
    user_arr = user_arr.reshape(1, -1)
    cosine_similarities = cosine_similarity(rec_data, user_arr)
    # Convert array back to pd.Series to maintain index of URLs
    recommendations = [item[0] for item in cosine_similarities]
    recommendations = pd.Series(recommendations, index=rec_data.index)
    # Sort recommendations
    weighted_recs = weight_recommendations(data, recommendations)
    sorted_recs = weighted_recs.sort_values(ascending=False)
    # Return dataframe of recommendations including only columns with property information
    property_cols = ['price', 'beds', 'baths', 'square feet', 'year built', 'days on market']
    index = sorted_recs.index
    # Conver year built to string 
    data['year built'] = data['year built'].astype('string')
    return data.loc[index][property_cols].head(num_recs)  


def weight_recommendations(data, recommendations):
    # Isolate index of recommended listings
    urls = recommendations.index
    # Calculate metrics to weight recommendations
    inverse_poverty = 1 - data.loc[urls]['poverty_rate']
    homeownership = data.loc[urls]['homeownership_rate']
    inverse_vacancy = 1 - data.loc[urls]['vacancy_rate']
    # Weight recommendations
    recommendations = recommendations * inverse_poverty * homeownership * inverse_vacancy
    return recommendations

