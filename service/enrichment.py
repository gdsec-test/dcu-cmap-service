def nutrition_label(hostname):
    hostname = hostname.lower()
    dc = hostname[:2]
    os = hostname[3]
    product = hostname[4:]

    dc = dc_finder(dc)

    if dc == 'SG2':
        os = hostname[4]
        os = os_finder(os)

        if hostname[5] == 8:
            product = '4GH'

        elif hostname[5] == 'v' and hostname[7] == 'w':
            product = 'Plesk'
        elif hostname[5] == 'v' and hostname[7] != 'w':
            product = 'VPS'
        else:
            product = product_finder(product)

    elif dc == 'P3' and hostname[4] == 8:
        os = 'Windows'
        product = '2GH'

    elif dc == 'DNS':
        product = 'Closed'

    elif dc == 'Corp':
        product = 'Closed'

    elif dc == 'VPH':
        product = 'Open'

    elif dc == 'Check VAT':
        os = 'Check VAT'
        product = 'Open'

    elif dc == 'Failed':
        product = 'Open'

    else:
        os = os_finder(os)

        if hostname[4] == 'v':
            product = hostname[4:7]
            product = product_finder(product)

        else:
            product = product_finder(product)

    return dc, os, product


def dc_finder(dc):

    if dc == 'p3':
        return 'P3'

    elif dc == 'n1':
        return 'N1'

    elif dc == 'p1':
        return 'P1'

    elif dc == 's2':
        return 'S2'

    elif dc == 'sg':
        return 'SG2'

    elif dc == 'a2':
        return 'A2'

    elif dc == 've':
        return 'Check VAT'

    elif dc == 'cn':
        return 'DNS'

    elif dc == 'vp':
        return 'VPH'

    elif dc == 'fw':
        return 'Corp'

    else:
        return 'Failed'


def os_finder(os):

    if os == 'L' or 'l':
        return 'Linux'
    elif os == 'W' or 'w':
        return 'Windows'
    else:
        print 'Error locating OS'


def product_finder(product):

    if product[0] == 'h' and product[1] == 'g':
        return '4GH'

    elif product[0] == 'h' and product[1] != 'g':
        return '2GH'

    elif product[0] == 'v' and product[2] == 'h':
        return 'VPS'

    elif product[0] == 'v' and product[2] == 'w':
        return 'Plesk'

    elif product[0] == 'w':
        return 'WPaaS'

    elif product[0] == 'c':
        return 'cPanel'
