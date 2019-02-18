def parse_hostname(hostname):
    hostname = hostname.lower()

    dc = hostname[:2]
    os = hostname[3]
    product = hostname[4:]

    dc = get_dc(dc)

    if dc == 'SG2':
        os = hostname[4]
        os = get_os(os)

        if hostname[5] == '8':
            product = '4GH'

        elif hostname[5] == 'v' and hostname[7] == 'w':
            product = 'Plesk'
        elif hostname[5] == 'v' and hostname[7] != 'w':
            product = 'VPS'
        elif hostname[5:9] == 'cpnl' or hostname[5:8] == 'pcs':
            product = 'Diablo'
        else:
            product = get_product(product)

    elif dc == 'P3' and hostname[4] == '8':
        os = 'Windows'
        product = '2GH'

    elif dc == 'DNS':
        product = 'Not Hosting'

    elif dc == 'Corp':
        product = 'Not Hosting'

    elif dc == 'VPH':
        os = ''
        product = 'VPH'

    elif dc == 'vert':
        os = ''
        product = 'Vertigo'

    elif dc == 'Failed':
        product = 'Not Hosting'

    else:
        os = get_os(os)

        if hostname[4] == 'v':
            product = hostname[4:7]
            product = get_product(product)

        else:
            product = get_product(product)

    return dc, os, product


def get_dc(dc):
    result = {
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
    }.get(dc, 'Failed')
    return result


def get_os(os):
    if os == 'l':
        return 'Linux'
    elif os == 'w':
        return 'Windows'
    return


def get_product(product):
    if product[0] == 'h':
        if product[1] == 'g':
            return '4GH'
        return '2GH'

    elif product[0] == 'v':
        if product[2] == 'h':
            return 'VPS'
        elif product[1] == 'c':
            return 'Diablo'
        return 'Angelo'

    elif product[:3] == 'wvp':
        return 'Angelo'

    elif product[0] == 'c' or product[:3] == 'pcs':
        return 'Diablo'
