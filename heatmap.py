import plotly.express as px
import pandas as pd

# Example Data
df = pd.DataFrame({
    'Country': ['France', 'Germany', 'United States', 'Japan'],
    'Values': [100, 200, 300, 150]
})

# Generate a choropleth heatmap
fig = px.choropleth(df, locations='Country', locationmode='country names', color='Values', 
                    color_continuous_scale='Viridis', title='World Heatmap')

fig.show()
