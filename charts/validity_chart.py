import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_validity_comparison(brics_csv, eu_csv, output_file='validity_comparison.pdf'):
    # Load the CSV files
    brics_df = pd.read_csv(brics_csv)
    eu_df = pd.read_csv(eu_csv)

    # Merge both datasets into a single DataFrame
    merged_df = brics_df.merge(eu_df, on='validity_category', suffixes=('_BRICS', '_EU'))

    # Extract values for plotting
    categories = merged_df['validity_category']
    brics_counts = merged_df['count_BRICS']
    eu_counts = merged_df['count_EU']

    # Define bar width and positions
    bar_width = 0.4
    x_pos = np.arange(len(categories))

    # Create the figure and axis
    fig, ax = plt.subplots()

    # Plot BRICS and EU bars side by side
    ax.bar(x_pos - bar_width / 2, brics_counts, bar_width, color='gray', edgecolor="black", label='BRICS')
    ax.bar(x_pos + bar_width / 2, eu_counts, bar_width, color='lightgray', edgecolor="black", label='EU')

    # Labels, titles, and formatting
    ax.set_xlabel('Validity Category')
    ax.set_ylabel('Number of Certificates')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(categories)
    ax.legend()

    # Add values above bars
    for i, v in enumerate(brics_counts):
        ax.text(x_pos[i] - bar_width / 2, v + (max(brics_counts) * 0.02), str(v), ha='center', va='bottom', fontweight='bold')
    for i, v in enumerate(eu_counts):
        ax.text(x_pos[i] + bar_width / 2, v + (max(eu_counts) * 0.02), str(v), ha='center', va='bottom', fontweight='bold')

    # Save and show plot
    plt.margins(x=0.02, y=0.1, tight=True)
    fig.tight_layout()
    plt.savefig(output_file)
    plt.close(fig)

# Example usage
plot_validity_comparison('brics_validity.csv', 'eu_validity.csv')
