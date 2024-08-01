import ssl
import socket
from OpenSSL import SSL, crypto
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from datetime import datetime

def fetch_ssl_certificate_chain(hostname, port=443):
    # Create a new SSL context
    context = SSL.Context(SSL.TLS_CLIENT_METHOD)
    context.set_verify(SSL.VERIFY_NONE, lambda *x: True)
    
    # Create a socket and wrap it in an SSL connection
    sock = socket.create_connection((hostname, port))
    ssl_conn = SSL.Connection(context, sock)
    ssl_conn.set_connect_state()
    ssl_conn.set_tlsext_host_name(hostname.encode())
    
    # Perform the handshake to establish the SSL connection
    ssl_conn.do_handshake()
    
    # Retrieve the entire certificate chain
    cert_chain = ssl_conn.get_peer_cert_chain()
    
    for cert in cert_chain:
        pem_cert = crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode()
        parsed_cert = x509.load_pem_x509_certificate(pem_cert.encode(), default_backend())
        print_certificate_details(parsed_cert)

    # Close the connection
    ssl_conn.shutdown()
    ssl_conn.close()
    sock.close()

def print_certificate_details(cert):
    subject = cert.subject
    issuer = cert.issuer
    version = cert.version
    serial_number = cert.serial_number
    not_before = cert.not_valid_before
    not_after = cert.not_valid_after
    
    print(f"Subject: {subject}")
    print(f"Issuer: {issuer}")
    print(f"Version: {version}")
    print(f"Serial Number: {serial_number}")
    print(f"Not Before: {not_before}")
    print(f"Not After: {not_after}")
    print("\n")

def main(domain):
    fetch_ssl_certificate_chain(domain)

if __name__ == '__main__':
    domain = 'marinha.mil.br'
    main(domain)