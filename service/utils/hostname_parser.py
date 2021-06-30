import re


def parse_hostname(hostname):
    if not hostname:
        return None, None, None

    os = product = None
    hostname = str(hostname).lower()
    dc = get_dc(hostname[:2])

    if re.search('\\dpl(v?)cpnl\\d|\\dplpcs\\d|5gh', hostname):
        os = 'Linux'
        product = 'Diablo'

    if re.search('\\dnwvpweb\\d', hostname):
        os = 'Windows'
        product = 'Plesk'

    elif re.search('vertigo', hostname):
        product = 'Vertigo'

    elif re.search('\\dnw8shg\\d', hostname):
        os = 'Windows'
        product = '4GH'

    elif re.search('\\dnlhg\\d', hostname):
        os = 'Linux'
        product = '4GH'

    elif re.search('.myftpupload.com$', hostname):
        os = 'Linux'
        product = 'MWP 1.0'

    elif re.search('dpsweb|starkgate|p3pwssweb', hostname):
        product = 'GoCentral'

    elif re.search('openstack', hostname):
        product = 'OpenStack'

    elif re.search('short(ener?|app?)', hostname):
        product = 'Shortener'

    elif re.search('^vph', hostname):
        product = 'VPH'

    elif re.search('\\dplvph', hostname):
        os = 'Linux'
        product = 'VPH'

    elif re.search('\\dpwvph', hostname):
        os = 'Windows'
        product = 'VPH'

    elif re.search('\\dnw8sh\\d', hostname):
        os = 'Windows'
        product = '2GH'

    elif re.search('\\dslh\\d', hostname):
        os = 'Linux'
        product = '2GH'

    elif re.search('gemwbe|wbeout', hostname):
        product = 'GEM'

    elif re.search('redir', hostname):
        product = 'EOL'

    return dc, os, product


def get_dc(dc):
    return {
        'p3': 'P3',
        'n1': 'N1',
        'n2': 'N2',
        'n3': 'N3',
        'p1': 'P1',
        's2': 'S2',
        'sg': 'SG2',
        'a2': 'A2',
        've': 'vert',
        'cn': 'DNS',
        'vp': 'VPH',
        'fw': 'Corp'
    }.get(dc, None)
