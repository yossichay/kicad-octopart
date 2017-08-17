import json
import urllib
from filter_dlg import FilterDialog

url = "http://octopart.com/api/v3/parts/search"
url += "?apikey=70358d97"

generic_fileds = ['case_package', '']

specs_fields = {
    'R' : [''],
    'C' : [
        'Capacitance',
        'capacitance_tolerance',
        'dielectric_characteristic',
        'dielectric_material',
        'lifecycle_status',
        'mounting_style',
        'packaging',
        'rohs_status',

    ]
}

args = [
    ('q', 'RES 10K'),
    ('start', 0),
    ('limit', 10),
    ('pretty_print','true'),
    ('include[]', 'specs'),
    #('include[]', 'datasheets'),
    ('spec_drilldown[include]', 'true'),
]

url += '&' + urllib.urlencode(args)

data = urllib.urlopen(url).read()
search_response = json.loads(data)

# print number of hits
num_results = search_response['hits']
print 'Number of results: %d' % num_results

num_results_threshold = num_results/100

facets = []
stats = []

metadata = search_response['spec_metadata']

for facet_result_field in search_response['facet_results']['fields'].iteritems():
    if len(facet_result_field[1]['facets']) > 1:
        fn = facet_result_field[0].split(".")[1]
        if metadata[fn]['unit'] != None:
            facet_result_field[1]['units_name'] = metadata[fn]['unit']['name']
            facet_result_field[1]['units_symbol'] = metadata[fn]['unit']['symbol']
        else:
            facet_result_field[1]['units_name'] = ''
            facet_result_field[1]['units_symbol'] = ''
        facet_result_field[1]['facet_name'] = metadata[fn]['name']
        facet_result_field[1]['datatype'] = metadata[fn]['datatype']
        facets.append(facet_result_field)

for stat_result in search_response['stats_results'].iteritems():
    if stat_result[1]['count'] > num_results_threshold:

        fn = stat_result[0].split(".")[1]
        if metadata[fn]['unit'] != None:
            stat_result[1]['units_name'] = metadata[fn]['unit']['name']
            stat_result[1]['units_symbol'] = metadata[fn]['unit']['symbol']
        else:
            stat_result[1]['units_name'] = ''
            stat_result[1]['units_symbol'] = ''
        stat_result[1]['stat_name'] = metadata[fn]['name']
        stat_result[1]['datatype'] = metadata[fn]['datatype']
        stats.append(stat_result)

FilterDialog(None, -1, num_results, facets, stats)





# print results
for result in search_response['results']:
   part = result['item']

   # print matched part
   print "%s - %s" % (part['brand']['name'], part['mpn'])