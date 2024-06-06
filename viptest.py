#!/usr/bin/env python3

import csv
import sys
import argparse
import httpx
import validators
from urllib.parse import urlparse
import ssl
import socket
import subprocess
import multiprocessing
from itertools import islice
import ipaddress
from datetime import datetime

# Editable variables

# USE_HTTP2: A boolean flag to enable or disable HTTP/2 for HTTPS requests.
# True: Use HTTP/2 for HTTPS requests. Fall back to HTTP/1.1 if client cannot negotiate HTTP/2.
# False: Use HTTP/1.1 for HTTPS requests.
USE_HTTP2 = True

# IGNORE_CERTIFICATE_WARNINGS: A boolean flag to ignore SSL certificate warnings.
# True: SSL certificate warnings will be ignored. Like bypassing a browser's invalid TLS certificate warning.
# False: SSL certificate warnings will not be ignored, and SSL verification will be enforced.
IGNORE_CERTIFICATE_WARNINGS = True

# MAX_CONCURRENCY: An integer specifying the maximum number of concurrent processes.
# This defines the upper limit on how many URLs can be processed in parallel.
MAX_CONCURRENCY = 50

# NAME_RESOLUTION_OVERRIDE: A boolean flag to decide whether to use the IP address provided in the CSV file
# to override the system DNS resolution.
# True: Use the IP address provided in the CSV file.
# False: Ignore the IP address in the CSV file and use system DNS resolution.
NAME_RESOLUTION_OVERRIDE = True

def is_valid_fqdn(fqdn):
    """
    Check if the given FQDN (Fully Qualified Domain Name) is valid.

    Parameters:
        fqdn (str): The fully qualified domain name to validate.

    Returns:
        bool: True if the FQDN is valid, False otherwise.
    """
    labels = fqdn.split('.')
    if len(fqdn) > 253:
        return False
    for label in labels:
        if len(label) < 1 or len(label) > 63:
            return False
        if not (label[0].isalnum() and label[-1].isalnum()):
            return False
        for char in label:
            if not (char.isalnum() or char == '-'):
                return False
    return True

def validate_url(url):
    """
    Validate the given URL. It checks the scheme, hostname, and path of the URL.

    Parameters:
        url (str): The URL to validate.

    Returns:
        tuple: (bool, str) indicating whether the URL is valid and an associated message.
    """
    try:
        url = url.strip()
        result = urlparse(url)
        scheme = result.scheme
        if scheme not in ['http', 'https', '']:
            return False, f"Invalid scheme: {scheme}"

        if not result.hostname:
            return False, "Invalid hostname"

        if not is_valid_fqdn(result.hostname):
            return False, f"Invalid FQDN: {result.hostname}"

        if result.path:
            if not validators.url(url):
                return False, "Invalid URL path"

        return True, "Valid URL"
    except Exception as e:
        return False, str(e)

def validate_ip(ip):
    """
    Validate the given IP address.

    Parameters:
        ip (str): The IP address to validate.

    Returns:
        bool: True if the IP address is valid, False otherwise.
    """
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def get_tls_info(hostname, ip, port):
    """
    Get TLS information (version and cipher) for the given hostname and IP address.

    Parameters:
        hostname (str): The hostname.
        ip (str): The IP address.
        port (int): The port number.

    Returns:
        tuple: (str, str) TLS version and cipher used.
    """
    context = ssl.create_default_context()
    if IGNORE_CERTIFICATE_WARNINGS:
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

    with socket.create_connection((ip, port), timeout=5) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            tls_version = ssock.version()
            cipher = ssock.cipher()
            return tls_version, cipher

def telnet_test(ip, port):
    """
    Perform a Telnet test to the given IP address and port.

    Parameters:
        ip (str): The IP address.
        port (int): The port number.

    Returns:
        str: The result of the Telnet test.
    """
    try:
        with socket.create_connection((ip, port), timeout=10) as sock:
            return f"Telnet {ip}:{port} - Port is open"
    except socket.error:
        return f"Telnet {ip}:{port} - Port is not open"

def ping_test(ip):
    """
    Perform a ping test to the given IP address.

    Parameters:
        ip (str): The IP address.

    Returns:
        bool: True if the host is reachable, False otherwise.
    """
    try:
        # Use system ping command
        output = subprocess.run(["ping", "-c", "1", ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if output.returncode == 0:
            return True
        else:
            return False
    except Exception as e:
        return False

def process_urls(urls, output_queue, counter):
    """
    Process a list of URLs.

    Parameters:
        urls (list): List of URLs and optional IP addresses to process.
        output_queue (multiprocessing.Queue): Queue to hold the output messages.
        counter (multiprocessing.Value): Counter to keep track of the number of processed URLs.
    """
    for entry in urls:
        if len(entry) == 0 or len(entry[0].strip()) == 0:
            output_queue.put(f"Error: Empty or invalid entry {entry}")
            continue

        url = entry[0].strip()
        ip = entry[1].strip() if len(entry) > 1 and entry[1].strip() else None

        if ip and not validate_ip(ip):
            output_queue.put(f"[{url}] Error: Invalid IP address {ip}")
            continue

        # Split entry on ':'
        parts = url.split(':')
        if len(parts) == 2 and parts[1].isdigit():
            hostname = parts[0]
            port = int(parts[1])

            # Validate hostname separately
            if not is_valid_fqdn(hostname):
                output_queue.put(f"[{url}] Error: Invalid hostname")
                continue

            resolved_ip = ip if ip and NAME_RESOLUTION_OVERRIDE else None
            if not resolved_ip:
                try:
                    resolved_ip = socket.gethostbyname(hostname)
                except socket.gaierror:
                    output_queue.put(f"[{url}] Error: Could not resolve hostname {hostname}")
                    continue

            # Accumulate results
            results = [f"[{url}]"]

            # Ping test
            ping_result = f"Ping {resolved_ip} - Host is reachable" if ping_test(resolved_ip) else f"Ping {resolved_ip} - Host is not reachable"
            results.append(ping_result)

            # Telnet test
            telnet_result = telnet_test(resolved_ip, port)
            results.append(telnet_result)

            output_queue.put(" - ".join(results))

        else:
            # Treat as a full URL
            is_valid, message = validate_url(url)

            if not is_valid:
                output_queue.put(f"[{url}] Error: {message}")
                continue

            try:
                parsed_url = urlparse(url)
                scheme = parsed_url.scheme
                port = parsed_url.port if parsed_url.port else (443 if scheme == 'https' else 80)
                hostname = parsed_url.hostname

                resolved_ip = ip if ip and NAME_RESOLUTION_OVERRIDE else None
                if not resolved_ip:
                    try:
                        resolved_ip = socket.gethostbyname(hostname)
                    except socket.gaierror:
                        output_queue.put(f"[{url}] Error: Could not resolve hostname {hostname}")
                        continue

                if scheme == 'http':
                    try:
                        response = httpx.get(url, timeout=10)
                        output_queue.put(f"[{url}] HTTP GET {url} - Resolved IP: {resolved_ip} - Response Code: {response.status_code}")
                    except httpx.RequestError as e:
                        output_queue.put(f"[{url}] Error processing {url}: {e}")
                elif scheme == 'https':
                    try:
                        tls_version, cipher = get_tls_info(hostname, resolved_ip, port)
                        with httpx.Client(http2=USE_HTTP2, verify=not IGNORE_CERTIFICATE_WARNINGS, timeout=10) as client:
                            response = client.get(url)
                            output_queue.put(f"[{url}] HTTPS GET {url} - Resolved IP: {resolved_ip} - TLS Version: {tls_version}, Cipher: {cipher}, Response Code: {response.status_code}")
                    except Exception as e:
                        output_queue.put(f"[{url}] Error processing {url}: {e}")
            except Exception as e:
                output_queue.put(f"[{url}] Error processing {url}: {e}")

        # Increment the counter
        counter.value += 1

def chunked_iterable(iterable, size):
    """
    Yield successive chunks from iterable of a specific size.

    Parameters:
        iterable (iterable): The iterable to chunk.
        size (int): The size of each chunk.

    Yields:
        list: Chunks of the original iterable.
    """
    it = iter(iterable)
    while True:
        chunk = list(islice(it, size))
        if not chunk:
            break
        yield chunk

def main():
    """
    Main function to test URLs from a CSV file.
    """
    global USE_HTTP2, IGNORE_CERTIFICATE_WARNINGS, NAME_RESOLUTION_OVERRIDE

    parser = argparse.ArgumentParser(description='Test URLs from a CSV file.')
    parser.add_argument('--csv', type=str, required=True, help='CSV file with URLs')
    parser.add_argument('-c', '--concurrent', type=int, help='Number of concurrent processes')
    args = parser.parse_args()

    if args.concurrent and args.concurrent > MAX_CONCURRENCY:
        print(f"Error: Maximum concurrency of {MAX_CONCURRENCY} exceeded.", file=sys.stderr)
        sys.exit(1)

    with open(args.csv, newline='') as csvfile:
        reader = csv.reader(csvfile)
        urls = [row for row in reader]

    output_queue = multiprocessing.Queue()
    counter = multiprocessing.Value('i', 0)

    if args.concurrent:
        chunk_size = len(urls) // args.concurrent
        chunks = list(chunked_iterable(urls, chunk_size))
        processes = []
        for chunk in chunks:
            p = multiprocessing.Process(target=process_urls, args=(chunk, output_queue, counter))
            processes.append(p)
            p.start()

        while any(p.is_alive() for p in processes) or not output_queue.empty():
            while not output_queue.empty():
                print(output_queue.get())
                sys.stdout.flush()

        for p in processes:
            p.join()
    else:
        process_urls(urls, output_queue, counter)

    while not output_queue.empty():
        print(output_queue.get())
        sys.stdout.flush()

    # Print timestamp and number of processed URLs
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"Processed {counter.value} URLs at {timestamp}")
    sys.stdout.flush()

if __name__ == "__main__":
    main()

