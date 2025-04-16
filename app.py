import streamlit as st
import pandas as pd
import numpy as np
import requests
from geocodio import GeocodioClient

def geocodio(address):
    client = GeocodioClient(st.secrets["GEOCODIO_TOKEN"])

    location = client.geocode(address, fields=["census2023"])

    census = location["results"][0]['fields']['census']['2023']
    tract = census['tract_code']
    state = census['state_fips']
    county = census['county_fips'][2:]
    try:
        mmsa = census['metro_micro_statistical_area']['area_code']
    except:
        mmsa = None
        print("ERROR: No Metropolitan/Micropolitan Statistical Area found for", location["results"][0]['formatted_address'])
    return tract, county, mmsa, location["results"][0]['formatted_address']

##################################################

# App title and description
st.title("Affirmative Fair Housing Marketing Plan (AFHMP) Form Helper")
st.write("Enter a full US address to gather demographic data. No specific formatting necessary.")

# User input
search_term = st.text_input("Address:")

# Process when user clicks button
if st.button("Submit"):
    if search_term:
        st.write(f"Gathering demographic data...")

        tract, county, mmsa, formatted_address = geocodio(search_term)
        
        # Simulate data processing (replace with your actual code)
        data = pd.DataFrame({
            'Category': ['A', 'B', 'C'],
            'Value': np.random.randn(3)
        })
        
        # Display results
        st.subheader(f"Demographic Summary for {formatted_address}")
        st.write("Census Tract: {tract}")
        st.write("County (Housing Market Area): {county}")
        if mmsa is None:
            st.write("No metropolitan statistical area/micropolitan statistical area to calculate Expanded Housing Market Area")
        else:
            st.write("Metro/Micropolitan Statistical Area (Expanded Housing Market Area): {mmsa}")

        # Show data table
        st.subheader("Data Table")
        st.dataframe(data)
        
        # Download buttons
        csv = data.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            "Download Detailed CSV",
            data=csv,
            file_name=f"{search_term}_results.csv",
            mime="text/csv"
        )
    else:
        st.error("Please enter an address")
