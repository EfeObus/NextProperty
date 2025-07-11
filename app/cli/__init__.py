"""
CLI module for NextProperty AI.
Contains command-line interfaces for various operations.
"""

def register_cli_commands(app):
    """Register all CLI commands with the Flask app."""
    from app.cli.etl_commands import register_etl_commands
    from app.cli.rate_limit_commands import register_rate_limit_commands
    
    # Register ETL commands
    register_etl_commands(app)
    
    # Register rate limiting commands
    register_rate_limit_commands(app)
