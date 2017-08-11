
import json
import urllib


class octopart_lookup(object):


    _field_map = [
        'Manufacturer',
        'Manufacturer PN',
        'Description',
        'Supplier',
        'Supplier PN',
        'Qty In Stock',
        'MOQ',
        'Prices',
        'Datasheet'
        ]
    '''
    _search_vendors [
        ''
    ]
    '''
    def __init__(self):
        self._api_key = "?apikey=70358d97"

    def get_fields(self):
        return self._field_map

    def get_hits(self):
        return self._hits

    def parts_search(self, ct):
        self._url = "http://octopart.com/api/v3/parts/search"
        self._args = [
            ('q', '{}'.format(ct.value)),
            ('start', 0),
            ('limit', 100),
            ('pretty_print','true'),
            ('include[]','descriptions'),
            ('include[]','datasheets'),
            ('include[]','specs'),
        #    ('filter[fields][offers.seller.name][]','Digi-Key')
            ]



 #   url += '&' + urllib.urlencode(args)
        search_url = self._url + self._api_key + '&' + urllib.urlencode(self._args)
        data = urllib.urlopen(search_url).read()
        search_response = json.loads(data)

# print number of hits
        self._hits = search_response['hits']

#   print "Manufacturer\t\t\tManufacturer PN\t\t\tSupplier\t\tSupplier PN\t\tDescription"
#   print "------------\t\t\t---------------\t\t\t--------\t\t-----------\t\t-----------"
# print results
        found=[]
        item={}
        for result in search_response['results']:
            part = result['item']
            for ds in part['datasheets']:
                att = ds['attribution']
                for src in att['sources']:
                    if not ds['metadata'] == None:
                        print "%s\t%s\t%s\t%s" % (ds['metadata']['last_updated'], ds['metadata']['date_created'], src['name'], ds['url'])
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
                    vendor = vendor_desc[0]['name']
                    dsht=''
                    if (vendor==offer['seller']['name']):
                        dsht=datasheet['url']
                        break

                found.append({self._field_map[0]:part['brand']['name'],
                              self._field_map[1]:part['mpn'],
                              self._field_map[3]:offer['seller']['name'],
                              self._field_map[4]:offer['sku'],
                              self._field_map[2]:d,
                              self._field_map[5]:offer['in_stock_quantity'],
                              self._field_map[6]:offer['moq'],
                              self._field_map[7]:offer['prices'],
                              self._field_map[8]:dsht
                            })

        return found

'''
queries = []
results = []

queries.append({'mpn': 'TDA7498LTR',
                'seller': '*'})
url = 'http://octopart.com/api/v3/parts/match?queries=%s' \
      % urllib.quote(json.dumps(queries))
url += '&apikey=70358d97'
data = urllib.urlopen(url).read()
response = json.loads(data)
# Record results for analysis
results.extend(response['results'])
'''

