import pandas as pd

# List of BRICS country codes
brics_countries = ['BR', 'RU', 'IN', 'CN', 'ZA']

# Function to extract counts for BRICS countries
def get_brics_count(country_count):
    brics_count = country_count[country_count.index.isin(brics_countries)]
    total_brics_count = brics_count.sum()
    return brics_count, total_brics_count

# List of EU country codes
eu_countries = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR', 
                'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'RO', 
                'SK', 'SI', 'ES', 'SE']

# Function to extract counts for EU countries
def get_eu_count(country_count):
    eu_count = country_count[country_count.index.isin(eu_countries)]
    total_eu_count = eu_count.sum()
    return eu_count, total_eu_count


# Load the CSV file without header
df = pd.read_csv('csv/world.csv', header=None, names=['domain', 'rank'])

# List of valid country-code top-level domains (ccTLDs)
valid_cctlds = ['ac', 'ad', 'ae', 'af', 'ag', 'ai', 'al', 'am', 'ao', 'aq', 'ar', 'as', 'at', 'au', 'aw', 'ax', 'az', 
                'ba', 'bb', 'bd', 'be', 'bf', 'bg', 'bh', 'bi', 'bj', 'bm', 'bn', 'bo', 'bq', 'br', 'bs', 'bt', 'bv', 'bw', 'by', 'bz',
                'ca', 'cc', 'cd', 'cf', 'cg', 'ch', 'ci', 'ck', 'cl', 'cm', 'cn', 'co', 'cr', 'cu', 'cv', 'cw', 'cx', 'cy', 'cz', 
                'de', 'dj', 'dk', 'dm', 'do', 'dz', 'ec', 'ee', 'eg', 'eh', 'er', 'es', 'et', 'eu', 'fi', 'fj', 'fk', 'fm', 'fo', 'fr', 
                'ga', 'gb', 'gd', 'ge', 'gf', 'gg', 'gh', 'gi', 'gl', 'gm', 'gn', 'gp', 'gq', 'gr', 'gs', 'gt', 'gu', 'gw', 'gy', 
                'hk', 'hm', 'hn', 'hr', 'ht', 'hu', 'id', 'ie', 'il', 'im', 'in', 'io', 'iq', 'ir', 'is', 'it', 'je', 'jm', 'jo', 
                'jp', 'ke', 'kg', 'kh', 'ki', 'km', 'kn', 'kp', 'kr', 'kw', 'ky', 'kz', 'la', 'lb', 'lc', 'li', 'lk', 'lr', 'ls', 
                'lt', 'lu', 'lv', 'ly', 'ma', 'mc', 'md', 'me', 'mf', 'mg', 'mh', 'mk', 'ml', 'mm', 'mn', 'mo', 'mp', 'mq', 'mr', 
                'ms', 'mt', 'mu', 'mv', 'mw', 'mx', 'my', 'mz', 'na', 'nc', 'ne', 'nf', 'ng', 'ni', 'nl', 'no', 'np', 'nr', 'nu', 
                'nz', 'om', 'pa', 'pe', 'pf', 'pg', 'ph', 'pk', 'pl', 'pm', 'pn', 'pr', 'ps', 'pt', 'pw', 'py', 'qa', 're', 'ro', 
                'rs', 'ru', 'rw', 'sa', 'sb', 'sc', 'sd', 'se', 'sg', 'sh', 'si', 'sj', 'sk', 'sl', 'sm', 'sn', 'so', 'sr', 'ss', 
                'st', 'sv', 'sx', 'sy', 'sz', 'tc', 'td', 'tf', 'tg', 'th', 'tj', 'tk', 'tl', 'tm', 'tn', 'to', 'tr', 'tt', 'tv', 
                'tw', 'tz', 'ua', 'ug', 'uk', 'us', 'uy', 'uz', 'va', 'vc', 've', 'vg', 'vi', 'vn', 'vu', 'wf', 'ws', 'ye', 'yt', 'za', 'zm', 'zw']

# Define a function to extract country from domain suffix
def get_country_from_suffix(domain):
    if domain.endswith('.com'):
        return 'US'
    else:
        # Extract the last part of the domain (after the last dot)
        suffix = domain.split('.')[-1]
        if suffix in valid_cctlds:
            return suffix.upper()  # Return the suffix in uppercase to represent the country code
        else:
            return None  # Return None if the suffix is not valid

# Apply the function to the 'domain' column and create a new 'country' column
df['country'] = df['domain'].apply(get_country_from_suffix)

# Filter out rows where 'country' is None (i.e., invalid TLDs)
df_valid = df.dropna(subset=['country'])

# Count the number of domains per country
country_count = df_valid['country'].value_counts()

# Count the number of domains per country
country_count = df_valid['country'].value_counts()

# Save the result to a new CSV file
country_count.to_csv('domains_per_country.csv', header=['count'], index_label='country')

# Get the counts for BRICS countries
brics_count, total_brics_count = get_brics_count(country_count)
print(f"BRICS countries domain count:\n{brics_count}")
print(f"Total BRICS domains: {total_brics_count}")

# Get the counts for EU countries
eu_count, total_eu_count = get_eu_count(country_count)
print(f"EU countries domain count:\n{eu_count}")
print(f"Total EU domains: {total_eu_count}")