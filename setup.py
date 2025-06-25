from setuptools import setup, find_packages

setup(
    name="ctp-horarios",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.24.0",
        "pandas>=1.5.0",
        "reportlab>=4.0.0",
        "streamlit-tags>=0.1.0",
        "extra-streamlit-components>=0.1.0",
        "xlsxwriter>=3.0.0",
        "plotly>=5.0.0",
        "streamlit-authenticator>=0.2.0",
        "openpyxl>=3.0.0",
    ],
)
