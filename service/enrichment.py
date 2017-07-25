def nutrition_label(hostname):
    hostname = hostname.lower()
    dc = hostname[:2]
    os = hostname[3]
    product = hostname[4:]

    dc = dc_finder(dc)

    if dc == 'SG2':
        os = hostname[4]
        os = os_finder(os)

        if hostname[5] == '8':
            product = '4GH'

        elif hostname[5] == 'v':
            product = 'VPS'
            if hostname[7] == 'w':
                product = 'Plesk'

        else:
            product = product_finder(product)

    elif dc == 'P3' and hostname[4] == '8':
        os = 'Windows'
        product = '2GH'

    elif dc == 'DNS':
        product = 'Not Hosting'

    elif dc == 'Corp':
        product = 'Not Hosting'

    elif dc == 'VPH':
        product = 'VPH'

    elif dc == 'vert':
        dc = 'P3'
        os = ''
        product = 'Vertigo'

    elif dc == 'Failed':
        product = 'Not Hosting'

    else:
        os = os_finder(os)

        if hostname[4] == 'v':
            product = hostname[4:7]
            product = product_finder(product)

        else:
            product = product_finder(product)

    return dc, os, product


def dc_finder(dc):
    result = {
        'p3': 'P3',
        'n1': 'N1',
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


def os_finder(os):

    if os == 'L' or 'l':
        return 'Linux'
    elif os == 'W' or 'w':
        return 'Windows'
    else:
        print 'Error locating OS'


def product_finder(product):
    if product[0] == 'h':
        if product[1] == 'g':
            return '4GH'
        return '2GH'

    elif product[0] == 'v':
        if product[2] == 'h':
            return 'VPS'
        return 'Angelo'

    elif product[:3] == 'wvp':
        return 'Angelo'

    elif product[0] == 'c':
        return 'Diablo'
