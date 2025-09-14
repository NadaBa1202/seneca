from setuptools import setup, find_packages

setup(
    name="esports_analytics",
    version="0.1",
    packages=find_packages(include=['esports_analytics', 'esports_analytics.*']),
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
        'python-dotenv>=1.0.0',
        'langdetect>=1.0.9',
        'wordcloud>=1.9.0',
        'nltk>=3.8.1',
        'transformers>=4.30.0',
        'torch>=2.0.0',
        'tqdm>=4.65.0',
        'aiohttp>=3.8.5',
        'websockets>=11.0.3',
        'pydantic>=2.0.0',
        'redis>=5.0.0',
        'emoji>=2.10.0',
        'networkx>=3.0',
        'scipy>=1.10.0',
        'tensorflow>=2.12.0',
        'nltk>=3.8.1',
        'spacy>=3.5.0',
        'beautifulsoup4>=4.11.0',
        'textblob>=0.15.3',
        'gensim>=4.3.0'
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
