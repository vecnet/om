from urlparse import ParseResult, urlparse


def custom_urlparse(url):
    """
    This is customized variant of the urlparse function.  It's needed because
    data: URIs have been created which are not handled by the urlparse function
    correctly.  They were created from file contents that contained URL
    reserved characters like "?" # and "#".  Unfortunately, these reserved
    characters were not escaped.

    To handle these "broken" data: URIs, we generate a parse result manually
    to ensure the path contains all the file contents.
    """
    parsed_url = urlparse(url)
    if parsed_url.scheme == 'data':
        parsed_url = ParseResult('data', parsed_url.netloc, url[5:], '', '', '')
    return parsed_url
