from waitress import serve
from korucu_erp.wsgi import application
import os
from dotenv import load_dotenv

# Load env in case this script is run directly (though wsgi/settings should handle it)
load_dotenv()

port = os.getenv('PORT', '8000')

print(f"Starting Production Server on port {port}...")
print("Press Ctrl+C to stop.")

serve(application, host='0.0.0.0', port=port)
