import os
from setuptools import setup, find_packages

# Get the long description from the README file
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(BASE_DIR, 'README.md')) as f:
    long_description = f.read()


setup(
    name='fair-identifiers-client',
    version='0.5.1',
    url='https://github.com/fair-research/fair-identifiers-client',
    author="FAIR Research Team",
    description='FAIR Research Identifiers Service Client',
    long_description=long_description,
    long_description_content_type='text/markdown',
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        "globus-sdk>=1.6.0,<4.0.0",
        "six>=1.10.0,<2.0.0",
    ],
    entry_points={
        'console_scripts': [
            'fair-identifiers-client = fair_identifiers_client:main'
        ]
    },
    license='Apache 2.0',
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Operating System :: POSIX',
    ]
)
