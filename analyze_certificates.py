import pandas as pd

def get_countries(csv_filename):

    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_filename)

    # Drop duplicate rows based on the 'domain' column, keeping the first occurrence
    df = df.drop_duplicates(subset='domain', keep='first')

    # Apply the function to the 'issuer' column and create a new column with the extracted country code
    df['country'] = df['issuer'].apply(extract_country)
    # Count the unique countries and their occurrences
    country_counts = df['country'].value_counts()
    
    # Print the DataFrame to see the results
    print(df[['domain', 'issuer', 'country']])
    # Print the unique countries and their occurrences
    print("\nUnique countries and their occurrences:")
    print(country_counts)

# Function to extract the 'C=' field from the issuer string
def extract_country(issuer):
    # Split the issuer string by commas
    fields = issuer.split(',')
    # Find the field that starts with 'C='
    for field in fields:
        if field.strip().startswith('C='):
            return field.strip()
    return None

def main():
    get_countries('certificates.csv')

if __name__ == '__main__':
    main()