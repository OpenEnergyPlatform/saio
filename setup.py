from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='saio',  # Required
    version='0.2',  # Required
    description='SQLAlchemyIO (saio): Module hack for autoloading table definitions',  # Optional
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',
    url='https://github.com/coroa/saio',
    author='Jonas Hörsch',  # Optional
    author_email='coroa@posteo.de',  # Optional

    # Classifiers help users find your project by categorizing it.
    #
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    py_modules=["saio"],
    python_requires='>=3.4, <4',
    install_requires=['sqlalchemy'],  # Optional
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/coroa/saio/issues',
        'Source': 'https://github.com/coroa/saio/',
    },
)
