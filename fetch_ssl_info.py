import socket
from OpenSSL import SSL

def get_ssl_certificate_chain(domain):
    port = 443
    # Create an SSL context with a modern TLS method
    context = SSL.Context(SSL.TLSv1_2_METHOD)
    
    # Create a socket and connect to the server
    sock = socket.create_connection((domain, port))
    connection = SSL.Connection(context, sock)
    connection.set_tlsext_host_name(domain.encode())

    try:
        connection.setblocking(1)
        connection.do_handshake()
        
        # Get the certificate chain
        cert_chain = connection.get_peer_cert_chain()
        return cert_chain

    except SSL.Error as e:
        print(f"SSL error: {e}")
        return None
    finally:
        connection.shutdown()
        sock.close()

def print_cert_details(cert):
    print(f"Subject: {cert.get_subject()}")
    print(f"Issuer: {cert.get_issuer()}")
    print(f"Serial Number: {cert.get_serial_number()}")
    print(f"Not Valid Before: {cert.get_notBefore().decode()}")
    print(f"Not Valid After: {cert.get_notAfter().decode()}")
    print("---------------------------------------------------")

if __name__ == "__main__":
    domain = 'example.com'  # Replace with your target domain
    cert_chain = get_ssl_certificate_chain(domain)
    
    if cert_chain:
        print("SSL Certificate Chain:")
        for cert in cert_chain:
            print_cert_details(cert)
    else:
        print("No certificate chain found.")
