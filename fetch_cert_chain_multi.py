import csv
import socket
import time
import select
import ssl
from OpenSSL import SSL, crypto
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

# List to store failed domains
errored_domains = []

def fetch_ssl_certificate_chain(hostname, port=443, timeout=60, max_retries=3):
    for attempt in range(max_retries):
        try:
            # Ensure hostname does not contain scheme (https://)
            parsed_url = urlparse(hostname)
            if parsed_url.scheme:
                hostname = parsed_url.netloc
            
            # Create an SSL context with modern TLS support
            context = SSL.Context(SSL.TLS_METHOD)
            context.set_verify(SSL.VERIFY_NONE, lambda *x: True)
            
            # Create and connect socket
            sock = socket.create_connection((hostname, port), timeout=timeout)
            ssl_conn = SSL.Connection(context, sock)
            ssl_conn.set_connect_state()
            ssl_conn.set_tlsext_host_name(hostname.encode())
            
            end_time = time.time() + timeout
            while True:
                try:
                    ssl_conn.do_handshake()
                    break
                except (SSL.WantReadError, SSL.WantWriteError):
                    if time.time() > end_time:
                        raise TimeoutError("SSL handshake timed out")
                    select.select([ssl_conn], [ssl_conn], [], end_time - time.time())
                except SSL.Error as e:
                    if "tlsv1 alert protocol version" in str(e).lower():
                        print(f"[Attempt {attempt+1}] TLS version mismatch for {hostname}, trying TLSv1.2")
                        context = SSL.Context(SSL.TLSv1_2_METHOD)
                        continue
                    else:
                        raise e
            
            # Retrieve certificate chain
            cert_chain = ssl_conn.get_peer_cert_chain()
            cert_details = []
            for cert in cert_chain:
                pem_cert = crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode()
                parsed_cert = x509.load_pem_x509_certificate(pem_cert.encode(), default_backend())
                cert_details.append(extract_certificate_details(parsed_cert))
            
            # Close connection
            ssl_conn.shutdown()
            ssl_conn.close()
            sock.close()
            
            return cert_details
        
        except (socket.timeout, TimeoutError):
            print(f"[Attempt {attempt+1}] Timeout fetching certificate for {hostname}")
        except socket.gaierror:
            print(f"[Attempt {attempt+1}] Invalid hostname: {hostname} (Check if scheme is included)")
            break  # No need to retry
        except ConnectionRefusedError:
            print(f"[Attempt {attempt+1}] Connection refused for {hostname}")
            break  # No need to retry
        except SSL.Error as e:
            print(f"[Attempt {attempt+1}] SSL error for {hostname}: {e}")
        except Exception as e:
            print(f"[Attempt {attempt+1}] Unexpected error for {hostname}: {e}")
    
    # If all attempts failed, store the domain in errored_domains
    errored_domains.append(hostname)
    return []

def extract_certificate_details(cert):
    return {
        "subject": cert.subject.rfc4514_string(),
        "issuer": cert.issuer.rfc4514_string(),
        "serial_number": cert.serial_number,
        "not_before": cert.not_valid_before,
        "not_after": cert.not_valid_after,
    }

def write_cert_chain_to_csv(domain, cert_chain, filename):
    fieldnames = ["domain", "subject", "issuer", "serial_number", "not_before", "not_after"]
    with open(filename, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if file.tell() == 0:
            writer.writeheader()
        for cert in cert_chain:
            row = {"domain": domain}
            row.update(cert)
            writer.writerow(row)

def process_domain(domain, output_file):
    cert_chain = fetch_ssl_certificate_chain(domain)
    if cert_chain:
        write_cert_chain_to_csv(domain, cert_chain, output_file)

def process_domains_from_csv(input_file, output_file, error_log_file):
    with open(input_file, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        with ThreadPoolExecutor(max_workers=200) as executor:
            futures = {executor.submit(process_domain, row[0], output_file): row[0] for row in reader}
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    errored_domains.append(futures[future])
    
    # Log errored domains
    if errored_domains:
        with open(error_csv_file, 'w', newline='') as errfile:
            writer = csv.writer(errfile)
            writer.writerow(["Failed Domains"])
            for domain in errored_domains:
                writer.writerow([domain])

if __name__ == "__main__":
    input_csv_file = './csv/eu.csv'  # Replace with your input CSV file path
    output_csv_file = './csv/eu_certificates.csv'  # Replace with your output CSV file path
    error_csv_file = './csv/eu_failed_domains.csv'  # File to store failed domains
    process_domains_from_csv(input_csv_file, output_csv_file, error_csv_file)
