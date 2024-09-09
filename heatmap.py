import plotly.express as px
import pandas as pd
import numpy as np
import pycountry

def plot_country_heatmap(countries, values):
    """
    Generates a choropleth map heatmap based on the provided countries and values,
    handling countries with no values and addressing large discrepancies in the dataset.

    Parameters:
    - countries: list of country names (strings)
    - values: list of values (integers or floats) corresponding to the countries
    """
    # Create a dataframe from the input lists
    df = pd.DataFrame({
        'Country': countries,
        'Values': values
    })

    # Group by country and sum the certificate counts to avoid duplicates
    df = df.groupby('Country', as_index=False)['Values'].sum()

    # Get all available country names from pycountry
    all_countries = [country.name for country in pycountry.countries]

    # Create a DataFrame for all countries and merge with the existing data
    all_countries_df = pd.DataFrame({'Country': all_countries})

    # Merge the data with all countries, filling missing values with 0
    df = pd.merge(all_countries_df, df, on='Country', how='left').fillna(0)

    # Apply a logarithmic transformation to the values to handle large discrepancies
    # Adding 1 to avoid issues with log(0)
    df['LogValues'] = np.log1p(df['Values'])

    # Define the color scale based on the data's distribution
    color_scale = 'Plasma'

    # Define the range for the color scale based on log-transformed values
    min_value = df['LogValues'].min()
    max_value = df['LogValues'].max()

    # Plot the choropleth map using Plotly Express with log-transformed values
    fig = px.choropleth(
        df, 
        locations='Country', 
        locationmode='country names', 
        color='LogValues', 
        color_continuous_scale=color_scale,
        range_color=(min_value, max_value),  # Adjust color scale range using the log-transformed values
        title='Country Heatmap: Number of Issued Certificates (Log Scale)'
    )

    # Customize the color bar to show more meaningful ticks based on original values
    fig.update_layout(
        coloraxis_colorbar=dict(
            title="Certificates (Log Scale)",
            tickvals=[min_value, (min_value + max_value) / 2, max_value],
            ticktext=[
                f'{int(np.expm1(min_value))}',  # Convert back from log scale to original
                f'{int(np.expm1((min_value + max_value) / 2))}',
                f'{int(np.expm1(max_value))}'
            ]
        )
    )

    # Show the plot
    fig.show()
