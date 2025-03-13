import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pycountry
import constants

# Function to extract the 'C=' field from the issuer string
def extract_country(issuer):
    # Split the issuer string by commas
    fields = issuer.split(',')
    # Find the field that starts with 'C='
    for field in fields:
        if field.strip().startswith('C='):
            return field.strip()
    return None

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

    # Convert suffix (".xx") to its corresponding alpha-3 country code for comparison
    df['suffix_country'] = df['suffix'].apply(lambda s: convert_to_alpha_3(f'C={s[1:].upper()}'))  # Remove '.' and convert

    # Group by suffix and calculate total counts
    result = df.groupby('suffix').agg(
        total_certs=('suffix', 'count'),
        certs_emitted_inside_country=('country', lambda x: (x == df.loc[x.index, 'suffix_country']).sum())
    ).reset_index()

    # Save results to CSV
    result.to_csv('eu.csv', index=False)

def get_brics_cert_stats(csv_filename, output_csv):
    df = pd.read_csv(csv_filename)

    df = df.drop_duplicates(subset='domain', keep='first')
    df = df.dropna(subset=['issuer'])

    df['country'] = df['issuer'].apply(extract_country)
    df = df.dropna(subset=['country'])

    # Convert country to alpha-3 code
    df['country'] = df['country'].apply(convert_to_alpha_3)

    # Extract suffix in format '.xx' and filter only BRICS domains
    df['suffix'] = df['domain'].apply(lambda x: next((s for s in constants.eu_suffixes if x.endswith(s)), None))
    df = df[df['suffix'].notnull()]

    # Assign BRICS group to domains
    df['group'] = 'EU'

    # Map BRICS countries to the BRICS group
    eu_countries = {convert_to_alpha_3(f'C={s[1:].upper()}') for s in constants.eu_suffixes}
    df['issuer_group'] = df['country'].apply(lambda c: 'EU' if c in eu_countries else 'Other')

    # Group by suffix and calculate totals
    result = df.groupby('suffix').agg(
        total_certs=('suffix', 'count'),
        certs_emitted_inside_group=('issuer_group', lambda x: (x == 'EU').sum())
    ).reset_index()

    # Save results to CSV
    result.to_csv(output_csv, index=False)

def get_brics_cert_totals(csv_filename, output_csv):
    df = pd.read_csv(csv_filename)

    df = df.drop_duplicates(subset='domain', keep='first')
    df = df.dropna(subset=['issuer'])

    df['country'] = df['issuer'].apply(extract_country)
    df = df.dropna(subset=['country'])

    # Convert country to alpha-3 code
    df['country'] = df['country'].apply(convert_to_alpha_3)

    # Extract suffix and filter only BRICS domains
    df['suffix'] = df['domain'].apply(lambda x: next((s for s in constants.eu_suffixes if x.endswith(s)), None))
    df = df[df['suffix'].notnull()]

    # List of BRICS countries in alpha-3 format
    brics_countries = {convert_to_alpha_3(f'C={s[1:].upper()}') for s in constants.eu_suffixes}

    # Check if the certificate was issued inside BRICS
    df['issued_in_brics'] = df['country'].apply(lambda c: c in brics_countries)

    # Compute total values
    total_certs = len(df)
    certs_emitted_inside_group = df['issued_in_brics'].sum()

    # Save results as a single line CSV
    result_df = pd.DataFrame([{
        "group": "EU",
        "total_certs": total_certs,
        "certs_emitted_inside_group": certs_emitted_inside_group
    }])

    result_df.to_csv(output_csv, index=False)

def categorize_validity_days(days):
    """Categorizes certificates into short, medium, or long validity groups."""
    if days <= 90:
        return "Short-term (≤90 days)"
    elif days <= 180:
        return "Medium-term (91-180 days)"
    else:
        return "Long-term (>=181 days)"

def analyze_certificate_validity(csv_filename, output_csv):
    df = pd.read_csv(csv_filename)

    # Convert 'not_before' and 'not_after' to datetime
    df['not_before'] = pd.to_datetime(df['not_before'], errors='coerce')
    df['not_after'] = pd.to_datetime(df['not_after'], errors='coerce')

    # Drop rows where conversion failed (NaT values)
    df = df.dropna(subset=['not_before', 'not_after'])    

    df = df.drop_duplicates(subset='domain', keep='first')
    df = df.dropna(subset=['issuer'])

    df['country'] = df['issuer'].apply(extract_country)
    df = df.dropna(subset=['country'])

    # Calculate validity period in days
    df['validity_days'] = (df['not_after'] - df['not_before']).dt.days

    # Categorize into short, medium, or long term
    df['validity_category'] = df['validity_days'].apply(categorize_validity_days)

    # Count certificates per category
    result = df['validity_category'].value_counts().reset_index()
    result.columns = ['validity_category', 'count']

    # Save results to CSV
    result.to_csv(output_csv, index=False)

def extract_organization(issuer):
    """Extracts the organization (O=xxx) from the issuer field."""
    fields = issuer.split(',')
    for field in fields:
        field = field.strip()
        if field.startswith("O="):  # Look for 'O=' field
            return field[2:]  # Remove 'O=' prefix
    return None  # Return None if no organization is found

def get_top_certificate_authorities(csv_filename, output_csv):
    # Load the CSV data
    df = pd.read_csv(csv_filename)

    # Drop duplicate domains to ensure unique certificate entries
    df = df.drop_duplicates(subset='domain', keep='first')
    df = df.dropna(subset=['issuer'])

    # Extract the organization (O=xxx) from the issuer field
    df['certificate_authority'] = df['issuer'].apply(extract_organization)
    df = df.dropna(subset=['certificate_authority'])  # Remove rows where O= is missing

    # Count certificates issued per CA
    top_cas = df['certificate_authority'].value_counts().reset_index()
    top_cas.columns = ['certificate_authority', 'certificate_count']

    # Keep only the top 5 CAs
    top_cas = top_cas.head(5)

    # Save results to CSV
    top_cas.to_csv(output_csv, index=False)

    # Display results
    print(top_cas)

def get_top_countries(csv_filename, output_csv):
    # Load the CSV data
    df = pd.read_csv(csv_filename)

    df = df.drop_duplicates(subset='domain', keep='first')
    df = df.dropna(subset=['issuer'])

    df['country'] = df['issuer'].apply(extract_country)
    df = df.dropna(subset=['country'])

    # Extract suffix and filter only BRICS domains
    df['suffix'] = df['domain'].apply(lambda x: next((s for s in constants.eu_suffixes if x.endswith(s)), None))
    df = df[df['suffix'].notnull()]

    # Filter only BRICS domains
    df = df[df['suffix'].isin(constants.eu_suffixes)]

    # Count certificates issued per country
    top_issuers = df['country'].value_counts().reset_index()
    top_issuers.columns = ['country', 'certificate_count']

    # Display the top 10 issuers
    print(top_issuers.head(10))

    # Save results to CSV
    top_issuers.to_csv(output_csv, index=False)

def process_certificates(eu_csv, brics_csv, output_csv="certificates_by_validity.csv"):
    # Load both CSV files into a single DataFrame
    df_eu = pd.read_csv(eu_csv)
    df_eu = df_eu.drop_duplicates(subset='domain', keep='first')

    df_brics = pd.read_csv(brics_csv)
    df_brics = df_brics.drop_duplicates(subset='domain', keep='first')

    # Merge datasets and add a group identifier
    df_eu["group"] = "EU"
    df_brics["group"] = "BRICS"
    df = pd.concat([df_eu, df_brics], ignore_index=True)

    # Convert 'not_before' and 'not_after' to datetime
    df['not_before'] = pd.to_datetime(df['not_before'], errors='coerce')
    df['not_after'] = pd.to_datetime(df['not_after'], errors='coerce')

    # Drop rows where conversion failed (NaT values)
    df = df.dropna(subset=['not_before', 'not_after'])    

    # Calculate certificate validity duration in days
    df['validity_days'] = (df['not_after'] - df['not_before']).dt.days

    # Categorize certificates into short, medium, or long term
    df['validity_category'] = df['validity_days'].apply(categorize_validity_days)

    # Extract the Certificate Authority (O=xxx)
    df['certificate_authority'] = df['issuer'].apply(extract_organization)

    # Drop rows where CA extraction failed
    df = df.dropna(subset=['certificate_authority'])

    # Count the number of certificates per CA and validity category
    result = df.groupby(['validity_category', 'certificate_authority']).size().reset_index(name='certificate_count')

    # Save results to CSV
    result.to_csv(output_csv, index=False)

    print(f"Processed data saved to {output_csv}")

def main():
    process_certificates('./csv/eu_certificates.csv', './csv/brics_certificates.csv')

if __name__ == '__main__':
    main()