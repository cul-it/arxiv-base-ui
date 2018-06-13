"""Helpers for working with URLs in arXiv Flask applications."""

from urllib.parse import parse_qs
from werkzeug.urls import url_encode, url_parse, url_unparse, url_encode
from flask import current_app
from arxiv.base import config
from arxiv.base.exceptions import ConfigurationError


def config_url(target: str, path_params: dict = {}, params: dict = {}) -> str:
    """
    Generate a URL from this app's configuration.

    This will load the value of the configuration parameter
    `ARXIV_{target}_URL` from either the current application configuration
    (preferred), or the base configuration defined in this package (see
    :mod:`arxiv.base.config`).

    Note: this function relies on the `flask.current_app` proxy object, which
    means that it can only be used in an application or request context.

    Parameters
    ----------
    target : str
        Name of the endpoint, defined as `ARXIV_{target}_URL` in the
        application configuration.
    path_params : dict
        Parameters used to format the URL. For example, if the value of the
        configuration parameter is `http://arxiv.org/abs/{arxiv_id}/`,
        passing `path_params = {'arxiv_id': '1901.00123'}` would generate the
        URL `http://arxiv.org/abs/1901.00123`.
    params : dict
        GET request parameters to add to the URL.

    Returns
    -------
    str

    Raises
    ------
    :class:`.ConfigurationError`
        Raised if the configuration parameter for `target` cannot be found.

    Examples
    --------

    .. code-block:: python

       from arxiv.base.urls import config_url
    """
    target = target.upper()
    # Look for the URL on the config of the current app (this will *not* be
    # base); fall back to the base config if not found.
    try:
        url: str = current_app.config.get(f'ARXIV_{target}_URL')
        if url is None:
            url = getattr(config, f'ARXIV_{target}_URL')

    except AttributeError as e:
        raise ConfigurationError(f'URL for {target} not set') from e

    # Format with path parameters.
    try:
        url = url.format(**path_params)
    except KeyError as e:
        raise ValueError('Missing a required parameter: %s' % e) from e

    # Format with request parameters.
    parts = url_parse(url)
    params.update(parse_qs(parts.query))
    parts = parts.replace(query=url_encode(params))
    url = url_unparse(parts)
    return url