import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pycountry
import constants

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

def plot_top_5_companies_by_suffix(df):
    # Add a new column for company names extracted from 'issuer'
    df['company'] = df['issuer'].apply(extract_company)
    
    # Group by suffix and find the top 5 companies for each suffix
    for suffix in df['suffix'].unique():
        # Filter the dataframe for the current suffix
        suffix_df = df[df['suffix'] == suffix]
        
        # Count occurrences of each company
        company_counts = suffix_df['company'].value_counts().nlargest(5)
        
        # Plotting the top 5 companies for the current suffix
        company_counts.plot(kind='bar', color='skyblue')
        plt.title(f"Top 5 Companies for {suffix} Suffix")
        plt.ylabel('Certificate Count')
        plt.xlabel('Company')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()

def plot_top_5_companies_overall(df):
    # Add a new column for company names extracted from 'issuer'
    df['company'] = df['issuer'].apply(extract_company)
    
    # Count occurrences of each company across the entire dataframe
    company_counts = df['company'].value_counts().nlargest(5)
    
    # Plotting the top 5 companies overall
    company_counts.plot(kind='bar', color='skyblue')
    plt.title("Top 5 Companies Overall")
    plt.ylabel('Certificate Count')
    plt.xlabel('Company')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

def cap_out_of_bounds_dates(series, min_date=None, max_date=None):
    """
    Cap out-of-bounds dates in the series to specified limits.
    """
    series = pd.to_datetime(series, errors='coerce')
    
    # Use default pandas min and max datetime limits if not provided
    min_date = pd.Timestamp.min if min_date is None else pd.to_datetime(min_date)
    max_date = pd.Timestamp.max if max_date is None else pd.to_datetime(max_date)
    
    # Cap the dates
    series = series.where(series >= min_date, min_date)
    series = series.where(series <= max_date, max_date)
    
    return series

def plot_cert_expiration_by_suffix(df):
    # Define the cap limits for datetime (min_date is optional if you want to set lower bounds)
    max_valid_date = '2262-04-11'

    # Ensure 'not_before' and 'not_after' are capped to avoid out-of-bounds dates
    df['not_before'] = cap_out_of_bounds_dates(df['not_before'])
    df['not_after'] = cap_out_of_bounds_dates(df['not_after'], max_date=max_valid_date)

    # Filter out rows where 'not_after' is earlier than 'not_before'
    df = df[df['not_after'] > df['not_before']]

    # Calculate the certificate duration (in years)
    df['Years to Expiration'] = (df['not_after'] - df['not_before']).dt.total_seconds() / (365 * 24 * 3600)

    # Define bins and labels for the expiration groups
    bins = [-float('inf'), 1, 5, 10, float('inf')]
    labels = ['< 1 year', '1-5 years', '5-10 years', '> 10 years']

    # Create a new column that categorizes the expiration into intervals
    df['Expiration Group'] = pd.cut(df['Years to Expiration'], bins=bins, labels=labels)

    # Group by suffix and expiration group, then count the certificates
    grouped = df.groupby(['suffix', 'Expiration Group']).size().unstack(fill_value=0)

    # Plotting certificate expiration distribution for each suffix
    for suffix in grouped.index:
        grouped.loc[suffix].plot(kind='bar', stacked=True)
        plt.title(f"Certificate Expiration Distribution for .{suffix} Domains")
        plt.ylabel('Certificate Count')
        plt.xlabel('Expiration Group')
        plt.xticks(rotation=0)
        plt.tight_layout()
        plt.show()

def plot_cert_expiration_overall(df):
    # Define the cap limits for datetime (min_date is optional if you want to set lower bounds)
    max_valid_date = '2262-04-11'

    # Ensure 'not_before' and 'not_after' are capped to avoid out-of-bounds dates
    df['not_before'] = cap_out_of_bounds_dates(df['not_before'])
    df['not_after'] = cap_out_of_bounds_dates(df['not_after'], max_date=max_valid_date)

    # Filter out rows where 'not_after' is earlier than 'not_before'
    df = df[df['not_after'] > df['not_before']]

    # Calculate the certificate duration (in years)
    df['Years to Expiration'] = (df['not_after'] - df['not_before']).dt.total_seconds() / (365 * 24 * 3600)

    # Define bins and labels for the expiration groups
    bins = [-float('inf'), 1, 5, 10, float('inf')]
    labels = ['< 1 year', '1-5 years', '5-10 years', '> 10 years']

    # Create a new column that categorizes the expiration into intervals
    df['Expiration Group'] = pd.cut(df['Years to Expiration'], bins=bins, labels=labels)

    # Group by expiration group and count the certificates
    grouped = df.groupby('Expiration Group').size()

    # Plotting overall certificate expiration distribution
    grouped.plot(kind='bar', stacked=True, color='skyblue')
    plt.title("Overall Certificate Expiration Distribution")
    plt.ylabel('Certificate Count')
    plt.xlabel('Expiration Group')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.show()

# Replace country codes (ISO Alpha-2 codes) with country names for the heatmap
    # We'll use pycountry to convert country codes to full country names
def get_country_name(country_code):
    try:
        return pycountry.countries.get(alpha_2=country_code).name
    except:
        return None

# Function to convert 'C=xx' to 'xxx' (alpha-3 code)
def convert_to_alpha_3(country_code):
    if country_code.startswith('C='):
        alpha_2 = country_code.split('=')[1]
        try:
            alpha_3 = pycountry.countries.get(alpha_2=alpha_2).alpha_3
            return alpha_3
        except AttributeError:
            return None  # Handle cases where the country code is not found
    return None

# Modify the get_countries function to call the combined plotting function
def get_countries(csv_filename):
    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_filename)

    # Drop duplicate rows based on the 'domain' column, keeping the first occurrence
    df = df.drop_duplicates(subset='domain', keep='first')
    df = df.dropna(subset='issuer')

    # Apply the function to the 'issuer' column and create a new column with the extracted country code
    df['country'] = df['issuer'].apply(extract_country)
    # Drop rows where 'country' is None
    df = df.dropna(subset=['country'])

    df['suffix'] = df['domain'].apply(lambda x: next((s for s in constants.eu_suffixes if x.endswith(s)), None))

    # Filter the DataFrame to keep only rows with the defined suffixes
    df= df[df['suffix'].notnull()]
    df['country'] = df['country'].apply(convert_to_alpha_3)
    #plot_cert_expiration_overall(df)
    #plot_top_5_companies_by_suffix(df)
    plot_top_5_companies_overall(df)


def main():
    get_countries('./csv/eu_certificates.csv')

if __name__ == '__main__':
    main()