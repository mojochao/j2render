import json
import os
from importlib import import_module

import click
import jinja2
import munch
import toml
import yaml


_VALID_FILE_EXTENSIONS = {
    '.json': 'json',
    '.toml': 'toml',
    '.yaml': 'yaml',
    '.yml': 'yaml'
}
# Dict[str, str]: Valid data file extensions.

_VALID_FILE_FORMATS = set(_VALID_FILE_EXTENSIONS.values())


@click.command()
@click.option('-s', '--source', 'sources', metavar='LOCATION', multiple=True,
              help='Template data source. May be provided multiple times.')
@click.option('-v', '--variable', 'variables', metavar='NVP', multiple=True,
              help='Template name=value variable. May be provided multiple times.')
@click.option('-o', '--output', metavar='FILE',
              help='Write output to named file or standard output.')
@click.option('-d', '--output-dir', metavar='DIR',
              help='Write output to named directory.')
@click.option('--no-trim-blocks', is_flag=True,
              help='Render with trim_blocks=False.')
@click.option('--no-lstrip-blocks', is_flag=True,
              help='Render with lstrip_blocks=False.')
@click.option('--no-trailing-newline', is_flag=True,
              help='Render with keep_trailing_newline=False.')
@click.argument('template')
def cli(sources, variables, output, output_dir, no_trim_blocks, no_lstrip_blocks, no_trailing_newline, template):
    """j2render is a cli for jinja2 template rendering.

    The *--source* option may be provided multiple times and provides the
    locations of the sources provided data to be used in template rendering.

    Locations may be provided as a path to a JSON, TOML, or JSON file
    containing template data, or as a module attribute string such as
    ``my.pkg:data`` describing the name of the module containing a dict
    attribute containing template data.

    If no locations are provided, templates named after the template with
    JSON, TOML, and YAML file extensions will be looked for in the current
    working directory followed by the directory containing the template.

    The *--variable* option may be provided multiple times and provides any
    overrides to apply to the template data provided by the *--source* option.
    The format of this argument is ``name=value``, where name is a scalar or
    dotted property of the form ``some_prop`` or ``some.nested.prop``.

    The *--output* option may be provided to name the output file the rendered
    template is written to.  If not provided, defaults to a file in the
    template's directory named same as the template with the ``.j2`` or
    ``.jinja2`` extension removed.  If ``stdout`` is specified, the rendered
    template will be written to standard output.

    The *--output-dir* option may be provided to name the directory.  If not
    provided, defaults to the directory containing the template.


    """
    try:
        # Load all template data from sources.
        if not sources:
            source = _find_data_file(template)
            if not source:
                raise RuntimeError('no data source found for template {}'.format(template))
            sources = [source]
        template_variables = {}
        for source in sources:
            loaded = _load_variables_from_module(source) if ':' in source else _load_variables_from_data_file(source)
            template_variables = dict(_merge(template_variables, loaded))

        template_variables = munch.munchify(template_variables)
        overrides = {}
        for variable in variables:
            _update(template_variables, variable)
        template_variables = dict(_merge(template_variables, overrides))
        if not template_variables:
            raise RuntimeError('no template data found for template {}'.format(template))

        # Load template and render.
        loaded = _load_template(template, not no_trim_blocks, not no_lstrip_blocks, not no_trailing_newline)
        try:
            rendered = loaded.render(**template_variables)
        except jinja2.TemplateError as err:
            raise RuntimeError('template render error: {}'.format(err))

        # Write rendered output.
        if output and output.upper() == 'STDOUT':
            print(rendered)
            return
        if output is None:
            output, _ = os.path.splitext(template)
            if output_dir is not None:
                os.makedirs(output_dir, exist_ok=True)
                output = os.path.join(output_dir, os.path.basename(output))
        try:

            with open(output, 'w') as outfile:
                outfile.write(rendered)
            print('rendered template written to {}'.format(os.path.abspath(output)))
        except OSError as err:
            raise RuntimeError('template output error: {}'.format(err))

    except RuntimeError as err:
        raise click.ClickException(str(err))


def _find_data_file(path):
    """Find data file for template at *path*.

    Looks for a data file named after the template with one of the supported
    file extensions from the current working directory or the directory
    containing the template.

    Args:
        path (str): template path

    Returns:
        str | None: found data file path

    """
    base_name = os.path.basename(path)
    name, _ = os.path.splitext(base_name)
    dir_name = os.path.abspath(os.path.dirname(path))
    dir_names = [os.getcwd(), dir_name]
    for dir_name in dir_names:
        for extension in _VALID_FILE_EXTENSIONS:
            data_path = os.path.join(dir_name, name + extension)
            if os.path.exists(data_path):
                return data_path
    return None


def _load_template(path, trim_blocks=False, lstrip_blocks=False, keep_trailing_newline=False):
    """Load template from *path*.

    Args:
        path (str): template path
        trim_blocks (bool): remove first newline after a block
        lstrip_blocks (boo): remove leading spaces and tabs from the start of a line to a block
        keep_trailing_newline (bool): preserve trailing newline in template

    Returns:
        jinja2.Template: found data file path


    """
    dir_path = os.path.dirname(path)
    template_name = os.path.basename(path)
    try:
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(dir_path),
            trim_blocks=trim_blocks,
            lstrip_blocks=lstrip_blocks,
            keep_trailing_newline=keep_trailing_newline)
        return env.get_template(template_name)
    except jinja2.TemplateError as err:
        raise RuntimeError('cannot load template {}: {}'.format(path, err))


def _load_variables_from_data_file(path, fmt=None):
    """Load template variables from a file.

    Args:
        path (str): path to file containing template variables

    Returns:
        dict: template variables

    Raises:
        RuntimeError: on error

    """
    if fmt is None:
        fmt = _get_file_format(path)
    if fmt not in _VALID_FILE_FORMATS:
        raise RuntimeError('invalid format for file {}'.format(path))
    try:
        with open(path) as infile:
            variables = dict()
            if fmt == 'json':
                variables = json.load(infile)
            elif fmt == 'toml':
                variables = toml.load(infile)
            elif fmt == 'yaml':
                variables = yaml.load(infile)
    except OSError as err:
        raise RuntimeError('cannot open {}: {}'.format(path, err))
    except Exception as err:
        raise RuntimeError('cannot load data from {}: {}'.format(path, err))
    if not isinstance(variables, dict):
        raise RuntimeError('data from {} is not a dict: {}'.format(path, variables))
    return variables


def _load_variables_from_module(path):
    """Load template variables from a Python module attribute.

    The variables path for modules is of the form::

        my.module:some_data

    Where ``my.module`` is the name of a module containing a dict attribute
    named ``some_data``.

    Args:
        path (str): module and attr name containing template variables

    Returns:
        dict: template variables

    Raises:
        RuntimeError: on error

    """
    try:
        module_name, module_attr = path.split(':')
    except ValueError:
        raise RuntimeError('module data path {} is invalid'.format(path))
    try:
        module = import_module(module_name)
    except ImportError:
        raise RuntimeError('module {} cannot be imported'.format(module_name))
    try:
        variables = getattr(module, module_attr)
    except AttributeError:
        raise RuntimeError('module {} attribute {} not found'.format(module_name, module_attr))
    if not isinstance(variables, dict):
        raise RuntimeError('module data {} is not a dict'.format(variables))
    return variables


def _get_file_format(path):
    """Get file format from *path*.

    Args:

        path (str): path to file containing template variables

    Returns:
        str | None: format of file

    """
    _, ext = os.path.splitext(path)
    ext = ext.lower()
    return _VALID_FILE_EXTENSIONS.get(ext) if ext else None


def _merge(original, deltas):
    """Merge two dictionaries.

    Args:
        original (Dict[str, Any]): original data
        deltas (Dict[str, Any]): deltas data

    Yields:
        Tuple[str, Any]: merged keys and values

    """
    for k in set(original.keys()).union(deltas.keys()):
        if k in original and k in deltas:
            if isinstance(original[k], dict) and isinstance(deltas[k], dict):
                yield k, dict(_merge(original[k], deltas[k]))
            else:
                yield k, deltas[k]
        elif k in original:
            yield k, original[k]
        else:
            yield k, deltas[k]


def _update(data, update):
    """Update *data* identified by *name* with *value*.

    Args:
        data (munch.Munch): data to update
        update (str): update to apply

    Raises:
        RuntimeError: on error

    """
    try:
        name, value = update.split('=')
    except ValueError:
        raise RuntimeError('update {} is malformed'.format(update))

    if '.' not in name:
        data[name] = value
        return

    prop_parts = name.split('.')
    if len(prop_parts) > 1:
        parent_prop_name = '.'.join(prop_parts[:-1])
        name = prop_parts[-1]
        config = eval('data.{}'.format(parent_prop_name))
    else:
        config = data
    config[name] = value


if __name__ == "__main__":
    cli()
