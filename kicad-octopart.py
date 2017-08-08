
import json
import urllib

url = "http://octopart.com/api/v3/parts/search"

# NOTE: Use your API key here (https://octopart.com/api/register) kjd
url += "?apikey=70358d97"

args = [
    ('q', '49.9K 0603'),
    ('start', 0),
    ('limit', 100),
    ('pretty_print','true'),
    ('include[]','descriptions'),
    ('include[]','datasheets'),
    ('include[]','specs'),
    #    ('filter[fields][offers.seller.name][]','Digi-Key')
   ]

url += '&' + urllib.urlencode(args)

data = urllib.urlopen(url).read()
search_response = json.loads(data)

# print number of hits
print search_response['hits']

print "Manufacturer\t\t\tManufacturer PN\t\t\tSupplier\t\tSupplier PN\t\tDescription"
print "------------\t\t\t---------------\t\t\t--------\t\t-----------\t\t-----------"
# print results
found=[]
item={}
for result in search_response['results']:
    part = result['item']
    for offer in part['offers']:

        desc_found = 0
        for description in part['descriptions']:
            vendor_desc = description['attribution']['sources']
            vendor = vendor_desc[0]['name']
            d=''
            if (vendor==offer['seller']['name']):
                d=description['value']
#                print "%s\t\t\t%s\t\t\t" % (part['brand']['name'], part['mpn']),
#                print "%s\t\t%s\t\t" % (offer['seller']['name'], offer['sku']),
#                print "%s" % description['value']
                break
#        item['MFG']=part['brand']['name']
#        item['MPN']=part['mpn']
#        item['SUP']=offer['seller']['name']
#        item['SPN']=offer['sku']
        found.append({'Manufacturer':part['brand']['name'],
                      'Manufacturer_PN':part['mpn'],
                      'Supplier':offer['seller']['name'],
                      'Supplier_PN':offer['sku'],
                      'Description':d,
                      'In_stock_qty':offer['in_stock_quantity'],
                      'MOQ':offer['moq'],
                      'Prices':offer['prices']
                      })
#            print "%s\t\t\t%s\t\t\t" % (part['brand']['name'], part['mpn']),
#            print "%s\t\t%s\t\t" % (offer['seller']['name'], offer['sku'])


queries = []
results = []
'''
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

