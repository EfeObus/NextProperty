"""
CLI module for NextProperty AI.
Contains command-line interfaces for various operations.
"""

def register_cli_commands(app):
    """Register all CLI commands with the Flask app."""
    from app.cli.etl_commands import register_etl_commands
    from app.cli.rate_limit_commands import register_rate_limit_commands
    from app.cli.abuse_detection_commands import register_abuse_detection_commands
    from app.cli.pattern_analysis_commands import register_pattern_analysis_commands
    from app.cli.predictive_limiting_commands import register_predictive_limiting_commands
    from app.cli.geographic_limiting_commands import register_geographic_limiting_commands
    from app.cli.api_key_commands import api_key_commands
    
    # Register ETL commands
    register_etl_commands(app)
    
    # Register rate limiting commands
    register_rate_limit_commands(app)
    
    # Register abuse detection commands
    register_abuse_detection_commands(app)
    
    # Register pattern analysis commands
    register_pattern_analysis_commands(app)
    
    # Register predictive limiting commands
    register_predictive_limiting_commands(app)
    
    # Register geographic limiting commands
    register_geographic_limiting_commands(app)
    
    # Register API key commands
    app.cli.add_command(api_key_commands)
