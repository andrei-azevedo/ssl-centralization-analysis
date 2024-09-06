import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def get_countries(csv_filename):

    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_filename)

    # Drop duplicate rows based on the 'domain' column, keeping the first occurrence
    df = df.drop_duplicates(subset='domain', keep='first')

    # Apply the function to the 'issuer' column and create a new column with the extracted country code
    df['country'] = df['issuer'].apply(extract_country)
    # Count the unique countries and their occurrences
    country_counts = df['country'].value_counts()
    #suffixes = ['.br', '.ru', '.in', '.za', '.cn']
    suffixes = [
    ".eu", ".at", ".be", ".bg", ".hr", ".cy", ".cz", ".dk", ".ee", ".fi", 
    ".fr", ".de", ".gr", ".hu", ".ie", ".it", ".lv", ".lt", ".lu", ".mt", 
    ".nl", ".pl", ".pt", ".ro", ".sk", ".si", ".es", ".se"
    ]
    # Print the DataFrame to see the results
    #print(df[['domain', 'issuer', 'country']])
    # Print the unique countries and their occurrences
    #print("\nUnique countries and their occurrences:")
    #print(country_counts)
    # Create a new column 'suffix' in the DataFrame to store the suffix of each domain
    df['suffix'] = df['domain'].apply(lambda x: next((s for s in suffixes if x.endswith(s)), None))

    # Filter the DataFrame to keep only rows with the defined suffixes
    df_filtered = df[df['suffix'].notnull()]

    # Group by 'suffix' and count the occurrences of each country
    country_counts_by_suffix = df_filtered.groupby('suffix')['country'].value_counts()

    # Print the results
    print("\nCountry counts by domain suffix:")
    print(country_counts_by_suffix)
    # Generate and plot the graphics for each suffix
    for suffix in suffixes:
        if suffix in country_counts_by_suffix:
            total_domains = df_filtered[df_filtered['suffix'] == suffix].shape[0]
            print(f"\nTop 4 country counts for suffix {suffix}:")
            top_4_counts = country_counts_by_suffix[suffix].nlargest(4)
            print(top_4_counts)
            plot_top_4_country_counts(suffix, country_counts_by_suffix[suffix], total_domains)
    plot_top_countries_percentage(df, country_column='country')

# Function to extract the 'C=' field from the issuer string
def extract_country(issuer):
    # Split the issuer string by commas
    fields = issuer.split(',')
    # Find the field that starts with 'C='
    for field in fields:
        if field.strip().startswith('C='):
            return field.strip()
    return None

# Function to plot the top 4 country counts for a given suffix (without normalization)
def plot_top_4_country_counts(suffix, counts, total_domains):
    # Get the top 4 countries by count
    top_4_counts = counts.nlargest(4)
    
    # Generate a grayscale color palette for the bars
    colors = sns.color_palette("gray", len(top_4_counts))
    
    # Plot the top 4 country counts side by side with grayscale colors
    ax = top_4_counts.plot(kind='bar', color=colors, width=0.8)
    
    plt.title(f'Top 4 Country Counts for Suffix {suffix}')
    plt.xlabel('Country')
    plt.ylabel('Number of Occurrences')
    plt.xticks(rotation=45, ha='right')
    
    # Add total number of domains as text in the plot
    plt.text(0.95, 0.95, f'Total domains: {total_domains}', 
             horizontalalignment='right', 
             verticalalignment='top', 
             transform=ax.transAxes, 
             fontsize=10, 
             bbox=dict(facecolor='white', alpha=0.5))
    
    plt.tight_layout()
    plt.show()


def plot_top_countries_percentage(df, country_column='country'):
    # Count the occurrences of each country
    country_counts = df[country_column].value_counts()

    # Calculate the total number of domains
    total_domains = country_counts.sum()

    # Calculate the percentage for each country
    country_percentages = (country_counts / total_domains) * 100

    # Select the top 5 countries
    top_countries = country_percentages.head(5)

    # Generate a scale of gray colors
    colors = [str(0.2 + 0.15 * i) for i in range(len(top_countries))]

    # Plotting
    plt.figure(figsize=(10, 6))
    bars = plt.bar(top_countries.index, top_countries, color=colors, width=0.8)

    # Add the exact percentage above each bar
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2.0, height,
                 f'{height:.2f}%', ha='center', va='bottom')

    # Add total domains text on the plot
    plt.text(0.95, 0.95, f'Total domains: {total_domains}', 
             horizontalalignment='right', 
             verticalalignment='top',              
             transform=plt.gca().transAxes, 
             fontsize=10, 
             bbox=dict(facecolor='white', alpha=0.5))

    
    plt.xlabel('Country')
    plt.ylabel('Percentage of Total Domains (%)')
    plt.title('Top 5 Countries by Domain Percentage')
    plt.show()

def main():
    get_countries('eu_certificates.csv')

if __name__ == '__main__':
    main()