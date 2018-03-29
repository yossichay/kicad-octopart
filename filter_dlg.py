import wx


class FilterDialog(wx.Dialog):
    def __init__(self, parent, id, hits, facets, stats):
        #super(FilterDialog, self).__init__(parent, id, wx.DefaultPosition)
        wx.Dialog.__init__(self, parent, -1, title="Filter", size = (1000, 500), style = wx.CAPTION | wx.CLOSE_BOX | wx.RESIZE_BORDER)
        #wx.Dialog.__init__(self, parent, -1, title="Filter", style = wx.CAPTION | wx.CLOSE_BOX | wx.RESIZE_BORDER)

        vbox = wx.BoxSizer(wx.VERTICAL)
        self.parent = parent

        stats_grid = wx.FlexGridSizer(0, 6, 3, 15)
        facets_box = wx.BoxSizer(wx.HORIZONTAL)

        # Create fooprint selector box
        fbox =[]
        flabel = []
        fp_list = []
        n = 0
        font_static = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        font_lb = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        for n in range(0, len(facets)):
        #for facet in facets:
            facet = facets[n]
            fbox.append(wx.BoxSizer(wx.VERTICAL))
            flist = []
            flist_name = facet[1]['facet_name']
            fstatic = wx.StaticText(self, -1, flist_name, style=wx.ALIGN_CENTER_HORIZONTAL)
            #self._static_font = fstatic.GetDefaultCellFont().Smaller().Smaller()
            fstatic.SetFont(font_static)
            flabel.append(fstatic)
            flist_box = wx.ListBox(self, 330+n, style=wx.LB_MULTIPLE  | wx.LB_SORT)
            flist_box.SetFont(font_lb)
            fp_list.append(flist_box)

            fbox[n].Add(flabel[n], 0, wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND)
            fbox[n].Add(fp_list[n], 1, wx.EXPAND)
            facets_box.Add(fbox[n], 1, wx.EXPAND)
            for f in facet[1]['facets']:
                s = "%s (%d)" % (f['value'], f['count'])
                flist.append(s)
                fp_list[n].Append(s)
                #flist.append(f['value'])
                #fp_list[n].Append(f['value'])
        #n += 1

        slist = []
        for n in range(0, len(stats)):
            stat = stats[n]
            slist_name = stat[1]['stat_name']
            slist.append(wx.TextCtrl(self, 304, ''))
            stats_grid.Add(wx.StaticText(self, -1, slist_name), 0, wx.EXPAND)
            stats_grid.Add(slist[n])
            #stats_grid.Add(wx.StaticText(self, -1, stat[1]['units_name']), 0, wx.EXPAND)
            stats_grid.Add(wx.StaticText(self, -1, stat[1]['units_symbol']), 0, wx.EXPAND)
            stats_grid.Add(wx.StaticText(self, -1, stat[1]['min']), 0, wx.EXPAND)
            stats_grid.Add(wx.StaticText(self, -1, stat[1]['max']), 0, wx.EXPAND)
            stats_grid.Add(wx.StaticText(self, -1, str(stat[1]['count'])), 0, wx.EXPAND)

        vbox.Add(facets_box, 3, wx.EXPAND | wx.ALL, 3)
        vbox.Add(stats_grid, 1, wx.EXPAND | wx.ALL, 3)
        #facets_box.Fit(self)
        self.SetSizer(vbox)
        #stats_grid.Fit(self)
        #vbox.Fit(self)
        #self.DoLayoutAdaptation()

