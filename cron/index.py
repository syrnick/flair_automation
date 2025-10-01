from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import os
import sys

# Add parent directory to path to import flair_controller
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flair_controller import FlairController

def runCron():
    """Execute the cron job and return status."""
    try:
        controller = FlairController()
        results = controller.apply_schedule()

        if not results:
            return {"status": "no_action", "message": "No schedule applied (no active segment or schedule not configured)"}

        success_count = sum(1 for r in results.values() if r['success'])
        total_count = len(results)

        return {
            "status": "success" if success_count == total_count else "partial_success",
            "message": f"Schedule applied: {success_count}/{total_count} rooms processed successfully",
            "results": results
        }
    except Exception as e:
        return {"status": "error", "message": f"Error executing cron: {str(e)}"}

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