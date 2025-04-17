import socket
import ssl
import urllib.request
import urllib.error
from urllib.parse import urlparse
import dns.resolver

class WebsiteChecker:
    def __init__(self, config):
        self.config = config
        self.user_agent = config.get('user_agent')
    
    def check_website(self, website):
        """Check website with combined SSL and HTTP checks to reduce requests"""
        # First ensure you have the proper import at the top of checker.py
        # from urllib.parse import urlparse
        
        url = website['url']
        check_string = website.get('check_string', '')
        
        # Parse the URL to get components
        parsed_url = None
        try:
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
        except ImportError:
            # Fallback if urlparse import fails
            hostname = url.split('//')[1].split('/')[0] if '//' in url else url.split('/')[0]
        else:
            hostname = parsed_url.netloc
        
        status = 'OK'
        status_code = '200'
        response_content = None
        
        # Check DNS if enabled
        if self.config.get('check_dns'):
            dns_status = self.check_dns(hostname)
            if dns_status != 'OK':
                return 'DNS', dns_status
        
        # Combined SSL and HTTP check
        if self.config.get('check_http'):
            http_status, response_code, response_content = self.check_http(url)
            
            # If HTTPS URL and SSL check is enabled, interpret SSL errors properly
            is_https = url.startswith('https://')
            if is_https and self.config.get('check_ssl'):
                if http_status.startswith('SSL') or ('SSL' in response_code):
                    return 'SSL', response_code
            
            if http_status != 'OK':
                return 'HTTP', response_code
            
            status_code = response_code
        elif self.config.get('check_ssl') and url.startswith('https://'):
            # If only SSL check is enabled (not HTTP)
            ssl_status = self.check_ssl(hostname)
            if ssl_status != 'OK':
                return 'SSL', ssl_status
        
        # Check for the expected string if needed
        if self.config.get('check_string') and check_string and response_content:
            if check_string not in response_content:
                return 'String', 'Not Found'
        
        return status, status_code
    
    def check_dns(self, hostname):
        try:
            # Clear DNS cache by using a resolver with no cache
            resolver = dns.resolver.Resolver()
            resolver.cache = None
            
            resolver.resolve(hostname)
            return 'OK'
        except dns.resolver.NXDOMAIN:
            return 'Not Found'
        except dns.resolver.NoAnswer:
            return 'No Answer'
        except dns.resolver.Timeout:
            return 'Timeout'
        except Exception as e:
            return str(e)
    
    def check_ssl(self, hostname):
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443)) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    if cert:
                        return 'OK'
                    return 'Invalid Certificate'
        except ssl.SSLCertVerificationError:
            return 'Certificate Verification Error'
        except ssl.SSLError as e:
            return str(e)
        except socket.gaierror:
            return 'DNS Lookup Failed'
        except socket.timeout:
            return 'Connection Timeout'
        except ConnectionRefusedError:
            return 'Connection Refused'
        except Exception as e:
            return str(e)
    
    def check_http(self, url):
        try:
            headers = {'User-Agent': self.user_agent}
            req = urllib.request.Request(url, headers=headers)
            response = urllib.request.urlopen(req, timeout=10)
            status_code = str(response.status)
            content = response.read().decode('utf-8', errors='ignore')
            
            return 'OK', status_code, content
        except urllib.error.HTTPError as e:
            return 'HTTP Error', str(e.code), None
        except urllib.error.URLError as e:
            # Check if it's an SSL error
            if isinstance(e.reason, ssl.SSLError):
                return 'SSL Error', str(e.reason), None
            elif isinstance(e.reason, ssl.CertificateError):
                return 'SSL Certificate Error', str(e.reason), None
            else:
                return 'URL Error', str(e.reason), None
        except ssl.SSLError as e:
            return 'SSL Error', str(e), None
        except ssl.CertificateError as e:
            return 'SSL Certificate Error', str(e), None
        except socket.timeout:
            return 'Timeout', 'Connection Timeout', None
        except Exception as e:
            return 'Error', str(e), None