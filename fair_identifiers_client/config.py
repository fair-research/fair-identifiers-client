from os import path, environ
from six.moves.configparser import ConfigParser
from distutils.version import LooseVersion
import globus_sdk

GLOBUS_SDK_VERSION = tuple(LooseVersion(globus_sdk.__version__).version)
GLOBUS_SDK_MAJOR_VERSION = GLOBUS_SDK_VERSION[0]

_default = path.join(path.expanduser('~'), '.fair_identifier')
IDENTIFIER_CONFIG_FILE = path.abspath(
    environ.get('IDENTIFIER_CONFIG_FILE', _default))
IDENTIFIER_ENVIRONMENT = environ.get('IDENTIFIER_ENVIRONMENT', 'production')

_identifier_environments = {
    'dev': {
        'service_url': 'https://identifiers-test.fair-research.org/',
        'client_id': '653d6d76-70d0-4993-bbd1-459e077b7c16',
        'scope': 'https://auth.globus.org/scopes/identifiers.fair-research.org/writer'
    },
    'production': {
        'service_url': 'https://identifiers.fair-research.org/',
        'client_id': '653d6d76-70d0-4993-bbd1-459e077b7c16',
        'scope': 'https://auth.globus.org/scopes/identifiers.fair-research.org/writer'
    }
}


def _set_defaults(cfg):
    env = _identifier_environments[IDENTIFIER_ENVIRONMENT]
    config.add_section('client')
    cfg.set('client', "service_url", env["service_url"])
    cfg.set('client', "client_id", env["client_id"])
    cfg.set('client', "scope", env["scope"])
    config.add_section('tokens')
    cfg.set('tokens', 'access_token', '')
    cfg.set('tokens', 'access_token_expires', '0')
    cfg.set('tokens', 'refresh_token', '')


config = ConfigParser()


def _save():
    with open(IDENTIFIER_CONFIG_FILE, 'w') as configfile:
        config.write(configfile)


# Monkey-patch config so other things can call
# config.save() without having to care about file
# location.
config.save = _save

if path.exists(IDENTIFIER_CONFIG_FILE):
    config.read(IDENTIFIER_CONFIG_FILE)
else:
    _set_defaults(config)
