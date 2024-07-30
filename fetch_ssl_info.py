import csv
import ssl
import socket
from datetime import datetime

def get_ssl_certificate(domain):
    context = ssl.create_default_context()
    conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=domain)
    conn.settimeout(5.0)
    
    try:
        conn.connect((domain, 443))
        ssl_info = conn.getpeercert()
    except Exception as e:
        print(f"Error fetching SSL certificate for {domain}: {e}")
        return None
    finally:
        conn.close()
    
    return ssl_info

def parse_ssl_certificate(cert):
    if cert is None:
        return None
    
    domain = cert['subject'][0][0][1]
    issuer = cert['issuer'][0][0][1]
    not_before = datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
    
    return {
        'domain': domain,
        'issuer': issuer,
        'issue_date': not_before,
        'expiration_date': not_after
    }

def write_to_csv(data, output_file):
    fieldnames = ['domain', 'issuer', 'issue_date', 'expiration_date']
    
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def read_crux_data(csv_file):
    domains = []
    
    with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        
        # Read the header if present
        header = next(reader, None)
        
        for row in reader:
            field = row[0]
            if field.startswith('https://'):
                field = field[len('https://'):]
            domains.append(field)
    
    return domains

def main(domains, output_file):
    ssl_data = []
    
    for domain in domains:
        cert = get_ssl_certificate(domain)
        parsed_cert = parse_ssl_certificate(cert)
        if parsed_cert:
            ssl_data.append(parsed_cert)
    write_to_csv(ssl_data, output_file)
    print(f"SSL certificate data has been written to {output_file}")

if __name__ == '__main__':
    # List of domains to fetch SSL information for
    domains = read_crux_data('brics.csv')
    output_csv_file = 'ssl_certificates.csv'
    
    main(domains, output_csv_file)