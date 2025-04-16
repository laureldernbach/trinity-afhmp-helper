import streamlit as st
import pandas as pd
import numpy as np
import requests
from geocodio import GeocodioClient

def geocodio_helper(address):
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
    return tract, county, state, mmsa, location["results"][0]['formatted_address']

def census(year, state, county, tract, api_key):
    # https://api.census.gov/data/2023/acs/acs5/profile/variables.html

    # White
    percent_white = {"code":'DP05_0037PE', "label": "% White"}
    # Black or African American
    percent_black = {"code":'DP05_0038PE', "label": "% Black or African American"}
    # Hispanic or Latino (of any race)
    percent_hispanic_latino = {"code":'DP05_0076PE', "label": "% Hispanic or Latino"}
    # Asian
    percent_asian = {"code":'DP05_0047PE', "label": "% Asian"}
    # American Indian and Alaska Native
    percent_american_indian = {"code":'DP05_0039PE', "label": "% American Indian or Alaskan Native"}
    # Native Hawaiian and Other Pacific Islander
    percent_native_hawaiian = {"code":'DP05_0055PE', "label": "% Native Hawaiian or Pacific Islander"}
    # With a disability
    percent_disability = {"code":'DP02_0072PE', "label": "% Persons with Disabilities"}
    # Households with one or more people under 18 years
    percent_households_under_18 = {"code":'DP02_0014PE', "label": "% Families with Children under the age of 18"}

    variables = f'NAME,{percent_white["code"]},{percent_black["code"]},{percent_hispanic_latino["code"]},{percent_asian["code"]},{percent_american_indian["code"]},{percent_native_hawaiian["code"]},{percent_disability["code"]},{percent_households_under_18["code"]}'

    # TRACT LEVEL
    query_url = "https://api.census.gov/data/{year}/acs/acs5/profile?get={variables}&for=tract:{tract}&in=state:{state}%20county:{county}&key={key}"
    query = query_url.format(year=year, variables=variables, state=state, tract=tract, county=county, key=api_key)

    response = requests.get(query)
    data=response.json()
    df_tract = pd.DataFrame(data[1:], columns=data[0])
    print("Census Tract: ", df_tract.loc[0, "NAME"])
    formatted_tract = df_tract.loc[0, "NAME"]
    df_tract.loc[0, "NAME"] = "Census Tract"

    # COUNTY LEVEL
    query_url = "https://api.census.gov/data/{year}/acs/acs5/profile?get={variables}&for=county:{county}&in=state:{state}&key={key}"
    query = query_url.format(year=year, variables=variables, state=state, tract=tract, county=county, key=api_key)

    response = requests.get(query)
    data=response.json()
    df_county = pd.DataFrame(data[1:], columns=data[0])
    print("County (Housing Market Area): ", df_county.loc[0, "NAME"])
    formatted_county = df_county.loc[0, "NAME"]
    df_county.loc[0, "NAME"] = "Housing Market Area"

    # MMSA LEVEL
    if mmsa is not None:
        query_url = "https://api.census.gov/data/{year}/acs/acs5/profile?get={variables}&for=metropolitan%20statistical%20area/micropolitan%20statistical%20area:{mmsa}&key={key}"
        query = query_url.format(year=year, variables=variables, mmsa=mmsa, key=api_key)

        response = requests.get(query)
        data=response.json()
        df_mmsa = pd.DataFrame(data[1:], columns=data[0])
        # the census variable comes from geocodio... save for later
        # print(f"M{census['metro_micro_statistical_area']['type'][1:]} Statistical Area (Expanded Housing Market Area): ", df_mmsa.loc[0, "NAME"])
        formatted_mmsa = df_mmsa.loc[0, "NAME"]
        df_mmsa.loc[0, "NAME"] = "Expanded Housing Market Area"

        df = pd.concat([df_tract, df_county, df_mmsa])
        df.drop(columns=['state','county','tract','metropolitan statistical area/micropolitan statistical area'],inplace=True)
        df.rename(columns={percent_white["code"]:percent_white["label"],
                            percent_black["code"]:percent_black["label"],
                            percent_hispanic_latino["code"]:percent_hispanic_latino["label"],
                            percent_asian["code"]:percent_asian["label"],
                            percent_american_indian["code"]:percent_american_indian["label"],
                            percent_native_hawaiian["code"]:percent_native_hawaiian["label"],
                            percent_disability["code"]:percent_disability["label"],
                            percent_households_under_18["code"]:percent_households_under_18["label"],
                            "NAME": "DEMOGRAPHIC"
                            }, inplace=True)

        df = df.transpose()
        df.columns = ["Census Tract", "Housing Market Area", "Expanded Housing Market Area"]
        df.drop(index="DEMOGRAPHIC", inplace=True)
        return df, formatted_tract, formatted_county, formatted_mmsa
    else:
        print("No metropolitan statistical area/micropolitan statistical area to calculate Expanded Housing Market Area")
        df = pd.concat([df_tract, df_county])
        df.drop(columns=['state','county','tract'],inplace=True)
        df.rename(columns={percent_white["code"]:percent_white["label"],
                            percent_black["code"]:percent_black["label"],
                            percent_hispanic_latino["code"]:percent_hispanic_latino["label"],
                            percent_asian["code"]:percent_asian["label"],
                            percent_american_indian["code"]:percent_american_indian["label"],
                            percent_native_hawaiian["code"]:percent_native_hawaiian["label"],
                            percent_disability["code"]:percent_disability["label"],
                            percent_households_under_18["code"]:percent_households_under_18["label"],
                            "NAME": "DEMOGRAPHIC"
                            }, inplace=True)

        df = df.transpose()
        df.columns = ["Census Tract", "Housing Market Area"]
        df.drop(index="DEMOGRAPHIC", inplace=True)
        return df, formatted_tract, formatted_county, None

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

        tract, county, state, mmsa, formatted_address = geocodio_helper(search_term)
        
        # Simulate data processing (replace with your actual code)
        # data = pd.DataFrame({
        #     'Category': ['A', 'B', 'C'],
        #     'Value': np.random.randn(3)
        # })
        data, formatted_tract, formatted_county, formatted_mmsa = census("2023", state, county, tract, st.secrets["CENSUS_TOKEN"])
        
        # Display results
        st.subheader(f"Demographic Summary for {formatted_address}")
        st.write(f"Census Tract: {formatted_tract}")
        st.write(f"County (Housing Market Area): {formatted_county}")
        if mmsa is None:
            st.write("No metropolitan statistical area/micropolitan statistical area to calculate Expanded Housing Market Area")
        else:
            st.write(f"Metro/Micropolitan Statistical Area (Expanded Housing Market Area): {formatted_mmsa}")

        # Show data table
        st.subheader("Data Table")
        st.dataframe(data)
        
        # # Download buttons
        # csv = data.to_csv(index=False).encode('utf-8')
        
        # # maybe use the full fip here for download
        # f = formatted_address.strip(" ")
        # st.download_button(
        #     "Download Detailed CSV",
        #     data=csv,
        #     file_name=f"{f}_results.csv",
        #     mime="text/csv"
        # )
    else:
        st.error("Please enter an address")
