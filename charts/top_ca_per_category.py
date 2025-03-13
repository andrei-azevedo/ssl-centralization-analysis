import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_top_cas_by_validity(csv_file, output_file='top_cas_by_validity.pdf'):
    # Load the CSV file
    df = pd.read_csv(csv_file)

    # Ensure all validity categories are present (matching CSV labels exactly)
    categories = ["Short-term (≤90 days)", "Medium-term (91-180 days)", "Long-term (>=181 days)"]

    # Define colors for each validity category
    category_colors = {
        "Short-term (≤90 days)": "darkgray",
        "Medium-term (91-180 days)": "gray",
        "Long-term (>=181 days)": "lightgray",
    }

    # Identify the top-3 CAs per validity category
    top_cas = df.groupby('validity_category').apply(lambda x: x.nlargest(3, 'certificate_count')).reset_index(drop=True)

    # Ensure each category has exactly 3 CAs (add placeholders if needed)
    complete_data = []
    for category in categories:
        category_data = top_cas[top_cas['validity_category'] == category]

        # Add missing entries if there are fewer than 3
        while len(category_data) < 3:
            category_data = pd.concat([
                category_data,
                pd.DataFrame([{"validity_category": category, "certificate_authority": "N/A", "certificate_count": 0}])
            ], ignore_index=True)

        complete_data.append(category_data)

    # Merge back into a single DataFrame
    top_cas = pd.concat(complete_data, ignore_index=True)

    # Define bar width and positions
    bar_width = 0.3
    x_pos = np.arange(len(categories))

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(8, 5))
    plt.grid(True, color='silver')

    # Plot bars for each validity category
    for i, category in enumerate(categories):
        category_data = top_cas[top_cas['validity_category'] == category]

        for j, (_, row) in enumerate(category_data.iterrows()):
            bar_x = x_pos[i] + (j - 1) * bar_width  
            ax.bar(bar_x, row['certificate_count'], bar_width, color=category_colors[category], edgecolor="black")

            if row['certificate_authority'] == 'Google Trust Services':
                ax.text(bar_x + 0.07, row['certificate_count'] * 1, row['certificate_authority'], 
                        ha='center', va='bottom', fontsize=6, fontweight='bold', rotation=30)
            # Add CA names with a **smaller font size**
            elif row['certificate_authority'] != "N/A":
                ax.text(bar_x, row['certificate_count'] * 1, row['certificate_authority'], 
                        ha='center', va='bottom', fontsize=6, fontweight='bold', rotation=30)  # Reduced fontsize

    # Set labels and formatting
    ax.set_xlabel('Validity Category')
    ax.set_ylabel('Number of Issued Certificates')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(categories)
    
    # Adjust layout and save the plot
    plt.margins(x=0.02, y=0.1, tight=True)
    fig.tight_layout()
    plt.savefig(output_file)
    plt.close(fig)

    print(f"Plot saved as {output_file}")

# Example usage
plot_top_cas_by_validity("certificates_by_validity.csv")
