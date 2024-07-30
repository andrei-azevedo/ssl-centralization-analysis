import csv

# Define the set of suffixes
suffixes = {'.br', '.ru', '.in', '.za', '.cn'}

# Function to check if the string ends with any of the specified suffixes
def ends_with_suffix(string, suffixes):
    return any(string.endswith(suffix) for suffix in suffixes)

# Read and filter the CSV file
def filter_csv(input_file, output_file):
    with open(input_file, mode='r', newline='', encoding='utf-8') as infile, \
         open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        # Write header to output file if there is one
        header = next(reader, None)
        if header:
            writer.writerow(header)
        
        # Filter rows based on the first field
        for row in reader:
            if ends_with_suffix(row[0], suffixes):
                writer.writerow(row)

# Specify input and output CSV file paths
input_csv_file = '202406.csv'
output_csv_file = 'filtered_output.csv'

# Filter the CSV file
filter_csv(input_csv_file, output_csv_file)

print(f'Filtered data has been written to {output_csv_file}')