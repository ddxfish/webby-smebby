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
        url = website['url']
        check_string = website.get('check_string', '')
        
        parsed_url = urlparse(url)
        hostname = parsed_url.netloc
        
        status = 'OK'
        status_code = '200'
        
        if self.config.get('check_dns'):
            dns_status = self.check_dns(hostname)
            if dns_status != 'OK':
                return 'DNS', dns_status
        
        if self.config.get('check_ssl') and parsed_url.scheme == 'https':
            ssl_status = self.check_ssl(hostname)
            if ssl_status != 'OK':
                return 'SSL', ssl_status
        
        if self.config.get('check_http'):
            http_status, response_code, response_content = self.check_http(url)
            if http_status != 'OK':
                return 'HTTP', response_code
            status_code = response_code
        
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
            return 'URL Error', str(e.reason), None
        except socket.timeout:
            return 'Timeout', 'Connection Timeout', None
        except Exception as e:
            return 'Error', str(e), None