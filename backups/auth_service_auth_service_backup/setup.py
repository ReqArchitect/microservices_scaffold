from setuptools import setup, find_packages

setup(
    name="auth_service",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "Flask==2.3.3",
        "Flask-SQLAlchemy==3.1.1",
        "Flask-Migrate==4.0.5",
        "psycopg==3.1.12",
        "python-dotenv==1.0.0",
        "pytest==7.4.2",
        "pytest-cov==4.1.0",
        "responses==0.23.3",
        "requests==2.31.0",
        "flasgger==0.9.7",
        "prometheus-client==0.17.1",
        "redis==5.0.1",
        "Flask-Caching==2.0.2",
        "Flask-Limiter==3.5.0"
    ],
    python_requires=">=3.8",
) 