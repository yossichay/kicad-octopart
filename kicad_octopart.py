
import json
import urllib
from collections import OrderedDict

class octopart_lookup(object):


    _field_map = [
        'Manufacturer',
        'Manufacturer PN',
        'Description',
        'Supplier',
        'Supplier PN',
        'Qty In Stock',
        'MOQ',
        'Datasheet'
        ]

    def __init__(self):
        self._api_key = "?apikey=70358d97"
        self._url = "http://octopart.com/api/v3/parts/search"
        self._args = []
        self._hits = 0

    def get_fields(self):
        return self._field_map

    def get_hits(self):
        return self._hits

    def format_prices(self, price):
        pr = OrderedDict()
        pr['qty 1-9'] = 0
        pr['qty 10-99'] = 0
        pr['qty 100-499'] = 0
        pr['qty 500-999'] = 0
        pr['qty 1000-4999'] = 0
        pr['qty 5000-'] = 0

        if 'USD' not in price:
            return pr

        for price_break in price['USD']:
            try:
                prc = float(price_break[1])
            except:
                prc = price_break[1]

            try:
                qty = int(price_break[0])
                if (qty >= 1 and qty < 10):
                    pr['qty 1-9'] = prc
                    continue
                if (qty >= 10 and qty < 100):
                    pr['qty 10-99'] = prc
                    continue
                if (qty >= 100 and qty < 500):
                    pr['qty 100-499'] = prc
                    continue
                if (qty >= 500 and qty < 1000):
                    pr['qty 500-999'] = prc
                    continue
                if (qty >= 1000 and qty < 5000):
                    pr['qty 1000-4999'] = prc
                    continue
                if (qty >= 5000):
                    pr['qty 5000-'] = prc
                    continue
            except:
                qty = price_break[0]
        return pr

    def parts_search(self, ct):

        self._args = [
            ('q', '{}'.format(ct.value)),
            ('start', 0),
            ('limit', 100),
            ('pretty_print','true'),
            ('include[]','descriptions'),
            ('include[]','datasheets'),
            ('include[]','specs'),
            ]
        search_url = self._url + self._api_key + '&' + urllib.urlencode(self._args)
        data = urllib.urlopen(search_url).read()
        search_response = json.loads(data)

        self._hits = search_response['hits']

        found=[]
        item={}
        for result in search_response['results']:
            part = result['item']
            for ds in part['datasheets']:
                att = ds['attribution']
                '''
                for src in att['sources']:
                    if not ds['metadata'] == None:
                        print "%s\t%s\t%s\t%s" % (ds['metadata']['last_updated'], ds['metadata']['date_created'], src['name'], ds['url'])
                        '''
            for offer in part['offers']:

                # Find the description that originated from the seller
                for description in part['descriptions']:
                    vendor_desc = description['attribution']['sources']
                    vendor = vendor_desc[0]['name']
                    d=''
                    if (vendor==offer['seller']['name']):
                        d=description['value']
                        d=d[:75]
                        break

                # Find the datasheet that originated from the seller
                for datasheet in part['datasheets']:
                    vendor_desc = datasheet['attribution']['sources']
                    try:
                        vendor = vendor_desc[0]['name']
                    except:
                        continue
                    dsht=''
                    if (vendor==offer['seller']['name']):
                        dsht=datasheet['url']
                        break
                prices_dict = self.format_prices(offer['prices'])
                fn = OrderedDict()
                fn[self._field_map[0]] = part['brand']['name']
                fn[self._field_map[1]] = part['mpn']
                fn[self._field_map[3]] = offer['seller']['name']
                fn[self._field_map[4]] = offer['sku']
                fn[self._field_map[2]] = d
                fn[self._field_map[5]] = offer['in_stock_quantity']
                fn[self._field_map[6]] = offer['moq']
                for q, p in prices_dict.items():
                    fn[q] = p
                fn[self._field_map[7]] = dsht

                found.append(fn)

        return found
