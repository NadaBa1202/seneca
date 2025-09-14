from setuptools import setup, find_packages

setup(
    name="esports_analytics",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'streamlit>=1.31.0',
        'pandas>=2.2.0',
        'plotly>=5.18.0',
        'vaderSentiment>=3.3.2',
        'detoxify>=0.5.1',
        'sentence-transformers>=2.2.2',
        'numpy>=1.24.3',
        'pillow>=10.2.0',
        'opencv-python>=4.9.0',
        'scikit-learn>=1.3.0',
        'python-dotenv>=1.0.0'
    ],
    extras_require={
        'dev': [
            'pytest>=8.4.0',
            'pytest-cov>=7.0.0',
            'pytest-asyncio>=1.2.0',
            'pytest-mock>=3.15.0'
        ],
    }
)
