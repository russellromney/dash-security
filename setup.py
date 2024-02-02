from setuptools import setup, find_packages


setup(
    name="dash-security",
    version="0.0.1",
    description="Building blocks for secure Dash development with Dash Pages",
    long_description="Securely develop Dash apps for cases with multiple clients and which require loading dynamic content per user/client - with Dash Pages support",
    keywords="dash security callbacks plotly access authorization authentication flask python flask-login python3 clients orgs emails",
    url="https://github.com/russellromney/dash-security",
    download_url="https://github.com/russellromney/dash-security/archive/v0.0.1.tar.gz",
    author="Russell Romney",
    author_email="russellromney@gmail.com",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "Flask-Login>=0.6.3",
        "dash>=2.14.2",
        "python-dotenv",
        "bcrypt",
        "pydantic",
        "SQLAlchemy>=2.0.25",
        "urllib3>=2.1.0"
    ],
    python_requires='>=3.9',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    include_package_data=False,
    zip_safe=False,
)
