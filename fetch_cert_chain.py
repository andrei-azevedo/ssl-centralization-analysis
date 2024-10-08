import csv
import socket
import select
from OpenSSL import SSL, crypto
from cryptography import x509
import time
from cryptography.hazmat.backends import default_backend

def fetch_ssl_certificate_chain(hostname, port=443, timeout=10):
    try:
        # Create a new SSL context
        context = SSL.Context(SSL.TLSv1_2_METHOD)
        context.set_verify(SSL.VERIFY_NONE, lambda *x: True)
        
        # Create a socket and wrap it in an SSL connection
        sock = socket.create_connection((hostname, port), timeout=timeout)
        ssl_conn = SSL.Connection(context, sock)
        ssl_conn.set_connect_state()
        ssl_conn.set_tlsext_host_name(hostname.encode())
        
        end_time = time.time() + timeout
        while True:
            try:
                ssl_conn.do_handshake()
                break
            except SSL.WantReadError:
                if time.time() > end_time:
                    raise TimeoutError("SSL handshake timed out")
                select.select([ssl_conn], [], [], end_time - time.time())
            except SSL.WantWriteError:
                if time.time() > end_time:
                    raise TimeoutError("SSL handshake timed out")
                select.select([], [ssl_conn], [], end_time - time.time())
        
        # Retrieve the entire certificate chain
        cert_chain = ssl_conn.get_peer_cert_chain()
        
        cert_details = []
        for cert in cert_chain:
            pem_cert = crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode()
            parsed_cert = x509.load_pem_x509_certificate(pem_cert.encode(), default_backend())
            cert_details.append(extract_certificate_details(parsed_cert))

        # Close the connection
        ssl_conn.shutdown()
        ssl_conn.close()
        sock.close()

        return cert_details

    except Exception as e:
        print(f"An error occurred for hostname {hostname}: {e}")
        return []

def extract_certificate_details(cert):
    details = {
        "subject": cert.subject.rfc4514_string(),
        "issuer": cert.issuer.rfc4514_string(),
        "version": cert.version.name,
        "serial_number": cert.serial_number,
        "not_before": cert.not_valid_before,
        "not_after": cert.not_valid_after,
    }
    return details

def write_cert_chain_to_csv(domain, cert_chain, filename):
    fieldnames = ["domain", "subject", "issuer", "version", "serial_number", "not_before", "not_after"]
    
    with open(filename, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        # Write header only if file is empty
        if file.tell() == 0:
            writer.writeheader()
        
        for cert in cert_chain:
            row = {"domain": domain}
            row.update(cert)
            writer.writerow(row)

def process_domains_from_csv(input_file, output_file):
    with open(input_file, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        
        for row in reader:
            domain = row[0]
            cert_chain = fetch_ssl_certificate_chain(domain)
            if cert_chain:
                write_cert_chain_to_csv(domain, cert_chain, output_file)

def main():
    process_domains_from_csv('./csv/brics.csv', './csv/brics_certificates.csv')

if __name__ == '__main__':
    main()