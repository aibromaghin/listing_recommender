# Listing Recommender

## Folders
This repo contains files for my Practicum II at Regis University. 
The Notebook Files folder contains notebooks from my initial data cleaning, analysis, and building of the recommendation system. 
The Streamlit folder contains the final files for the Streamlit web app.

## Work Done
The files in the Streamlit folder run a web app that acts as a recommendation system for a residential real estate listings. The app prompts users for information about the property characteristics they want and some demographic information, and then generates the requested number of listings. Data is scraped from Redfin and the 2021 American Community Survey. Cosine similarity is used to generate recommendations, which are weighted by features in the demographic data for the user. 

## Unresolved Issues
The web app runs locally but I am still having difficulty successfully deploying it on the Streamlit cloud. The issue stems from the use of Selenium to scrape listings, which apparently does not integrate easily with Streamlit.

## Work to Expand this Project.
There are a number of items that could be done to extend this project, time permitting. 
  1. Incorporate a method to receive feedback on the recommendations.
  2. Generate synthetic user data to enable a switch to collaborative based filtering.
  3. Switch to another library for web scraping for easier deployment.
