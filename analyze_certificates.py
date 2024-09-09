import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pycountry
import heatmap


def plot_eu_vs_non_eu_individual_counts(df, eu_country_codes):
    # Remove the 'C=' prefix from the 'country' column
    df['country_code'] = df['country'].apply(lambda c: c.split('=')[1] if isinstance(c, str) and c.startswith('C=') else None)

    # Classify each domain's country as 'EU' or 'Non-EU'
    df['is_eu'] = df['country_code'].apply(lambda c: 'EU' if c in eu_country_codes else 'Non-EU')

    # Count the number of domains for EU countries (grouped into one) and non-EU countries (individually)
    eu_count = df[df['is_eu'] == 'EU'].shape[0]
    non_eu_counts = df[df['is_eu'] == 'Non-EU']['country_code'].value_counts()

    # Create a DataFrame for plotting
    data = {
        'Category': ['EU Countries'] + non_eu_counts.index.tolist(),
        'Count': [eu_count] + non_eu_counts.tolist()
    }
    plot_df = pd.DataFrame(data)

    # Plot the bar chart using seaborn
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Category', y='Count', data=plot_df, palette='Set3')

    # Add title and labels
    plt.title('Incidence of Domains from EU and Non-EU Countries')
    plt.xlabel('Country')
    plt.ylabel('Number of Domains')

    # Rotate x-axis labels for readability
    plt.xticks(rotation=45, ha='right')

    # Add exact counts above the bars
    for i, count in enumerate(plot_df['Count']):
        plt.text(i, count + 10, f'{count}', ha='center', va='bottom')

    plt.tight_layout()
    plt.show()

def plot_combined_top_4_country_counts(df_filtered, country_counts_by_suffix, suffixes):
    # Create an empty list to store the data for the plot
    plot_data = []

    # Iterate over each suffix and extract the top 4 countries and their counts
    for suffix in suffixes:
        if suffix in country_counts_by_suffix:
            top_4_counts = country_counts_by_suffix[suffix].nlargest(4)
            for country, count in top_4_counts.items():
                plot_data.append([suffix, country, count])

    # Convert the list to a DataFrame for easier plotting
    plot_df = pd.DataFrame(plot_data, columns=['Suffix', 'Country', 'Count'])

    # Get all unique countries and generate a color palette with as many unique colors as needed
    unique_countries = plot_df['Country'].unique()
    palette = sns.color_palette("hsv", len(unique_countries))  # Generating unique colors

    # Create a dictionary to map each country to its unique color
    country_color_map = dict(zip(unique_countries, palette))

    # Create a grouped bar plot with seaborn (suffixes on the x-axis, counts on the y-axis)
    plt.figure(figsize=(12, 8))
    
    # Map the color palette based on the 'Country' column
    sns.barplot(x='Suffix', y='Count', hue='Country', data=plot_df, 
                palette=country_color_map)

    # Rotate the x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')

    # Add title and labels
    plt.title('Top 4 Country Counts for Each Suffix')
    plt.xlabel('Domain Suffix')
    plt.ylabel('Number of Occurrences')

    # Add a legend to indicate which color corresponds to which country
    plt.legend(title='Country')

    plt.tight_layout()
    plt.show()

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

def extract_company(issuer):
    """
    Extracts the company name from the 'issuer' field.
    Assumes the format 'O=company_name' where 'O=' precedes the company name.
    """
    # Split the issuer string by commas
    fields = issuer.split(',')
    # Find the field that starts with 'O='
    for field in fields:
        if field.strip().startswith('O='):
            return field.strip().split('=')[1]  # Return the company name after 'O='
    return None

def analyze_top_companies_by_country(df, top_n=5):
    # Extract company names from the 'issuer' column
    df['company'] = df['issuer'].apply(extract_company)

    # Filter rows where company and country are not null
    df_filtered = df[df['company'].notnull() & df['country'].notnull()]

    # Remove the 'C=' prefix from the 'country' column to get the actual country code
    df_filtered['country_code'] = df_filtered['country'].apply(lambda c: c.split('=')[1] if isinstance(c, str) and c.startswith('C=') else None)

    # Group by country and company, and count the occurrences
    company_counts_by_country = df_filtered.groupby(['country_code', 'company']).size().reset_index(name='count')

    # For each country, get the top N companies
    top_companies_by_country = company_counts_by_country.groupby('country_code').apply(
        lambda group: group.nlargest(top_n, 'count')
    ).reset_index(drop=True)

    # Print the top companies for each country
    for country_code, group in top_companies_by_country.groupby('country_code'):
        print(f"\nTop {top_n} companies for country {country_code}:")
        print(group[['company', 'count']])

    # Optionally, you can plot the data for each country as a bar chart
    plot_top_companies_by_country(top_companies_by_country, top_n)

def analyze_top_companies_by_country(df, top_n=5):
    # Extract company names from the 'issuer' column
    df['company'] = df['issuer'].apply(extract_company)

    # Filter rows where company and country are not null
    df_filtered = df[df['company'].notnull() & df['country'].notnull()]

    # Remove the 'C=' prefix from the 'country' column to get the actual country code
    df_filtered['country_code'] = df_filtered['country'].apply(lambda c: c.split('=')[1] if isinstance(c, str) and c.startswith('C=') else None)

    # Group by country and company, and count the occurrences
    company_counts_by_country = df_filtered.groupby(['country_code', 'company']).size().reset_index(name='count')

    # For each country, get the top N companies
    top_companies_by_country = company_counts_by_country.groupby('country_code').apply(
        lambda group: group.nlargest(top_n, 'count')
    ).reset_index(drop=True)

    # Print the top companies for each country
    for country_code, group in top_companies_by_country.groupby('country_code'):
        print(f"\nTop {top_n} companies for country {country_code}:")
        print(group[['company', 'count']])

    # Plot each country's top companies separately
    plot_top_companies_separately(top_companies_by_country, top_n)

def plot_top_companies_separately(top_companies_df, top_n):
    """
    Plots the top N companies for each country in separate figures.
    """
    # Get the unique list of countries
    countries = top_companies_df['country_code'].unique()

    # Iterate over each country and create a separate figure for each
    for country in countries:
        country_df = top_companies_df[top_companies_df['country_code'] == country]

        # Sort the data by count
        country_df = country_df.sort_values(by='count', ascending=False)

        # Create a new figure for each country
        plt.figure(figsize=(10, 6))

        # Plot the data for this country
        sns.barplot(x='count', y='company', data=country_df, palette='Set2')

        # Set title and labels
        plt.title(f"Top {top_n} Companies in {country}")
        plt.xlabel('Number of Certificates Issued')
        plt.ylabel('Company')

        # Add exact counts above the bars
        for i, row in country_df.iterrows():
            plt.text(row['count'] + 0.1, i, f'{row["count"]}', va='center')

        # Show the plot for this country
        plt.tight_layout()
        plt.show()

def plot_certificate_heatmap(df):
    """
    Plots a heatmap showing the countries with the most issued certificates.

    Parameters:
    - df: DataFrame containing 'country' and 'issuer' columns.
    """
    # Ensure the country field is cleaned ('C=XX' format)
    df['country_code'] = df['country'].apply(lambda c: c.split('=')[1] if isinstance(c, str) and c.startswith('C=') else None)
    
    # Count the number of certificates issued per country
    country_counts = df['country_code'].value_counts().reset_index()
    country_counts.columns = ['Country', 'Certificate Count']
    
    country_counts['Country'] = country_counts['Country'].apply(get_country_name)
    country_counts = country_counts.dropna(subset=['Country'])  # Drop rows where country name conversion failed

    # Prepare the lists of country names and their corresponding certificate counts
    countries = country_counts['Country'].tolist()
    values = country_counts['Certificate Count'].tolist()

    # Plot the heatmap using the provided function
    heatmap.plot_country_heatmap(countries, values)


# Replace country codes (ISO Alpha-2 codes) with country names for the heatmap
    # We'll use pycountry to convert country codes to full country names
def get_country_name(country_code):
    try:
        return pycountry.countries.get(alpha_2=country_code).name
    except:
        return None

# Modify the get_countries function to call the combined plotting function
def get_countries(csv_filename):
    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_filename)

    # Drop duplicate rows based on the 'domain' column, keeping the first occurrence
    df = df.drop_duplicates(subset='domain', keep='first')

    # Apply the function to the 'issuer' column and create a new column with the extracted country code
    df['country'] = df['issuer'].apply(extract_country)

    # Create a new column 'suffix' in the DataFrame to store the suffix of each domain
    suffixes = [
        ".eu", ".at", ".be", ".bg", ".hr", ".cy", ".cz", ".dk", ".ee", ".fi", 
        ".fr", ".de", ".gr", ".hu", ".ie", ".it", ".lv", ".lt", ".lu", ".mt", 
        ".nl", ".pl", ".pt", ".ro", ".sk", ".si", ".es", ".se"
    ]
    eu_country_codes = [
        'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 
        'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 
        'RO', 'SK', 'SI', 'ES', 'SE'
    ]
    df['suffix'] = df['domain'].apply(lambda x: next((s for s in suffixes if x.endswith(s)), None))

    # Filter the DataFrame to keep only rows with the defined suffixes
    df_filtered = df[df['suffix'].notnull()]

    # Group by 'suffix' and count the occurrences of each country
    country_counts_by_suffix = df_filtered.groupby('suffix')['country'].value_counts()

    # Call the new combined plotting function with inverted axes and color palette
    #plot_combined_top_4_country_counts(df_filtered, country_counts_by_suffix, suffixes)

    # Call the percentage plot function
    #plot_top_countries_percentage(df, country_column='country')
    #plot_eu_vs_non_eu_individual_counts(df, eu_country_codes)
    plot_certificate_heatmap(df)
    #analyze_top_companies_by_country(df, top_n=5)

def main():
    get_countries('eu_certificates.csv')

if __name__ == '__main__':
    main()