from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import os

def runCron():
    """Execute the cron job and return status."""
    # TODO: Implement cron logic
    return {"status": "success", "message": "Cron executed successfully"}

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        # Parse query parameters
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        # Get QSECRET from query parameter and environment
        qsecret_param = query_params.get('QSECRET', [None])[0]
        qsecret_env = os.environ.get('QSECRET')

        self.send_response(200)
        self.send_header('Content-type','text/plain')
        self.end_headers()

        # Check if secrets match
        if qsecret_param and qsecret_env and qsecret_param == qsecret_env:
            # Secrets match - run cron
            status = runCron()
            response = f"Status: {status}"
            self.wfile.write(response.encode('utf-8'))
        else:
            # Secrets don't match - return default response
            self.wfile.write('Hello, world!'.encode('utf-8'))

        return