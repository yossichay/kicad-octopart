
import json
import urllib
from collections import OrderedDict
import wx
from filter_dlg import FilterDialog

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

    _filter_map = [
        'specs.packaging.value',
        'specs.contact_style.value',
        'specs.lifecycle_status.value',
        'specs.mounting_style.value',
        'specs.capacitance_tolerance.value',
        'specs.output_capacitor_type.value',
        'specs.part_family.value',
        'specs.inductance_tolerance.value',
        'specs.termination_style.value',
        'specs.color.value',
        'specs.contact_plating.value',
        'specs.china_rohs.value',
        'specs.conductor_material.value',
        'specs.resistance_tolerance.value',
        'specs.shielding.value',
        'specs.material.value',
        'specs.gender.value',
        'specs.rohs_status.value',
        'specs.contacts_type.value',
        'specs.logic_type.value',
        'specs.lead_free_status.value',
        'specs.contact_material.value',
        'specs.case_package.value',
        'specs.housing_material.value',
        'specs.oscillator_type.value',
        'specs.output_type.value',
        'specs.dielectric_material.value'
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


    def find_categories(self, pn):

        self._args = [
            ('q', '{}'.format(pn)),
            #('start', 0),
            #('limit', 100),
            #('pretty_print','true'),
            #('include[]','descriptions'),
            #('include[]','datasheets'),
            ('include[]', 'category_uids'),
            #('spec_drilldown[include]', 'true'),
            #('include[]','specs'),
            #('include[]','spec_drilldown'),
            ]
        search_url = self._url + self._api_key + '&' + urllib.urlencode(self._args)
        data = urllib.urlopen(search_url).read()
        search_response = json.loads(data)

        num_results = self._hits = search_response['hits']

        num_results_threshold = num_results / 100

        facets = []
        stats = []

        metadata = search_response['spec_metadata']


        # Find the possible categories for the part

        cat_uids = []
        args = []
        for result in search_response['results']:
            for cat_uid in result['item']['category_uids']:
                if cat_uid not in cat_uids:
                    cat_uids.append(cat_uid)
                    args.append(('uid[]', cat_uid))

        url = 'http://octopart.com/api/v3/categories/get_multi'
        url += self._api_key
        url += "&" + urllib.urlencode(args)

        data = urllib.urlopen(url).read()
        server_response = json.loads(data)

        categories = []
        category_names = []
        index = 0
        for cat in server_response.iteritems():
            if len(cat[1]['children_uids']) == 0:
                #c['uid'] = cat[0]
                #c['name'] = cat[1]['name']
                categories.append({'name':cat[1]['name'], 'uid': cat[0]})
                category_names.append(cat[1]['name'])


        dlg = wx.SingleChoiceDialog(None, "Select Category", "wx.MultiChoiceDialog", category_names)


        dlg.ShowModal()
        cat_name = dlg.GetStringSelection()
        for c in categories:
            if c['name'] == cat_name:
                cat_uids = c['uid']
                break

        return cat_uid


    def parts_search(self, pn, cat_uid):
    #def parts_search(self, pn):

        self._args = [
            ('q', '{}'.format(pn)),
            #('start', 0),
            ('limit', 100),
            ('pretty_print','true'),
            ('include[]','descriptions'),
            ('include[]','datasheets'),
            ('include[]', 'category_uids'),
            ('spec_drilldown[include]', 'true'),
            #('spec_drilldown[limit]', 2),
            ('include[]','specs'),
            ('filter[fields][category_uids][]', cat_uid)
            #('include[]','spec_drilldown'),
            ]
        search_url = self._url + self._api_key + '&' + urllib.urlencode(self._args)
        data = urllib.urlopen(search_url).read()
        search_response = json.loads(data)

        num_results = self._hits = search_response['hits']

        #num_results_threshold = 1
        num_results_threshold = num_results / 100 + 1

        facets = []
        stats = []

        metadata = search_response['spec_metadata']

        # Check drilldown Rank

        drilldown = []
        dr = {}
        #for f in search_response['facet_results']['fields'].iteritems():

        #F = open("facets.txt", "w")

        for facet_result_field in search_response['facet_results']['fields'].iteritems():
            # if len(facet_result_field[1]['facets']) > 1:
            #if True:

            if facet_result_field[0] in self._filter_map:

                count = 0
                for f in facet_result_field[1]['facets']:
                    count += f['count']
                # Don't use items with qty < 1% of all results
                if count < num_results_threshold:
                    continue
                fn = facet_result_field[0].split(".")[1]

                #dr['name'] = fn
                #dr['rank'] = facet_result_field[1]['spec_drilldown_rank']
                #dr['count'] = count
                #drilldown.append({'name':fn, 'rank':facet_result_field[1]['spec_drilldown_rank'], 'count':count})
                #F.write(fn)
                #print("'%s'," % facet_result_field[0])
                if metadata[fn]['unit'] != None:
                    facet_result_field[1]['units_name'] = metadata[fn]['unit']['name']
                    facet_result_field[1]['units_symbol'] = metadata[fn]['unit']['symbol']
                else:
                    facet_result_field[1]['units_name'] = ''
                    facet_result_field[1]['units_symbol'] = ''
                facet_result_field[1]['facet_name'] = metadata[fn]['name']
                facet_result_field[1]['datatype'] = metadata[fn]['datatype']
                facets.append(facet_result_field)
        #F.close()

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

        self._fd = FilterDialog(None, -1, num_results, facets, stats)
        self._fd.ShowModal()




        found=[]
        if self._hits < 1:
            return found


        item={}
        num_results = 0
        for result in search_response['results']:
            part = result['item']

            # specs = part['specs']
            # print specs.keys()

            d = result['snippet']
            # for ds in part['datasheets']:
                # att = ds['attribution']

            for offer in part['offers']:
                '''
                # Find the description that originated from the seller
                d = ''
                for description in part['descriptions']:
                    #vendor_desc = description['attribution']['sources']
                    #vendor = vendor_desc[0]                                                                                                                                                                    ['name']
                    vendor = description['attribution']['sources'][0]['name']
                    if (vendor==offer['seller']['name']):
                        d=description['value']
                        d=d[:75]
                        break
            '''
            # Find the datasheet that originated from the seller
                dsht = ''
                mfg = part['brand']['name']

                for datasheet in part['datasheets']:
                    try:
                        src = datasheet['attribution']['sources'][0]['name']
                    except:
                        continue
                    if (mfg==src):
                        dsht = datasheet['url']
                        break
                    '''
                    vendor_desc = datasheet['attribution']['sources']
                    try:
                        vendor = vendor_desc[0]['name']
                    except:
                        continue
                    if (vendor==offer['seller']['name']):
                        dsht=datasheet['url']
                        break
                    '''
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
                num_results = num_results + 1

        return found
