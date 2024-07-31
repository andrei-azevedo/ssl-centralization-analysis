import ssl
import socket

def get_cert_chain(domain):
    # Create a socket and connect to the domain
    port = 443
    context = ssl.create_default_context()
    with socket.create_connection((domain, port)) as sock:
        with context.wrap_socket(sock, server_hostname=domain) as ssock:
            # Fetch the certificate chain
            cert_chain = ssock.getpeercert()
            return ssock.getpeercert(binary_form=True)

def print_cert_details(cert):
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend

    # Load the certificate
    cert = x509.load_der_x509_certificate(cert, default_backend())
    
    # Print certificate details
    print(f"Subject: {cert.subject}")
    print(f"Issuer: {cert.issuer}")
    print(f"Serial Number: {cert.serial_number}")
    print(f"Not Valid Before: {cert.not_valid_before}")
    print(f"Not Valid After: {cert.not_valid_after}")

if __name__ == "__main__":
    domain = 'marinha.mil.br'  # Replace with your target domain
    cert_chain = get_cert_chain(domain)

    # Print root and intermediate certificate details
    print_cert_details(cert_chain)