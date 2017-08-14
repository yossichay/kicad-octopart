import wx
import wx.grid as gridlib
from wx.lib import sheet
from operator import itemgetter
import webbrowser

TBFLAGS = ( wx.TB_HORIZONTAL
            | wx.NO_BORDER
            | wx.TB_FLAT
            #| wx.TB_TEXT
            #| wx.TB_HORZ_LAYOUT
            )


class SpreadSheet(wx.Frame):
    def __init__(self, parent, up):
        """Constructor"""
        wx.Frame.__init__(self, parent, -1, title="Parts Found", size = (550, 500))
        self._parent=parent
        self._fields = up[0].keys()
        self._fields.remove('Datasheet')    # We don't need it on the spreadsheet
        self.selected_part = {}
        self._up = []

        self._pref_vendors = ['Digi-Key', 'Mouser', 'Arrow', 'Avnet', 'Newark']
        vendors = self.GetVendorList(up)
        _pref_vend_ind=[]
        for v in self._pref_vendors:
            if v in vendors:
                _pref_vend_ind.append(vendors.index(v))
        dlg = wx.MultiChoiceDialog(self,
                                   "Select Vendors",
                                   "wx.MultiChoiceDialog", vendors)

        dlg.SetSelections(_pref_vend_ind)
        if (dlg.ShowModal() == wx.ID_OK):
            selections = dlg.GetSelections()
            self._selected_vendors = [vendors[x] for x in selections]
            #self.log.write("Selections: %s -> %s\n" % (selections, strings))

        dlg.Destroy()

        for p in up:
            if p['Supplier'] in self._selected_vendors:
                self._up.append(p)


        manufacturers = self.GetManufacturerList(self._up)

        toolbar = self.CreateToolBar(TBFLAGS)
        self.CreateStatusBar()

        cbID = wx.NewId()

        vnd = wx.ComboBox(toolbar, cbID, choices=vendors, size=(100, -1), style=wx.CB_DROPDOWN)
        mfgs = wx.ComboBox(toolbar, cbID, choices=manufacturers, size=(100, -1), style=wx.CB_DROPDOWN)
        toolbar.AddControl(vnd)
        toolbar.AddControl(mfgs)

        toolbar.Realize()

        self._sheet = wx.lib.sheet.CSheet(self)
        self._def_cell_font = self._sheet.GetDefaultCellFont().Smaller().Smaller().Smaller()
        self._sheet.row = self._sheet.col = 0
        self._sheet.SetDefaultCellFont(self._def_cell_font)
        self._sheet.SetNumberRows(55)
        self._sheet.SetNumberCols(25)
        self._sheet.EnableEditing(False)
        self._sheet.EnableCellEditControl(False)
        self._sheet.SetDefaultRenderer(wx.grid.GridCellAutoWrapStringRenderer())

        for i in range(55):
            self._sheet.SetRowSize(i, 20)

        i = 0
        for label in self._fields:
            self._sheet.SetColLabelValue(i, label)
            i += 1
        self.Bind(gridlib.EVT_GRID_COL_SORT, self.OnGridColSort)
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_DCLICK, self.OnGridSelectRow)
        self.Bind(gridlib.EVT_GRID_CELL_LEFT_CLICK, self.OnGridCellLeftClick)


        self.populate()
        self._sheet.AutoSize()

    def GetVendorList(self, up):
        vendors = []
        for part in up:
            if part['Supplier'] not in vendors:
                vendors.append(part['Supplier'])
        return vendors

    def GetManufacturerList(self, up):
        manufacturers = []
        for part in up:
            if part['Manufacturer'] not in manufacturers:
                manufacturers.append(part['Manufacturer'])
        return manufacturers


    def OnGridColSort(self, evt):
        self._up = sorted(self._up, key=itemgetter(self._fields[evt.GetCol()]), reverse=False)
        self.populate()

    def OnGridSelectRow(self, evt):
        comp = self._up[evt.GetRow()]
        self._parent.ds_text.SetValue(comp['Datasheet'])
        self._parent.de_text.SetValue(comp['Description'])
        self._parent.mfr_text.SetValue(comp['Manufacturer'])
        self._parent.mpn_text.SetValue(comp['Manufacturer PN'])
        self._parent.spr_text.SetValue(comp['Supplier'])
        self._parent.spn_text.SetValue(comp['Supplier PN'])

        self.Close()

    def OnGridCellLeftClick(self, evt):
        _col = evt.GetCol()
        _row = evt.GetRow()
        if self._fields[_col] != 'Manufacturer PN':
            return
        else:
            if (self._up[_row]['Datasheet'] != ''):
                webbrowser.open(self._up[_row]['Datasheet'])


    def populate(self):
        k = 0

        mpn_column = self._fields.index("Manufacturer PN")
        default_font = self._sheet.GetCellFont(0,0)
        hyperlink_font = default_font
        hyperlink_font.MakeItalic()
        hyperlink_font.MakeUnderlined()
        hl_color = wx.Colour(0,0,255)

        for part in self._up:
            for col in range(len(self._fields)):
                v = part[self._fields[col]]
                if isinstance(v, basestring):
                    self._sheet.SetCellValue(k, col, v)
                else:
                    self._sheet.SetCellValue(k, col, str(v))
            if (part['Datasheet'] != ''):
                self._sheet.SetCellFont(k, mpn_column, hyperlink_font)
                self._sheet.SetCellTextColour(k, mpn_column, hl_color)

            self._sheet.AppendRows(1)
            k = k + 1

        self._sheet.AutoSizeColumns()

