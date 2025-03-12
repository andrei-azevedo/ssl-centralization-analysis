import pandas as pd

# Load the first CSV file (brics_certificates.csv)
certificates_df = pd.read_csv('csv/eu_certificates.csv')

# Load the second CSV file (brics.csv), specifying that it doesn't have a header
brics_df = pd.read_csv('csv/eu.csv', header=None, names=['domain', 'order'])

# Get the unique domains from both dataframes
unique_cert_domains = certificates_df['domain'].unique()
unique_brics_domains = brics_df['domain'].unique()

# Find the missing domains by comparing the two sets
missing_domains = set(unique_brics_domains) - set(unique_cert_domains)

# Calculate total unique domains in brics.csv, number of missing domains, and percentage
total_domains = len(unique_brics_domains)
missing_count = len(missing_domains)
missing_percentage = (missing_count / total_domains) * 100

# Print the results
print(f"Total unique domains in brics.csv: {total_domains}")
print(f"Number of missing domains: {missing_count}")
print(f"Percentage of missing domains: {missing_percentage:.2f}%")
