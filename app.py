import streamlit as st
import pandas as pd
import numpy as np

# App title and description
st.title("My Data Analysis App")
st.write("Enter a search term to analyze data")

# User input
search_term = st.text_input("Search term:")

# Process when user clicks button
if st.button("Analyze"):
    if search_term:
        st.write(f"Analyzing data for: {search_term}")
        
        # Simulate data processing (replace with your actual code)
        data = pd.DataFrame({
            'Category': ['A', 'B', 'C'],
            'Value': np.random.randn(3)
        })
        
        # Display results
        st.subheader("Results Summary")
        st.write(f"Found {len(data)} results")
        
        # Show data table
        st.subheader("Data Table")
        st.dataframe(data)
        
        # Download buttons
        csv = data.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            "Download CSV",
            data=csv,
            file_name=f"{search_term}_results.csv",
            mime="text/csv"
        )
    else:
        st.error("Please enter a search term")

# Footer
st.markdown("---")
st.caption("Created with Streamlit")
