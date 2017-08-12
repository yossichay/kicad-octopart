#!/usr/bin/env pythonw
import os
import csv
import shutil

import wx
import wx.grid as gridlib
from wx.lib import sheet
import sch, datastore
import kicad_helpers as kch
import kicad_octopart as octo
from operator import itemgetter

class DBPartSelectorDialog(wx.Dialog):
    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title)
        self.selection_idx = None
        self.selection_text = None

        vbox = wx.BoxSizer(wx.VERTICAL)
        stline = wx.StaticText(self, 11, 'Please select from the following components')
        vbox.Add(stline, 0, wx.ALIGN_CENTER|wx.TOP)
        self.comp_list = wx.ListBox(self, 331, style=wx.LB_SINGLE)

        vbox.Add(self.comp_list, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND)
        self.SetSizer(vbox)
        self.comp_list.Bind(wx.EVT_LISTBOX, self.on_selection, id=wx.ID_ANY)

    def on_selection(self, event):
        self.selection_text = self.comp_list.GetStringSelection()
        self.selection_idx = self.comp_list.GetSelection()
        self.Close()

    def attach_data(self, data):
        map(self.comp_list.Append, data)


class ComponentTypeView(wx.Panel):
    def __init__(self, parent, id):
        super(ComponentTypeView, self).__init__(parent, id, wx.DefaultPosition)

        vbox = wx.BoxSizer(wx.VERTICAL)
        self.parent = parent
        self._current_type = None
        self.grid = wx.GridSizer(0, 2, 3, 3)

        self.lookup_button = wx.Button(self, 310, 'Part Lookup')
        self.save_button = wx.Button(self, 311, 'Save Part to Datastore')

        self.qty_text = wx.TextCtrl(self, 301, '', style=wx.TE_READONLY)
        self.refs_text = wx.TextCtrl(self, 302, '', style=wx.TE_READONLY)
        self.fp_text = wx.TextCtrl(self, 303, '', style=wx.TE_READONLY)
        self.value_text = wx.TextCtrl(self, 304, '')
        self.ds_text = wx.TextCtrl(self, 305, '')
        self.mfr_text = wx.TextCtrl(self, 306, '')
        self.mpn_text = wx.TextCtrl(self, 307, '')
        self.spr_text = wx.TextCtrl(self, 308, '')
        self.spn_text = wx.TextCtrl(self, 309, '')

        # Bind the save and lookup component buttons
        self.save_button.Bind(wx.EVT_BUTTON, self.on_save_to_datastore, id=wx.ID_ANY)
        self.lookup_button.Bind(wx.EVT_BUTTON, self.on_lookup_component, id=wx.ID_ANY)

        # Set the background color of the read only controls to
        # slightly darker to differentiate them
        for ctrl in (self.qty_text, self.refs_text, self.fp_text):
            ctrl.SetBackgroundColour(wx.ColourDatabase().Find('Light Grey'))

        self._populate_grid()

        # Create fooprint selector box
        fpbox = wx.BoxSizer(wx.VERTICAL)

        fp_label = wx.StaticText(self, -1, 'Footprints', style=wx.ALIGN_CENTER_HORIZONTAL)
        self.fp_list = wx.ListBox(self, 330, style=wx.LB_SINGLE)

        fpbox.Add(fp_label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND)
        fpbox.Add(self.fp_list, 1, wx.EXPAND)

        self.fp_list.Bind(wx.EVT_LISTBOX, self.on_fp_list, id=wx.ID_ANY)

        # Create Component selector box
        compbox = wx.BoxSizer(wx.VERTICAL)

        comp_label = wx.StaticText(self, -1, 'Componenents', style=wx.ALIGN_CENTER_HORIZONTAL)
        self.comp_list = wx.ListBox(self, 331, style=wx.LB_SINGLE)

        compbox.Add(comp_label,  0, wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND)
        compbox.Add(self.comp_list, 1, wx.EXPAND)
        self.comp_list.Bind(wx.EVT_LISTBOX, self.on_comp_list, id=wx.ID_ANY)

        # Lay out the fpbox and compbox side by side
        selbox = wx.BoxSizer(wx.HORIZONTAL)

        selbox.Add(fpbox, 1, wx.EXPAND)
        selbox.Add(compbox, 1, wx.EXPAND)

        # Perform final layout
        vbox.Add(self.grid, 1, wx.EXPAND | wx.ALL, 3)
        vbox.Add(selbox, 3, wx.EXPAND | wx.ALL, 3)

        self.SetSizer(vbox)

    def _populate_grid(self):
        # Create text objects to be stored in grid

        # Create the component detail grid
        self.grid.AddMany([
            (wx.StaticText(self, -1, 'Quantity'), 0, wx.EXPAND),
            (self.qty_text, 0, wx.EXPAND),
            (wx.StaticText(self, -1, 'Refs'), 0, wx.EXPAND),
            (self.refs_text, 0, wx.EXPAND),
            (wx.StaticText(self, -1, 'Footprint'), 0, wx.EXPAND),
            (self.fp_text, 0, wx.EXPAND),
            (wx.StaticText(self, -1, 'Value'), 0, wx.EXPAND),
            (self.value_text, 0, wx.EXPAND),
            (wx.StaticText(self, -1, 'Datasheet'), 0, wx.EXPAND),
            (self.ds_text, 0, wx.EXPAND),
            (wx.StaticText(self, -1, 'Manufacturer'), 0, wx.EXPAND),
            (self.mfr_text, 0, wx.EXPAND),
            (wx.StaticText(self, -1, 'Manufacturer PN'), 0, wx.EXPAND),
            (self.mpn_text, 0, wx.EXPAND),
            (wx.StaticText(self, -1, 'Supplier'), 0, wx.EXPAND),
            (self.spr_text, 0, wx.EXPAND),
            (wx.StaticText(self, -1, 'Supplier PN'), 0, wx.EXPAND),
            (self.spn_text, 0, wx.EXPAND),
            (self.lookup_button, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (self.save_button, 0, wx.ALIGN_CENTER_HORIZONTAL),
        ])

    def save_component_type_changes(self):

        if not self._current_type:
            return

        self._current_type.value = self.value_text.GetValue()
        self._current_type.datasheet = self.ds_text.GetValue()
        self._current_type.manufacturer = self.mfr_text.GetValue()
        self._current_type.manufacturer_pn = self.mpn_text.GetValue()
        self._current_type.supplier = self.spr_text.GetValue()
        self._current_type.supplier_pn = self.spn_text.GetValue()




    def on_save_to_datastore(self, event):

        self.save_component_type_changes()
        if not self._current_type:
            return

        # TODO: I don't like parent walking...we should inject this
        # dependency somewhere
        self.parent.ds.update(self._current_type)

    def on_fp_list(self, event):
        self.save_component_type_changes()
        self.comp_list.Clear()
        self._current_type = None

        map(self.comp_list.Append,
            [x for x in sorted(set(self.type_data[self.fp_list.GetStringSelection()].keys()))])

    def on_comp_list(self, event):
        self.save_component_type_changes()
        fp = self.fp_list.GetStringSelection()
        ct = self.comp_list.GetStringSelection()

        comp = self.type_data[fp][ct]

        self.qty_text.SetValue(str(len(comp)))
        self.refs_text.SetValue(comp.refs)
        self.fp_text.SetValue(comp.footprint)
        self.value_text.SetValue(comp.value)
        self.ds_text.SetValue(comp.datasheet)
        self.mfr_text.SetValue(comp.manufacturer)
        self.mpn_text.SetValue(comp.manufacturer_pn)
        self.spr_text.SetValue(comp.supplier)
        self.spn_text.SetValue(comp.supplier_pn)

        self._current_type = comp

    def _reset(self):
        self.comp_list.Clear()
        self.fp_list.Clear()
        self._current_type = None

    def attach_data(self, type_data):
        self.type_data = type_data

        self._reset()

        map(self.fp_list.Append,
            [x for x in sorted(set(type_data.keys()))])

    def on_lookup_component(self, event):
        ct = self._current_type

        if not ct:
            return

        if not ct.has_valid_key_fields:
            raise Exception("Missing key fields (value / footprint)!")

        ol = octo.octopart_lookup()
        up = ol.parts_search(ct)
        hits = ol.get_hits()
        if hits < 1:
            dlg = wx.MessageDialog(self.parent,
                                   "Component does not exist in Octopart",
                                   "No Results Found",
                                   wx.OK | wx.ICON_INFORMATION)
        # self.fields = list(up[0].keys())
        self.fields = ol.get_fields()

        ss = SpreadSheet(self,  up)
        ss.Show(True)

        # fl = FiltersDialog(None, up)

'''        
class FilterDialog(wx.Frame):
    def __init__(self, parent, up):
        """Constructor"""
        wx.Frame.__init__(self, parent, -1, title="Filter")
        self.gr = SpreadSheetGrid(self, fields)
'''

class SelectionSheet(sheet.CSheet):
    def __init__(self, parent):
        sheet.CSheet.__init__(self, parent)
        self.row = self.col = 0
        self.SetNumberRows(55)
        self.SetNumberCols(25)

        for i in range(55):
            self.SetRowSize(i, 20)
    '''
    def OnGridSelectCell(self, event):
        self.row, self.col = event.GetRow(), event.GetCol()
        control = self.GetParent().GetParent().position
        value =  self.GetColLabelValue(self.col) + self.GetRowLabelValue(self.row)
        control.SetValue(value)
        event.Skip()
    '''

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
        self._fields = up[0].keys()
        self._up = up

        vendors = self.GetVendorList()
        manufacturers = self.GetManufacturerList()

        toolbar = self.CreateToolBar(TBFLAGS)
        self.CreateStatusBar()

        cbID = wx.NewId()

        vnd = wx.ComboBox(toolbar, cbID, choices=vendors, size=(100, -1), style=wx.CB_DROPDOWN)
        mfgs = wx.ComboBox(toolbar, cbID, choices=manufacturers, size=(100, -1), style=wx.CB_DROPDOWN)
        toolbar.AddControl(vnd)
        toolbar.AddControl(mfgs)

        toolbar.Realize()

        '''
        box = wx.BoxSizer(wx.VERTICAL)
        menuBar = wx.MenuBar()

        menu1 = wx.Menu()
        menuBar.Append(menu1, '&File')
        menu2 = wx.Menu()
        menuBar.Append(menu2, '&Edit')
        menu3 = wx.Menu()
        menuBar.Append(menu3, '&Edit')
        menu4 = wx.Menu()
        menuBar.Append(menu4, '&Insert')
        menu5 = wx.Menu()
        menuBar.Append(menu5, 'F&ormat')
        menu6 = wx.Menu()
        menuBar.Append(menu6, '&Tools')
        menu7 = wx.Menu()
        menuBar.Append(menu7, '&Data')
        menu8 = wx.Menu()
        menuBar.Append(menu8, '&Help')

        self.SetMenuBar(menuBar)
        '''

        self._sheet = wx.lib.sheet.CSheet(self)
        #sheet = SelectionSheet(self)
        self._sheet.row = self._sheet.col = 0
        self._sheet.SetNumberRows(55)
        self._sheet.SetNumberCols(25)

        for i in range(55):
            self._sheet.SetRowSize(i, 20)

        i = 0
        for label in self._fields:
            self._sheet.SetColLabelValue(i, label)
            i += 1
        self.Bind(gridlib.EVT_GRID_COL_SORT, self.OnGridColSort)
        self.populate()

        #box.Add(sheet, 1, wx.EXPAND)
        #box.RecalcSizes()
        #self.CreateStatusBar()
        '''
        client.SetSizer(box)

        #self.Centre()
        #self.Show(True)
        '''


        '''
        ss_grid = wx.BoxSizer(wx.VERTICAL)
        gl = gridlib.Grid.__init__(self, parent, -1)
        gl.CreateGrid(2, 8)
        gl.EnableEditing(False)
        gl.EnableCellEditControl(False)
        i = 0;
        for label in self._fields:
            gl.SetColLabelValue(i, label)
            i += 1

        # Bind Events
        self.gl.Bind(gridlib.EVT_GRID_COL_SORT, self.OnGridColSort)

        ss_grid.Add(gl, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND)
        '''
    def GetVendorList(self):
        vendors = []
        for part in self._up:
            if part['Supplier'] not in vendors:
                vendors.append(part['Supplier'])
        return vendors

    def GetManufacturerList(self):
        manufacturers = []
        for part in self._up:
            if part['Manufacturer'] not in manufacturers:
                manufacturers.append(part['Manufacturer'])
        return manufacturers


    def OnGridColSort(self, evt):
        # self.log.write("OnGridColSort: %s %s" % (evt.GetCol(), self.GetSortingColumn()))
        #self.SetSortingColumn(evt.GetCol())
        self._up = sorted(self._up, key=itemgetter(self._fields[evt.GetCol()]), reverse=False)
        self.populate()

    def populate(self):
        k = 0

        #self._up=up
        ds_column = self._fields.index("Datasheet")
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

            #self._sheet.HideCol(ds_column)


'''

class SpreadSheet(wx.Frame):
    def __init__(self, parent, fields):
        """Constructor"""
        wx.Frame.__init__(self, parent, -1, title="Parts Found")
        self.gr = SpreadSheetGrid(self, fields)

class SpreadSheetGrid(gridlib.Grid):
    def __init__(self, parent, fields):
        gridlib.Grid.__init__(self, parent, -1)
        self._fields = fields
        self._up = {}

        # self.gr = gridlib.Grid(panel)
        self.CreateGrid(2, 8)
        self.EnableEditing(False)
        self.EnableCellEditControl(False)
        i = 0;
        for label in self._fields:
            self.SetColLabelValue(i, label)
            i += 1

        # Bind Events
        self.Bind(gridlib.EVT_GRID_COL_SORT, self.OnGridColSort)


'''



class UniquePartSelectorDialog(wx.Dialog):
    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title)
        self.selection_idx = None
        self.selection_text = None

        vbox = wx.BoxSizer(wx.VERTICAL)
        stline = wx.StaticText(
            self,
            11,
            'Duplicate Component values found!'
            '\n\nPlease select which format to follow:')
        vbox.Add(stline, 0, wx.ALIGN_CENTER|wx.TOP)
        self.comp_list = wx.ListBox(self, 331, style=wx.LB_SINGLE)

        vbox.Add(self.comp_list, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND)
        self.SetSizer(vbox)
        self.comp_list.Bind(wx.EVT_LISTBOX_DCLICK, self.on_selection, id=wx.ID_ANY)

    def on_selection(self, event):
        self.selection_text = self.comp_list.GetStringSelection()
        self.selection_idx = self.comp_list.GetSelection()
        self.Close()

    def attach_data(self, data):
        map(self.comp_list.Append, data)

class MainFrame(wx.Frame):

    config_dir = os.path.join(
        os.path.expanduser("~"),
        '.kicadbom.d',
    )

    _legacy_dir = os.path.join(
        os.path.expanduser("~"),
        '.kicadbommgr.d',
    )
    config_file = os.path.join(
        config_dir,
        'KiCADbom.conf'
    )
    datastore_file = os.path.join(
        config_dir,
        'bommgr.db'
    )

    def __init__(self, parent, id, title):
        super(MainFrame, self).__init__(parent, id, title, wx.DefaultPosition, wx.Size(800, 600))

        self._load_config()

        self._create_menu()
        self._do_layout()
        self.Centre()

        self._reset()

        self.ds = datastore.Datastore(self.datastore_file)

    def _load_config(self):
        # Handle legacy file location
        if os.path.exists(self._legacy_dir):
            print "Migrating config from legacy location"
            shutil.move(self._legacy_dir, self.config_dir)

        # Create the kicad bom manager folder if it doesn't already exist
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

        self.filehistory = wx.FileHistory(8)
        self.config = wx.Config("KiCADbom",
                                localFilename=self.config_file,
                                style=wx.CONFIG_USE_LOCAL_FILE)
        self.filehistory.Load(self.config)

    def _do_layout(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.ctv = ComponentTypeView(self, -1)

        vbox.Add(self.ctv, 1, wx.EXPAND | wx.ALL, 3)

        self.SetSizer(vbox)

    def _create_menu(self):
        menubar = wx.MenuBar()
        file = wx.Menu()
        edit = wx.Menu()
        help = wx.Menu()

        file.Append(wx.ID_OPEN, '&Open', 'Open a schematic')
        file.Append(wx.ID_SAVE, '&Save', 'Save the schematic')
        file.AppendSeparator()
        file.Append(103, '&Export BOM as CSV', 'Export the BOM as CSV')
        file.AppendSeparator()

        # Create a new submenu for recent files
        recent = wx.Menu()

        file.AppendSubMenu(recent, 'Recent')
        self.filehistory.UseMenu(recent)
        self.filehistory.AddFilesToMenu()
        file.AppendSeparator()

        quit = wx.MenuItem(file, 105, '&Quit\tCtrl+Q', 'Quit the Application')
        file.AppendItem(quit)
        edit.Append(201, 'Consolidate Components', 'Consolidate duplicated components')
        menubar.Append(file, '&File')
        menubar.Append(edit, '&Edit')
        menubar.Append(help, '&Help')
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.on_quit, id=105)
        self.Bind(wx.EVT_MENU, self.on_open, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.on_consolidate, id=201)
        self.Bind(wx.EVT_MENU, self.on_export, id=103)
        self.Bind(wx.EVT_MENU, self.on_save, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU_RANGE, self.on_file_history,
                  id=wx.ID_FILE1, id2=wx.ID_FILE9)

    def _reset(self):
        self.schematics = {}
        self.component_type_map = {}

    def _consolidate(self):
        """
        Performs consolidation
        """
        uniq = {}
        dups = {}

        # Find all duplicated components and put them into a dups map
        for fp in self.component_type_map:
            for ct in self.component_type_map[fp]:
                cthsh = ct.upper().replace(' ', '')

                if cthsh in uniq:
                    if cthsh not in dups:
                        dups[cthsh] = [uniq[cthsh]]

                    dups[cthsh].append(self.component_type_map[fp][ct])
                else:
                    uniq[cthsh] = self.component_type_map[fp][ct]

        for d, cl in dups.items():

            _popup = UniquePartSelectorDialog(self,
                                              wx.ID_ANY,
                                              'Duplicate part value')

            _popup.attach_data([x.value for x in cl])
            _popup.ShowModal()

            # If the user didn't select anything, just move on
            if _popup.selection_idx is None:
                continue

            sel = cl.pop(_popup.selection_idx)

            for rem in cl:
                old_fp = rem.footprint
                old_val = rem.value

                # Set all relevant fields
                rem.value = sel.value
                rem.manufacturer = sel.manufacturer
                rem.manufacturer_pn = sel.manufacturer_pn
                rem.supplier_pn = sel.supplier_pn
                rem.supplier = sel.supplier

                print sel
                sel.extract_components(rem)
                del self.component_type_map[old_fp][old_val]

            self.ctv.attach_data(self.component_type_map)

            _popup.Destroy()


    def load(self, path):
        if len(path) == 0:
            return

        # remove old schematic information
        self._reset()

        base_dir = os.path.split(path)[0]
        top_sch = os.path.split(path)[-1]
        top_name = os.path.splitext(top_sch)[0]

        compmap = {}

        self.schematics[top_name] = (
            sch.Schematic(os.path.join(base_dir, top_sch))
        )

        # Recursively walks sheets to locate nested subschematics
        # TODO: re-work this to return values instead of passing them byref
        kch.walk_sheets(base_dir, self.schematics[top_name].sheets, self.schematics)

        for name, schematic in self.schematics.items():
            for _cbase in schematic.components:
                c = kch.ComponentWrapper(_cbase)

                # Skip virtual components (power, gnd, etc)
                if c.is_virtual:
                    continue

                # Skip anything that is missing either a value or a
                # footprint
                if not c.has_valid_key_fields:
                    continue

                c.add_bom_fields()

                if c.footprint not in self.component_type_map:
                    self.component_type_map[c.footprint] = {}

                if c.value not in self.component_type_map[c.footprint]:
                    self.component_type_map[c.footprint][c.value] = kch.ComponentTypeContainer()

                self.component_type_map[c.footprint][c.value].add(c)

        self.ctv.attach_data(self.component_type_map)
        self._current_type = None
        self.ctv.lookup_button.disabled = True
        self.ctv.save_button.disabled = True

    def on_consolidate(self, event):
        self._consolidate()


    def on_file_history(self, event):
        """
        Handles opening files from the recent file history
        """
        fileNum = event.GetId() - wx.ID_FILE1
        path = self.filehistory.GetHistoryFile(fileNum)
        self.filehistory.AddFileToHistory(path)  # move up the list
        self.load(path)

    def on_open(self, event):
        """
        Recursively loads a KiCad schematic and all subsheets
        """
        #self.save_component_type_changes()
        open_dialog = wx.FileDialog(self, "Open KiCad Schematic", "", "",
                                         "Kicad Schematics (*.sch)|*.sch",
                                         wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if open_dialog.ShowModal() == wx.ID_CANCEL:
            return

        # Load Chosen Schematic
        print "opening File:", open_dialog.GetPath()

        # Store the path to the file history
        self.filehistory.AddFileToHistory(open_dialog.GetPath())
        self.filehistory.Save(self.config)
        self.config.Flush()

        self.load(open_dialog.GetPath())

    def on_export(self, event):
        """
        Gets a file path via popup, then exports content
        """

        export_dialog = wx.FileDialog(self, "Export to CSV", "", "",
                                      "CSV Files (*.csv)|*.csv",
                                      wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)

        if export_dialog.ShowModal() == wx.ID_CANCEL:
            return


        base, ext = os.path.splitext(export_dialog.GetPath())

        if not ext:
            ext = '.csv'

        with open(base+ext, 'w') as csvfile:
            wrt = csv.writer(csvfile)

            wrt.writerow(['Refs', 'Value', 'Footprint',
                          'QTY', 'MFR', 'MPN', 'SPR', 'SPN'])

            for fp in sorted(self.component_type_map):
                for val in sorted(self.component_type_map[fp]):
                    ctcont = self.component_type_map[fp][val]
                    wrt.writerow([
                        ctcont.refs,
                        ctcont.value,
                        ctcont.footprint,
                        len(ctcont),
                        ctcont.manufacturer,
                        ctcont.manufacturer_pn,
                        ctcont.supplier,
                        ctcont.supplier_pn,
                    ])

    def on_quit(self, event):
        """
        Quits the application
        """
        self.ctv.save_component_type_changes()
        exit(0)

    def on_save(self, event):
        """
        Saves the schematics
        """
        self.ctv.save_component_type_changes()
        for name, schematic in self.schematics.items():
            schematic.save()


class KicadBomApp(wx.App):
    def OnInit(self):
        frame = MainFrame(None, -1, 'KiCAD BOM')
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

if __name__ == '__main__':
    KicadBomApp(0).MainLoop()
