import pandas as pd
import matplotlib.pyplot as plt

def get_countries(csv_filename):

    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_filename)

    # Drop duplicate rows based on the 'domain' column, keeping the first occurrence
    df = df.drop_duplicates(subset='domain', keep='first')

    # Apply the function to the 'issuer' column and create a new column with the extracted country code
    df['country'] = df['issuer'].apply(extract_country)
    # Count the unique countries and their occurrences
    country_counts = df['country'].value_counts()
    suffixes = ['.br', '.ru', '.in', '.za', '.cn']
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
            print(f"\nNormalized country counts for suffix {suffix}:")
            print(country_counts_by_suffix[suffix] / country_counts_by_suffix[suffix].sum())
            plot_normalized_country_counts(suffix, country_counts_by_suffix[suffix])

# Function to extract the 'C=' field from the issuer string
def extract_country(issuer):
    # Split the issuer string by commas
    fields = issuer.split(',')
    # Find the field that starts with 'C='
    for field in fields:
        if field.strip().startswith('C='):
            return field.strip()
    return None

def plot_normalized_country_counts(suffix, counts):
    # Normalize the counts by dividing by the total count for the suffix
    normalized_counts = counts / counts.sum()
    
    # Plot the normalized counts
    normalized_counts.plot(kind='bar', color='grey')
    plt.title(f'Normalized Country Counts for Suffix {suffix}')
    plt.xlabel('Country')
    plt.ylabel('Proportion of Occurrences')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

def main():
    get_countries('certificates.csv')

if __name__ == '__main__':
    main()