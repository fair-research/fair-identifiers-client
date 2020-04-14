from __future__ import print_function
import sys
import json
import logging

from fair_identifiers_client.config import config
from fair_identifiers_client.local_server import is_remote_session
from fair_identifiers_client.identifiers_api import (identifiers_client, IdentifierClientError, IdentifierNotLoggedIn)
from fair_identifiers_client.login import (LOGGED_IN_RESPONSE, LOGGED_OUT_RESPONSE, check_logged_in, do_link_login_flow,
                                           do_local_server_login_flow, revoke_tokens)
from fair_identifiers_client.helpers import (subcommand, argument, clear_internal_args, load_metadata,
                                             set_checksum_args, parse_none_values)
from argparse import ArgumentParser

log = logging.getLogger(__name__)

cli = ArgumentParser()
subparsers = cli.add_subparsers(dest="subcommand")

_namespace_skin_props = [
    'header_background', 'header_icon_url', 'header_icon_link', 'header_text',
    'page_title', 'favicon_url', 'preamble_text'
]

SUPPORTED_CHECKSUMS = (
    'dsa',
    'dsa-sha',
    'dsaencryption',
    'dsawithsha',
    'ecdsa-with-sha1',
    'md4',
    'md5',
    'ripemd160',
    'sha',
    'sha1',
    'sha224',
    'sha256',
    'sha384',
    'sha512',
    'whirlpool'
)
CHECKSUM_HELP = 'Checksum of the identifiers content with the {} algorithm'

checksum_arguments = [argument('--checksum-{}'.format(alg),
                               help=CHECKSUM_HELP.format(alg)
                               )
                      for alg in SUPPORTED_CHECKSUMS]


@subcommand([
        argument(
            '--force',
            action='store_true',
            default=False,
            help='Do a fresh login, ignoring any existing credentials'),
        argument(
            "--no-local-server",
            action='store_true',
            default=False,
            help=("Manual login by copying and pasting an auth code. "
                  "This will be implied if using a remote connection.")),
    ],
    parent=subparsers,
    help='Log in via Globus to get credentials for the FAIR Research Identifiers Client',
)
def login(args):
    # if not forcing, stop if user already logged in
    if not args.force and check_logged_in():
        print(LOGGED_IN_RESPONSE)
        return

    # use a link login if remote session or user requested
    if args.no_local_server or is_remote_session():
        do_link_login_flow()
    # otherwise default to a local server login flow
    else:
        do_local_server_login_flow()


@subcommand([], parent=subparsers, help='Log out of FAIR Research Identifiers Client')
def logout(args):
    revoke_tokens(config)
    config.set('tokens', 'access_token', '')
    config.set('tokens', 'access_token_expires', '0')
    config.set('tokens', 'refresh_token', '')
    config.save()
    print(LOGGED_OUT_RESPONSE)


@subcommand([
    argument(
        "--display-name",
        required=True,
        help="display_name of the new namespace"),
    argument(
        "--description",
        required=True,
        help="description of the new namespace"),
    argument(
        "--creators",
        nargs="*",
        help="The Principal URN for a Globus Group who's members "
        "are permitted to add to this namespace. Defaults to the same value as "
        "admins"),
    argument(
        "--admins",
        nargs='+',
        help="The Principal URN for a Globus Auth Identity or Globus Group "
        "who's members "
        "are permitted to perform administrative functions on "
        "this namespace"),
    argument(
        "--identifier-admins",
        nargs='+',
        help="The Principal URN for a Globus Auth Identity or Globus Group "
        "who's members "
        "are permitted to administrate identifiers created "
        "in this namespace"),
    argument(
        "--provider-type",
        required=True,
        help="The type of the provider used for minting "
        "identifiers"),
    argument(
        "--provider-config",
        help="Configuration for the provider used for "
        "minting identfiers in JSON format"),
    argument(
        "--header-background",
        help="HTML background color for header of landing page"),
    argument(
        "--header-icon-url",
        help="A URL for an image (icon) to be displayed in the "
        "header of the landing page"),
    argument(
        "--header-icon-link",
        help="A URL for a hyperlink when the header icon is "
        "clicked on in the landing page"),
    argument(
        "--header-text",
        help="A short text string to be placed in the header "
        "of the landing page next to the icon image"),
    argument(
        "--page-title",
        help="A short text string to be placed in the page "
        "(tab) title"),
    argument(
        "--favicon-url",
        help="A URL for the favicon to be displayed in the "
        "page/tab title"),
    argument(
        "--preamble-text",
        help="Short text placed above the metadata of the "
        "identifier on the landing page")
    ],
    parent=subparsers
)
def namespace_create(args):
    """
    Create a new namespace
    """
    client = identifiers_client(config)
    args = clear_internal_args(vars(args))
    # Convenience helper: If user doesn't specify a member
    # group, just use the same group as for admins.
    # This means all members will be admins.
    if 'creators' not in args:
        args['creators'] = args['admins']
    return client.create_namespace(**args)


@subcommand([
    argument(
        "--namespace-id",
        help="The id for the namespace to update",
        required=True),
    argument(
        "--display-name", help="The updated display_name of the namespace"),
    argument("--description", help="The updated description of the namespace"),
    argument(
        "--creators",
        nargs="*",
        help="The Principal URN for a Globus Group who's members are "
        "permitted to add to this namespace"),
    argument(
        "--admins",
        nargs="+",
        help="The Principal URN for a Globus Group who's members are "
        "permitted to perform administrative functions on "
        "this namespace"),
    argument(
        "--provider-type",
        help="The type of the provider used for minting "
        "identifiers"),
    argument(
        "--provider-config",
        help="Configuration for the provider used for "
        "minting identfiers in JSON format")
    ],
    parent=subparsers
)
def namespace_update(args):
    """
    Update the properties of an existing namespace
    """
    client = identifiers_client(config)
    args = clear_internal_args(vars(args))

    # Convenience helper: If user doesn't specify a member
    # group, just use the same group as for admins.
    # This means all members will be admins.
    if 'creators' not in args:
        args['creators'] = args['admins']
    namespace_id = args.pop('namespace_id')
    return client.update_namespace(namespace_id, **args)


@subcommand([
    argument(
        "--namespace-id",
        help="The id for the namespace to display",
        required=True)
],
    parent=subparsers
)
def namespace_display(args):
    """
    Display a namespace
    """
    client = identifiers_client(config)
    return client.get_namespace(args.namespace_id)


@subcommand([
    argument(
        "--namespace-id",
        help="The id for the namespace to update",
        required=True)
    ],
    parent=subparsers
)
def namespace_delete(args):
    """
    Remove an existing namespace
    """
    client = identifiers_client(config)
    return client.delete_namespace(args.namespace_id)


@subcommand([
    argument(
        "--namespace",
        help="The id for the namespace in which to add the "
        "identifier",
        required=True),
    argument(
        "--replaces",
        help="The id of the identifier which this identifier replaces"),
    argument(
        "--locations",
        nargs='+',
        help="A list of URLs from which the data referred to "
        "by the identifier may be retrieved"),
    argument(
        "--visible-to",
        required=True,
        nargs='+',
        help='List of users allowed to view the identifier '
        '(e.g. "public")'),
    argument(
        "--metadata",
        help='Additional metadata associated with the '
        'identifier in JSON format '
        '(e.g. file://foo.json or \'{"author": "John Doe", "year": 2018}\')',
        type=load_metadata)
    ] + checksum_arguments,
    parent=subparsers
)
def identifier_create(args):
    """
    Create a new identifier
    """
    client = identifiers_client(config)
    args = clear_internal_args(vars(args))
    args = set_checksum_args(args)
    if args.get('locations'):
        args['location'] = args.pop('locations')
    return client.create_identifier(**args)


@subcommand([
    argument(
        "--identifier",
        help="The id for the identifier to update",
        required=True),
    argument(
        "--activate",
        help="Mark the identifier as active",
        action='store_true',
        default=None),
    argument(
        "--deactivate",
        help="Mark the identifier as inactive",
        action='store_true',
        default=None),
    argument(
        "--replaces",
        help="The id of the identifier which this identifier replaces"),
    argument(
        "--replaced-by",
        help="The id of the identifier that replaces this identifier"),
    argument(
        "--locations",
        nargs='+',
        help="A list of URLs from which the data referred to "
             "by the identifier may be retrieved"),
    argument(
        "--metadata",
        help='Additional metadata associated with the '
             'identifier in JSON format '
             '(e.g. file://foo.json or '
             '\'{"author": "John Doe", "year": 2018}\')',
        type=load_metadata)
    ] + checksum_arguments,
    parent=subparsers
)
def identifier_update(args):
    """
    Update the state of an identifier
    """
    client = identifiers_client(config)
    identifier_id = args.identifier
    args = clear_internal_args(vars(args))
    args = set_checksum_args(args)
    optional_values = [
        ('replaces', args['replaces'], None),
        ('replaced_by', args['replaced_by'], None),
        ('location', args['locations'], [])
    ]
    args = (parse_none_values(optional_values))
    activate = args.get('activate')
    deactivate = args.get('deactivate')
    if activate and deactivate:
        raise IdentifierClientError("Error: argument --activate: not allowed with argument --deactivate")
    if activate:
        args['active'] = args.pop('activate')
    elif deactivate:
        args['active'] = not args.pop('deactivate')
    return client.update_identifier(identifier_id, **args)


@subcommand([
    argument(
        "--identifier", help="The id for identifier to display", required=True)
    ],
    parent=subparsers
)
def identifier_display(args):
    """
    Display the state of an identifier
    """
    client = identifiers_client(config)
    return client.get_identifier(args.identifier)


@subcommand([
    argument(
        "--checksum",
        help="An identifiers checksum",
        required=True),
    argument(
        "--function",
        help="The corresponding function used to generate the above checksum",
        required=True)
    ],
    parent=subparsers
)
def identifier_from_checksum(args):
    client = identifiers_client(config)
    return client.get_identifier_from_checksum(args.checksum, args.function)


def main():
    args = cli.parse_args()
    subcommand = args.subcommand
    if subcommand is None:
        cli.print_help()
    else:
        try:
            ret = args.func(args)
            # These two don't make API calls:
            if subcommand not in ('login', 'logout'):
                print(json.dumps(ret.data, indent=2))
        except IdentifierNotLoggedIn as err:
            log.info(err)
            msg = "Not logged in. Use:\n  identifier login\nto log in."
            print(msg, file=sys.stderr)
        except IdentifierClientError as nce:
            print(
                'Command {} failed with HTTP Status code {}, details:\n{}'.
                format(subcommand, nce.http_status, nce.message),
                file=sys.stderr)
        except ValueError as ve:
            print(ve)


if __name__ == "__main__":
    main()
