"""
getMODIS

download.py

Download script that manages SOAP interfaces and MODIS product saves.

Author: G. Worrall

Started: 30th July 2020
Last updated: 30th July 2020
"""

# TODO: remove pprint after development
# TODO: write function that formats MODIS data into layered raster
# TODO: write function that takes datetime objects, shapely / geometry files
#       and a product name / bands and kicks it all out as a raster / 
#       formatted array
import json
import requests

import pprint
pp = pprint.PrettyPrinter()

modis_rest_api = 'https://modis.ornl.gov/rst/api/v1/'
json_header = {'Accept': 'application/json'}


def get_data(search_params):
    """
    Get data for products given a combination of search terms.

    Parameters
    ----------
    search_params : dict
        Can contain any/all of the following keys (required are labelled):
            product : REQUIRED
            siteid
            network
            network_siteid
            band : REQUIRED -> can specify 'all' for all bands
            latitude : REQUIRED
            longitude : REQUIRED
            startDate : REQUIRED
            endDate : REQUIRED
            kmAboveBelow : REQUIRED
            kmLeftRight : REQUIRED
            email : specify if you want result emailed to you
            uid : specify if you want to declare an order number.
                    It will be available at:
                        https://modis.ornl.gov/subsetdata/{OrderID}

    Returns
    -------
    dict
        Containg data values nested among metadata
        Example output:
            {'band': 'sur_refl_b06',
             'cellsize': 463.312716528,
             'header': 'https://modisrest.ornl.gov/rst/api/...'
             'latitude': 39.56499,
             'longitude': -121.55527,
             'ncols': 3,
             'nrows': 2,
             'scale': '0.0001',
             'subset': [{'band': 'sur_refl_b06',
                         'calendar_date': '2003-04-15',
                         'data': [1610,
                                  1610,
                                  1658,
                                  1590,
                                  -28672,
                                  -28672],
                         'modis_date': 'A2003105',
                         'proc_date': '2015157083335',
                         'tile': 'h08v05'}],
             'units': 'reflectance',
             'xllcorner': '-10420829.58',
             'yllcorner': '4398227.66'}


    Note
    ----
    See ORNL documentation at:
        https://modis.ornl.gov/data/modis_webservice.html
    """
    default_args ={ 
        'product': None,
        'siteid': None,
        'network': None,
        'network_siteid': None,
        'band': None,
        'latitude': None,
        'longitude': None,
        'startDate': None,
        'endDate': None,
        'kmAboveBelow': None,
        'kmLeftRight': None,
        'email': None,
        'uid': None
    }
    diff = set(search_params.keys()) - set(default_args.keys())
    if diff:
        raise ValueError("Invalid search paramters: ", diff)

    product = search_params.pop('product')

    # Set product url
    subset_url = modis_rest_api + product + '/subset?'

    # If we want all bands, have to send through recursive requests.
    if search_params['band'] != 'all':
        response = requests.get(subset_url, params=search_params)
        results = json.loads(response.text)
    else:
        bands = get_bands(product)
        # Extract the formatted names of the bands only.
        bands = [band['band'] for band in bands['bands']]
        results = {}
        for band in bands:
            search_params['band'] = band
            response = requests.get(subset_url, params=search_params)
            result = json.loads(response.text)
            results[band] = result

    return results


def get_products():
    """
    Get a list of available MODIS products.

    Parameters
    ----------
    None

    Returns
    -------
    dict
        contains list of product names and information.
    """
    response = requests.get(modis_rest_api + 'products',
                            headers=json_header)
    products = json.loads(response.text)

    return products 


def get_bands(product):
    """
    Get a list of available bands for a given product.

    Parameters
    ----------
    product : str
        E.g. MYD09A1 - Terra + Aqua daily surface radiation

    Returns
    -------
    dict
        with available bands
    """
    request_string = modis_rest_api + f'{product}/bands'
    response = requests.get(request_string, headers=json_header)
    bands = json.loads(response.text)

    return bands


def get_dates(product, longitude, latitude):
    """
    Get dates of available data for a given product.

    Parameters
    ----------
    product : str
        Product code e.g. MYDO9A1
    latitude : str
        centre latitude coordinate for query area
    longitude : float 
        centre longitude coordinate for query area

    Returns
    -------
    dict
        with available dates
    """
    request_string = modis_rest_api + f'{product}/dates?'
    request_string = request_string + f'latitude={latitude}&'
    request_string = request_string + f'longitude={longitude}'
    response = requests.get(request_string, headers=json_header)
    dates = json.loads(response.text)

    return dates 

if __name__ == '__main__':
    search_term = {'product': 'MYD09A1',
                   'latitude': 39.56499,
                   'longitude': -121.55527,
                   'band' : 'sur_refl_b06',
                   'startDate': 'A2003101',
                   'endDate': 'A2003111',
                   'kmAboveBelow': 1,
                   'kmLeftRight': 1}

    pp.pprint(get_data(search_term))
