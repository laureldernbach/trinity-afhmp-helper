import streamlit as st
import pandas as pd
import requests
from geocodio import GeocodioClient
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
from shapely.geometry import Point
import requests
from io import BytesIO
import zipfile
import geopandas as gpd
import matplotlib.pyplot as plt

def county_map(year, county_name, state_fip, county_fip ):
    # Download and unzip
    tract_url = f"https://www2.census.gov/geo/tiger/TIGER{year}/COUNTY/tl_{year}_us_county.zip"
    r = requests.get(tract_url, headers={"User-Agent": "Mozilla/5.0"}, verify=False)

    with zipfile.ZipFile(BytesIO(r.content)) as z:
        z.extractall(f"tl_{year}_us_county")

    # Load census tracts for NY state
    counties = gpd.read_file(f"tl_{year}_us_county/tl_{year}_us_county.shp").to_crs(epsg=4326)

    selected = counties[(counties['STATEFP'] == state_fip) & (counties['COUNTYFP'] == county_fip)]
    selected = selected.to_crs(epsg=3857)

    # Plot with basemap
    fig, ax = plt.subplots(figsize=(10, 10))
    selected.plot(ax=ax, edgecolor='red', facecolor='none', linewidth=2)
    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, zoom=10)
    ax.set_title(f"WORKSHEET 1: Expanded Housing Market Area ({county_name})")
    plt.axis('off')
    #plt.show()
    return fig

def tract_map(year, state_fip, lng, lat, tract_name):
    # Download and unzip
    tract_url = f"https://www2.census.gov/geo/tiger/TIGER{year}/TRACT/tl_{year}_{state_fip}_tract.zip"
    r = requests.get(tract_url, headers={"User-Agent": "Mozilla/5.0"}, verify=False)

    with zipfile.ZipFile(BytesIO(r.content)) as z:
        z.extractall(f"tl_{year}_{state_fip}_tract")

    # Load census tracts for NY state
    tracts = gpd.read_file(f"tl_{year}_{state_fip}_tract/tl_{year}_{state_fip}_tract.shp")

    # Ensure CRS is geographic (lat/lon)
    tracts = tracts.to_crs(epsg=4326)
    # Create a point for
    point = Point(float(lng), float(lat))
    print(point)

    # Find the tract containing the point
    selected_tract = tracts[tracts.geometry.contains(point)]
    # Reproject to Web Mercator
    selected_tract = selected_tract.to_crs(epsg=3857)

    # Plot with basemap
    fig, ax = plt.subplots(figsize=(10, 10))
    selected_tract.plot(ax=ax, edgecolor='red', facecolor='none', linewidth=2)
    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)
    ax.set_title(f"WORKSHEET 1: Map of {tract_name}")
    plt.axis('off')
    #plt.show()
    return fig

def mmsa_map(year, cbsa_name):
    url = f"https://www2.census.gov/geo/tiger/TIGER{year}/CBSA/tl_{year}_us_cbsa.zip"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, verify=False)

    # Unzip and load
    with zipfile.ZipFile(BytesIO(r.content)) as z:
        z.extractall(f"tl_{year}_us_cbsa")

    # Load with GeoPandas
    cbsa = gpd.read_file(f"tl_{year}_us_cbsa/tl_{year}_us_cbsa.shp")

    this_cbsa = cbsa[cbsa['NAME'].str.contains(cbsa_name, case=False)]

    this_cbsa = this_cbsa.to_crs(epsg=3857)

    fig, ax = plt.subplots(figsize=(10, 10))
    this_cbsa.plot(ax=ax, facecolor='none', edgecolor='blue', linewidth=2)
    ctx.add_basemap(ax)
    ax.set_title(f"WORKSHEET 1: Expanded Housing Market Area ({cbsa_name})")
    plt.axis('off')
    #plt.show()
    return fig

def dp05_pdf():
    pass

def dp02_pdf():
    pass

def census_summary(year, state, county, tract, mmsa, api_key):
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
        # formatted_mmsa = df_mmsa.loc[0, "NAME"]
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
        return df, formatted_tract
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
        return df, formatted_tract
    
def to_filename(s):
    return ''.join(c for c in s if c.isalnum())

def display_map(fig, fig_name):
    st.pyplot(fig)

    # Save the plot to a buffer
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)

    # Provide download button
    st.download_button(
        label=f"Download {to_filename(fig_name)}.png",
        data=buf,
        file_name=f"{to_filename(fig_name)}.png",
        mime="image/png"
    )

def build_census_url(year, table_id, state_fips, county_fips, tract_code, cbsa_code):
    dataset_code = f"ACSDP5Y{year}"  # Example: ACSDP5Y2023
    base_url = f"https://data.census.gov/table/{dataset_code}.{table_id}"

    # Build geo codes
    county_geo = f"050XX00US{state_fips}{county_fips}"
    tract_geo = f"1400000US{state_fips}{county_fips}{tract_code}"
    cbsa_geo = f"310XX00US{cbsa_code}"

    if cbsa_code is None:
        # ex. https://data.census.gov/table/ACSDP1Y2023.DP05?q=dp05&g=050XX00US47037_1400000US47037016100
        geo_param = f"{county_geo}_{tract_geo}"
        return
    else:
        # ex. https://data.census.gov/table/ACSDP5Y2023.DP05?q=dp05&g=050XX00US47037_1400000US47037016100_310XX00US349801
        cbsa_geo = f"310XX00US{cbsa_code}"
        geo_param = f"{county_geo}_{tract_geo}_{cbsa_geo}"

    return f"{base_url}?q={table_id}&g={geo_param}"

##################################################

if "data" not in st.session_state:
    st.session_state.data = None
if "fig1" not in st.session_state:
    st.session_state.fig1 = None
if "fig2" not in st.session_state:
    st.session_state.fig2 = None
if "fig3" not in st.session_state:
    st.session_state.fig3 = None
if "search_term" not in st.session_state:
    st.session_state.search_term = ""

# App title and description
st.title("Affirmative Fair Housing Marketing Plan (AFHMP) Form Helper")
st.write("Enter a full US address to gather demographic data. No specific formatting necessary.")

# User input
search_term = st.text_input("Address:")

# Process when user clicks button
if st.button("Submit"):
    if search_term:
        st.write(f"Gathering demographic data... This may take a few seconds.")

        client = GeocodioClient(st.secrets["GEOCODIO_TOKEN"])

        location = client.geocode(search_term, fields=["census2023"])

        st.session_state.YEAR = '2023'
        CENSUS = location["results"][0]['fields']['census'][st.session_state.YEAR]
        st.session_state.ADDRESS = location["results"][0]['formatted_address']
        st.session_state.TRACT_CODE = CENSUS['tract_code']
        st.session_state.STATE_CODE = CENSUS['state_fips']
        st.session_state.COUNTY_CODE = CENSUS['county_fips'][2:]
        st.session_state.COUNTY_LABEL = location["results"][0]['address_components']['county']
        LAT = location["results"][0]['location']['lat']
        LNG = location["results"][0]['location']['lng']
        try:
            st.session_state.MMSA = CENSUS['metro_micro_statistical_area']['area_code']
            st.session_state.MMSA_LABEL = CENSUS['metro_micro_statistical_area']['name']
        except:
            st.session_state.MMSA = None
            print("ERROR: No Metropolitan/Micropolitan Statistical Area found for", st.session_state.ADDRESS)
        
        st.session_state.data, st.session_state.formatted_tract = census_summary(st.session_state.YEAR, st.session_state.STATE_CODE, st.session_state.COUNTY_CODE, st.session_state.TRACT_CODE, st.session_state.MMSA, st.secrets["CENSUS_TOKEN"])

        st.session_state.fig1 = tract_map(st.session_state.YEAR,st.session_state.STATE_CODE, LNG, LAT, st.session_state.formatted_tract)
        
        st.session_state.fig2 = county_map(st.session_state.YEAR, st.session_state.COUNTY_LABEL, st.session_state.STATE_CODE, st.session_state.COUNTY_CODE)

        if st.session_state.MMSA is not None:
            st.session_state.fig3 = mmsa_map(st.session_state.YEAR, st.session_state.MMSA_LABEL)

    else:
        st.error("Please enter an address")

# Make sure the data and plots are still rendered if the page is refreshed or interaction occurs
if st.session_state.data is not None and st.session_state.fig1 is not None \
    and st.session_state.fig2 is not None:
    # Display results
    st.subheader(f"Demographic Summary for {st.session_state.ADDRESS}")
    st.write(f"Census Tract: {st.session_state.formatted_tract.split(";")[0]}")
    st.write(f"County (Housing Market Area): {st.session_state.COUNTY_LABEL}")
    if st.session_state.MMSA is None:
        st.write("No Metro/Micropolitan Statistical Area to calculate Expanded Housing Market Area")
    else:
        st.write(f"Metro/Micropolitan Statistical Area (Expanded Housing Market Area): {st.session_state.MMSA_LABEL}")

    # Display the stored data table
    st.subheader("Data Table")
    st.dataframe(st.session_state.data)

    st.write("Download the entire ACS 2023 5-year DP05 Survey on data.census.gov:")
    st.write(build_census_url("2023", "DP05", st.session_state.STATE_CODE, st.session_state.COUNTY_CODE, st.session_state.TRACT_CODE, st.session_state.MMSA_CODE))
    st.write("Download the entire ACS 2023 5-year DP02 Survey on data.census.gov:")
    st.write(build_census_url("2023", "DP02", st.session_state.STATE_CODE, st.session_state.COUNTY_CODE, st.session_state.TRACT_CODE, st.session_state.MMSA_CODE))
    
    display_map(st.session_state.fig1, st.session_state.formatted_tract)

    display_map(st.session_state.fig2, st.session_state.COUNTY_LABEL)

    if st.session_state.MMSA is not None:
        display_map(st.session_state.fig3, st.session_state.MMSA_LABEL)