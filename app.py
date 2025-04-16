import streamlit as st
import pandas as pd
import numpy as np

# App title and description
st.title("Affirmative Fair Housing Marketing Plan (AFHMP) Form Helper")
st.write("Enter a full US address to gather demographic data. No specific formatting necessary.")

# User input
search_term = st.text_input("Address:")

# Process when user clicks button
if st.button("Submit"):
    if search_term:
        st.write(f"Gathering demographic data for: {search_term}")
        
        # Simulate data processing (replace with your actual code)
        data = pd.DataFrame({
            'Category': ['A', 'B', 'C'],
            'Value': np.random.randn(3)
        })
        
        # Display results
        st.subheader("Demographic Summary")
        # st.write(f"Found {len(data)} results")
        
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
