from setuptools import setup, find_packages


setup(
    name='fair-identifiers-client', version='0.3.0',
    description='FAIR Research Identifiers Service Client',
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        "globus-sdk>=1.6.0",
        "six>=1.10.0,<2.0.0",
    ],
    entry_points={
        'console_scripts': [
            'fair-identifiers-client = fair_identifiers_client:main'
        ]
    }
)
