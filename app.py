from app import create_app, db
from app.models.property import Property
from app.models.agent import Agent
from app.models.user import User
from app.models.economic_data import EconomicData
import sys

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Register shell context for flask shell command."""
    return {
        'db': db,
        'Property': Property,
        'Agent': Agent,
        'User': User,
        'EconomicData': EconomicData
    }

if __name__ == '__main__':
    # Default port
    port = 5007
    
    # Check for command line port argument
    if len(sys.argv) > 1:
        if '--port' in sys.argv:
            port_index = sys.argv.index('--port')
            if port_index + 1 < len(sys.argv):
                try:
                    port = int(sys.argv[port_index + 1])
                except ValueError:
                    print("Invalid port number, using default 5007")
                    port = 5007
    
    print(f"Starting server on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port)
