import matplotlib.pyplot as plt
import pandas as pd
import numpy as np  

# Read the data from the CSV file
data = pd.read_csv('top_eu.csv')

# Calculate total certificates (sum of all rows)
total_sum = data['certificate_count'].sum()

# Select only the top 5 countries for plotting
top_data = data.head(5)

# Extract required columns
groups = top_data['country']
total_certs = top_data['certificate_count']

# Compute percentages based on total dataset
percentages = (total_certs / total_sum) * 100  

# Create a figure and axis
fig, ax = plt.subplots()

ax.set_axisbelow(True)
plt.grid(True, color='silver', linestyle='solid')

# Increase bar width for better visibility
bar_width = 0.5  

# Bring bars closer together
x_pos = np.arange(len(groups)) * 0.6  # Reduce spacing factor

# Create the bars
bars = ax.bar(x_pos, percentages, bar_width, lw=0.75, edgecolor="black", color='lightgray')

# Set labels
ax.set_xlabel('Certificate Authority Country')
ax.set_ylabel('Percentage of Issued Certificates')
ax.set_xticks(x_pos)
ax.set_xticklabels(groups)

# Display percentage values above bars
for bar, v in zip(bars, percentages):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{v:.1f}%", 
            ha='center', va='bottom', fontweight='bold')

# Reduce extra margins
plt.margins(x=0.01, y=0.1, tight=True)

# Make layout tighter
fig.tight_layout()

# Save the graph
plt.savefig('top_eu.pdf')

# Close the figure
plt.close(fig)
