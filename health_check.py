"""
Health check endpoint for the Streamlit Cloud Engineer Agent application.
This provides a simple HTTP endpoint for monitoring systems to verify application status.
"""
from flask import Flask, jsonify
import os
import sys
import importlib.util
from datetime import datetime

app = Flask(__name__)

def check_environment_variables():
    """Check if required AWS environment variables are set."""
    required_vars = ['AWS_REGION', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        return {
            'status': 'warning',
            'message': f'Missing environment variables: {", ".join(missing_vars)}'
        }
    return {
        'status': 'ok',
        'message': 'All required environment variables are set'
    }

def check_dependencies():
    """Check if critical dependencies are importable."""
    critical_modules = ['streamlit', 'boto3', 'strands_agents']
    
    failed_imports = []
    for module_name in critical_modules:
        # Handle the case where the module name has a hyphen
        module_name_import = module_name.replace('-', '_')
        spec = importlib.util.find_spec(module_name_import)
        if spec is None:
            failed_imports.append(module_name)
    
    if failed_imports:
        return {
            'status': 'error',
            'message': f'Failed to find modules: {", ".join(failed_imports)}'
        }
    return {
        'status': 'ok',
        'message': 'All critical dependencies are available'
    }

def check_application_files():
    """Check if critical application files exist."""
    required_files = ['app.py', 'cloud_engineer_agent.py', 'env_validator.py']
    missing_files = [f for f in required_files if not os.path.exists(f'/app/{f}')]
    
    if missing_files:
        return {
            'status': 'error',
            'message': f'Missing application files: {", ".join(missing_files)}'
        }
    return {
        'status': 'ok',
        'message': 'All application files present'
    }

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint that returns operational status of the application.
    
    Returns:
        JSON response with status and detailed checks
        HTTP 200: Application is healthy
        HTTP 503: Application has issues (with details)
    """
    # Perform various health checks
    env_check = check_environment_variables()
    deps_check = check_dependencies()
    files_check = check_application_files()
    
    # Determine overall health status
    checks = [env_check, deps_check, files_check]
    has_error = any(check['status'] == 'error' for check in checks)
    has_warning = any(check['status'] == 'warning' for check in checks)
    
    if has_error:
        overall_status = 'unhealthy'
        http_status = 503
    elif has_warning:
        overall_status = 'degraded'
        http_status = 200
    else:
        overall_status = 'healthy'
        http_status = 200
    
    response = {
        'status': overall_status,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'application': 'cloudeng-strands-agent',
        'checks': {
            'environment': env_check,
            'dependencies': deps_check,
            'files': files_check
        }
    }
    
    return jsonify(response), http_status

@app.route('/health/live', methods=['GET'])
def liveness_check():
    """
    Liveness probe endpoint - checks if the service is running.
    This is a simple check that always returns 200 if the server is responding.
    
    Returns:
        JSON response with minimal status
        HTTP 200: Server is alive
    """
    return jsonify({
        'status': 'alive',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }), 200

@app.route('/health/ready', methods=['GET'])
def readiness_check():
    """
    Readiness probe endpoint - checks if the service is ready to accept traffic.
    This performs a subset of health checks to determine readiness.
    
    Returns:
        JSON response with readiness status
        HTTP 200: Ready to accept traffic
        HTTP 503: Not ready
    """
    # Check environment variables and dependencies for readiness
    env_check = check_environment_variables()
    deps_check = check_dependencies()
    
    checks = [env_check, deps_check]
    has_error = any(check['status'] == 'error' for check in checks)
    
    if has_error:
        status = 'not_ready'
        http_status = 503
    else:
        status = 'ready'
        http_status = 200
    
    response = {
        'status': status,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'checks': {
            'environment': env_check,
            'dependencies': deps_check
        }
    }
    
    return jsonify(response), http_status

if __name__ == '__main__':
    # Run the health check server on port 8080
    # Use 0.0.0.0 to accept connections from outside the container
    port = int(os.environ.get('HEALTH_CHECK_PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
