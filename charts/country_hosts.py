import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_certificates_by_country(csv_file, output_file='certificates_by_country.pdf'):
    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file)

    # Extract relevant columns
    suffixes = df['domain']
    total_certs = df['total']
    in_country_certs = df['in-country']

    # Define bar width and positions
    bar_width = 0.4
    x_pos = np.arange(len(suffixes))

    # Create figure and axis
    fig, ax = plt.subplots()
    ax.set_axisbelow(True)
    plt.grid(True, color='silver', linestyle='solid')

    # Plot total certificates and in-country certificates side by side
    ax.bar(x_pos - bar_width / 2, total_certs, bar_width, color='gray', edgecolor="black", label='Total Certificates')
    ax.bar(x_pos + bar_width / 2, in_country_certs, bar_width, color='lightgray', edgecolor="black", label='Issued by CAs in Country')
    # Set labels and formatting
    ax.set_xlabel('Government Domain')
    ax.set_ylabel('Number of Issued Certificates')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(suffixes, ha='right')
    ax.legend()

    # Add values above bars
    for i, v in enumerate(total_certs):
        ax.text(x_pos[i] - bar_width / 2, v * 1, str(v), ha='center', va='bottom', fontweight='bold')
    for i, v in enumerate(in_country_certs):
        ax.text(x_pos[i] + bar_width / 2, v * 1.05, str(v), ha='center', va='bottom', fontweight='bold')

    # Adjust layout and save the plot
    plt.margins(x=0.02, y=0.1, tight=True)
    fig.tight_layout()
    plt.savefig(output_file)
    plt.close(fig)

# Example usage
plot_certificates_by_country('eu_hosts.csv')
