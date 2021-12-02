import logging
from globus_sdk import (AccessTokenAuthorizer, ClientCredentialsAuthorizer,
                        RefreshTokenAuthorizer, NativeAppAuthClient)
from globus_sdk import GlobusAPIError
try:
    from globus_sdk import BaseClient
except ImportError:
    # Import for Globus SDK v2. Can be removed once we drop support for v2.
    from globus_sdk.base import BaseClient

from fair_identifiers_client.config import GLOBUS_SDK_MAJOR_VERSION
from fair_identifiers_client.login import extract_and_save_tokens

log = logging.getLogger(__name__)

_namespace_properties = [
    'description', 'display_name', 'creators', 'admins', 'identifier_admins',
    'provider_type', 'provider_config', 'landing_page_skin'
]

_namespace_json_props = [
    'creators', 'admins', 'identifier_admins', 'provider_config'
]

_identifier_properties = ['location', 'checksums', 'metadata', 'visible_to', 'active', 'replaces', 'replaced_by']
_identifier_json_props = ['metadata', 'visible_to', 'location', 'checksums', 'active', 'replaces', 'replaced_by']


def identifiers_client(config, **kwargs):
    app_name = 'fair_identifiers_client'
    base_url = config.get('client', 'service_url')
    client_id = config.get('client', 'client_id')
    access_token = config.get('tokens', 'access_token')
    at_expires = int(config.get('tokens', 'access_token_expires'))
    refresh_token = config.get('tokens', 'refresh_token')
    if not (refresh_token and access_token):
        raise IdentifierNotLoggedIn("Missing tokens")

    def _on_refresh(tkn):
        extract_and_save_tokens(tkn, config)

    authorizer_client = NativeAppAuthClient(client_id, app_name=app_name)
    authorizer = RefreshTokenAuthorizer(
        refresh_token,
        authorizer_client,
        access_token=access_token,
        expires_at=at_expires,
        on_refresh=_on_refresh,
    )

    return IdentifierClient(
        base_url=base_url,
        app_name=app_name,
        authorizer=authorizer,
        **kwargs)


class IdentifierClientError(GlobusAPIError):
    pass


class IdentifierNotLoggedIn(IdentifierClientError):
    def __init__(self, err_msg):
        self.message = err_msg


def _split_dict(in_dict, key_names, nullable_fields=frozenset()):
    """
    Split a dict into two dicts. Keys in key_names go into the new dict if
    their value is present and not None, allowing for None values if the key
    name is present in the nullable_fields set.
    return (updated original dict, new dict)
    """
    new_dict = {}
    for key_name in key_names:
        if key_name in in_dict:
            val = in_dict.pop(key_name, None)
            if val is not None or (val is None and key_name in nullable_fields):
                new_dict[key_name] = val
    return in_dict, new_dict


class IdentifierClient(BaseClient):
    allowed_authorizer_types = (AccessTokenAuthorizer, RefreshTokenAuthorizer,
                                ClientCredentialsAuthorizer)

    error_class = IdentifierClientError
    service_name = 'identifiers'
    base_path = ''

    def __init__(self, *args, **kwargs):
        if GLOBUS_SDK_MAJOR_VERSION >= 3:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(self, "identifier", **kwargs)

    def get(self, path, *args, **kwargs):
        """
        This method overrides the globus_sdk.BaseClient methods to provide a compatibility
        layer between v2 and v3. When ready to drop v2 support, simply delete this method.
        """
        if GLOBUS_SDK_MAJOR_VERSION >= 3:
            return super().get(path, *args, **kwargs)
        else:
            if 'query_params' in kwargs:
                params = kwargs.pop('query_params')
                kwargs['params'] = params
            return super().get(path, *args, **kwargs)

    def delete(self, path, *args, **kwargs):
        """
        This method overrides the globus_sdk.BaseClient methods to provide a compatibility
        layer between v2 and v3. When ready to drop v2 support, simply delete this method.
        """
        if GLOBUS_SDK_MAJOR_VERSION >= 3:
            return super().delete(path, *args, **kwargs)
        else:
            if 'query_params' in kwargs:
                params = kwargs.pop('query_params')
                kwargs['params'] = params
            return super().delete(path, *args, **kwargs)

    def post(self, path, *args, **kwargs):
        """
        This method overrides the globus_sdk.BaseClient methods to provide a compatibility
        layer between v2 and v3. When ready to drop v2 support, simply delete this method.
        """
        if GLOBUS_SDK_MAJOR_VERSION >= 3:
            return super().post(path, *args, **kwargs)
        else:
            if 'query_params' in kwargs:
                params = kwargs.pop('query_params')
                kwargs['params'] = params

            data = None
            if 'data' in kwargs:
                data = kwargs.pop('data')

            return super().post(path, data, **kwargs)

    def put(self, path, *args, **kwargs):
        """
        This method overrides the globus_sdk.BaseClient methods to provide a compatibility
        layer between v2 and v3. When ready to drop v2 support, simply delete this method.
        """
        if GLOBUS_SDK_MAJOR_VERSION >= 3:
            return super().put(path, *args, **kwargs)
        else:
            if 'query_params' in kwargs:
                params = kwargs.pop('query_params')
                kwargs['params'] = params

            data = None
            if 'data' in kwargs:
                data = kwargs.pop('data')

            return super().put(path, data, **kwargs)

    def create_namespace(self, **kwargs):
        """
        ``POST /namespace``

        **Parameters**
          ``display-name`` (*string*)
          display_name of the new namespace
          ``description`` (*string*)
          description of the new namespace
          ``creators`` (* array of string *)
          A list of principal URNs who are "
                      "permitted to add to this namespace"
          ``admins`` (*list of string*)
          A list of principal URNs who are
                      "permitted to perform administrative functions on "
                      "this namespace
          ``provider-type`` (*string*)
          The type of the provider used for minting "
          ``provider-config`` (*dict*)
          Configuration for the provider used for "
                      "minting identifiers in JSON format

        """
        kwargs, body = _split_dict(kwargs, _namespace_properties)
        log.info("IdentifierClient.create_namespace({}, ...)".format(
            body.get('display_name')))
        return self.post('namespace', data=body, query_params=kwargs)

    def update_namespace(self, namespace_id, **kwargs):
        """
        ``PATCH /namespace/<id>``

        ** Parameters **
          ``namespace_id`` (*string*)
          The id for the namespace to update
          ``display_name`` (*string*)
          The updated display name of the namespace
          ``description`` (*string*)
          description of the new namespace
          ``creators`` (*string*)
          The Principal URN for a Globus Group who's members are
          permitted to add to this namespace
          ``admins`` (*string*)
          The Principal URN for a Globus Group who's members are
          permitted to perform administrative functions on this namespace
          ``provider-type`` (*string*)
          The type of the provider used for minting external identifiers
          ``provider-config`` (*dict*)
          Configuration for the provider used for minting external
          identifiers in JSON format

        """
        kwargs, body = _split_dict(kwargs, _namespace_properties)
        log.info(
            "IdentifierClient.update_namespace({}, ...)".format(namespace_id))
        path = 'namespace/{}'.format(namespace_id)
        return self.put(path, data=body, query_params=kwargs)

    def get_namespace(self, namespace_id, **params):
        """
        ``GET /namespace/<namespace_id>

        ** Parameters **
          ``namespace_id`` (*string*)
          The id for the namespace to retrieve
        """
        log.info(
            "IdentifierClient.get_namespace({})".format(namespace_id))
        path = 'namespace/{}'.format(namespace_id)
        return self.get(path, query_params=params)

    def delete_namespace(self, namespace_id, **params):
        """
        ``DELETE /namespace/<namespace_id>

        ** Parameters **
          ``namespace_id`` (*string*)
          The id for the namespace to remove
        """
        log.info(
            "IdentifierClient.delete_namespace({})".format(namespace_id))
        path = 'namespace/{}'.format(namespace_id)
        return self.delete(path, query_params=params)

    def create_identifier(self, **kwargs):
        """
        ``POST /namespace/<namespace_id>/identifier

        ** Parameters **
          ``namespace`` (*string*)
          The id for the namespace in which to add the identifier
          ``replaces`` (*string*)
          The id of the identifier which this identifier replaces, if any.
          ``location`` (* array of string*)
          A list of URLs from which the data referred to by the identifier
          may be retrieved
          ``checksums`` (*array of object*)
          A list of objects, each containing the property ``value``
          indicting the value generated by the checksum function and
          the property ``function`` which indicates which of the known
          checksum functions was used for generating the value
          ``visible_to`` (*array of string*)
          A list of principal urn values or the value 'public' indicating
          what users may see the created identifier
          ``metadata`` (*dict*)
          Additional metadata associated with the identifier

        """
        kwargs, body = _split_dict(kwargs, _identifier_properties)
        log.info('IdentifierClient.create_identifier({}, ...)'.format(
                 body.get('namespace_id')))
        path = 'namespace/{}/identifier'.format(kwargs['namespace'])
        return self.post(path, data=body, query_params=kwargs)

    def get_identifier_by_checksum(self, checksum, function=None):
        """
        ``GET /checksum/<checksum>?function=<function>
        ** Parameters **
        ``checksum`` The checksum generated by hashing a file with ``function``
        ``function`` The algorithm used to generate the checksum
        """
        log.info('IdentifierClient.get_checksum({}, {})'.format(
                 checksum, function))
        path = 'checksum/{}'.format(checksum)
        return self.get(path, query_params={'function': function})

    def get_identifier(self, identifier_id):
        """
        ``GET /<identifier_id>

        ** Parameters **
        ``identifier_id`` The identification url for the identifier
        """
        log.info('IdentifierClient.get_identifier({})'.format(identifier_id))
        return self.get(identifier_id)

    def update_identifier(self, identifier_id, **kwargs):
        """
        ``PATCH /<identifier_id>

        ** Parameters **
          ``identifier_id`` (*string*)
          The identification url for the identifier
          ``active`` (*boolean*)
          The state of the identifier. It is either active or inactive
          ``replaces`` (*string*)
          The id of the identifier which this identifier replaces, if any
          ``replaced_by`` (*string*)
          The id of the identifier that replaces this identifier, if any
          ``location`` (* array of string*)
          A list of URLs from which the data referred to by the identifier
          may be retrieved
          ``checksums`` (*array of object*)
          A list of objects, each containing the property ``value``
          indicting the value generated by the checksum function and
          the property ``function`` which indicates which of the known
          checksum functions was used for generating the value
          ``visible_to`` (*array of string*)
          A list of principal urn values or the value 'public' indicating
          what users may see the created identifier
          ``metadata`` (*dict*)
          Additional metadata associated with the identifier

        """
        kwargs, body = _split_dict(kwargs, _identifier_properties,
                                   nullable_fields=frozenset(["replaces", "replaced_by"]))
        log.info('IdentifierClient.update_identifier({}, ...)'.format(identifier_id))
        return self.put(identifier_id, data=body, query_params=kwargs)
