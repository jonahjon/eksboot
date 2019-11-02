import os

# Load the development "mode". Use "developmen" if not specified
env = os.environ.get("PYTHON_ENV", "development")

# Configuration for each environment
# Alternatively use "python-dotenv"
all_environments = {
    "development": { "port": 80, "debug": True, "swagger-url": "/" },
    "production": { "port": 8080, "debug": True, "swagger-url": "/"}
}

# The config for the current environment
environment_config = all_environments['development']