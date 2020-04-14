import json
# Pattern (and code) taken from:
# https://gist.github.com/mivade/384c2c41c3a29c637cb6c603d4197f9f
FILE_SPECIFIER = 'file://'


def argument(*name_or_flags, **kwargs):
    """Convenience function to properly format arguments to pass to the
    subcommand decorator.
    """
    args = list()
    for arg in name_or_flags:
        args.append(arg)
    return args, kwargs


def subcommand(args, parent, **kwargs):
    def decorator(func):
        parser = parent.add_parser(
            func.__name__.replace('_', '-'),
            description=func.__doc__,
            **kwargs)
        for arg in args:
            parser.add_argument(*arg[0], **arg[1])
        parser.set_defaults(func=func)
        return func

    return decorator


_internal_arg_names = ['func', 'subcommand', 'identifier']


def clear_internal_args(args):
    for arg_name in _internal_arg_names:
        try:
            args.pop(arg_name)
        except KeyError:
            pass  # Its ok if the key is not in the list to be cleared
    return args


def load_metadata(argument):
    metadata = {}
    if argument.startswith(FILE_SPECIFIER):
        fname = argument.replace(FILE_SPECIFIER, '')
        with open(fname) as f:
            metadata = json.loads(f.read())
    else:
        metadata = json.loads(argument)
    return metadata


def set_checksum_args(arguments):
    """
    Argparse parses checksums as {'checksum_sha256': '<sha256_hash>'}

    Return a list of these arguments in a format the Identifiers Service
    understands:

    "checksums": [
      {
        "function": "md5",
        "value": "fobarbas"
      },
      {
        "function": "sha256",
        "value": "foobarbaz"
      }
    ],

    Note: This modifies the values in 'arguments'
    """
    checksum_args = [
        {'function': arg_name.replace('checksum_', '').replace('_', '-'),
         'value': arguments.pop(arg_name)}
        for arg_name in list(arguments.keys())
        if arg_name.startswith('checksum') and arguments[arg_name] is not None
    ]
    if checksum_args:
        arguments['checksums'] = checksum_args
    return arguments


def parse_none_values(values, none_value='None'):
    options = {}
    for option_name, option_value, option_none_value in values:
        if isinstance(option_value, str) and option_value == none_value:
            options[option_name] = option_none_value
        elif isinstance(option_value, list) and option_value == [none_value]:
            options[option_name] = option_none_value
        elif option_value:
            options[option_name] = option_value
    return options
