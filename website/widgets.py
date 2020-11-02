# -*- coding: utf-8 -*-

from flask import request

from numpy import linspace, asarray, pi, greater
from scipy import argmax

from bokeh.embed import components
from bokeh.models.sources import AjaxDataSource
from bokeh.plotting import figure
from bokeh.models import Select, Button, HoverTool, LabelSet, ColumnDataSource, Div
from bokeh.models import CrosshairTool, TextInput, RadioButtonGroup, NumeralTickFormatter, PrintfTickFormatter
from bokeh.layouts import widgetbox, gridplot, row, column, layout
from bokeh.models.widgets import DataTable, TableColumn, CheckboxGroup, Slider

from bokeh.models.callbacks import CustomJS
from scipy.signal import argrelextrema

CANT_MARKERS = 4 # al modificar esto, modificar tambien CANT_MARKERS en checkbox_callback.js y graf_adapter.js

def ajax_getplot(x,y,y_bottom,ref_value): #fi,ff,y_bottom,ref_value,x,y):
    # En la ventana del plot
    graf = figure(
                    tools="save",
                    x_axis_label="Frequency [Hz]", y_axis_label='Power [dBm]',
                    width=700,height=400,
                    sizing_mode = 'stretch_width',
                    x_range=(x[0], x[-1]),
                    y_range=(float(y_bottom), float(ref_value))
                )
    graf.toolbar.logo = None
    graf.toolbar.active_drag = None
    graf.toolbar.active_scroll = None

    graf.yaxis.major_label_text_font_style  = 'bold'    
    graf.xaxis.major_label_text_font_style  = 'bold'
    graf.xaxis.axis_label_text_font_style   = 'bold'
    graf.yaxis.axis_label_text_font_style   = 'bold'  
    graf.xaxis[0].formatter.use_scientific  = True

    graf.xaxis[0].ticker.desired_num_ticks = 15
    graf.yaxis[0].ticker.desired_num_ticks = 10
    graf.ygrid.grid_line_alpha = 0.4
    graf.ygrid.grid_line_dash = [6, 4]
    graf.xgrid.grid_line_alpha = 0.4
    graf.xgrid.grid_line_dash = [6, 4]
    # graf.ygrid.minor_grid_line_alpha = 0.1
    # graf.ygrid.minor_grid_line_color = 'navy'
    # graf.xgrid.minor_grid_line_alpha = 0.1
    
    graf.background_fill_color = "black"
    graf.border_fill_color = "black"
    graf.border_fill_alpha = 0
    graf.xaxis.axis_line_color = "white"
    graf.yaxis.axis_line_color = "white"

    props = dict(line_width = 4, line_alpha = 0.7)

    # source for (marker_abs, markers [CANT_MARKERS])
    source_markers = ColumnDataSource (data = {})
    
    # source for table of graf's markers
    source_table = ColumnDataSource ()
    # strings for table of graf's markers
    source_table_share = ColumnDataSource () # only for share strings of table's rows between graf_adapter.js, checkbox_callback.js

#################################################################################################################################################################
    # # --------------------------------------------------------------------------------------

    # button_height   = 30
    # button_width    = 70
    #SLIDER_WIDTH    = 500 # px
    CHECKBOX_WIDTH  = 100

    # --------------------------------------------------------------------------------------
        
    if x!=0 and y!=0:
        max_abs_y = max(y)
        max_abs_x = argmax(y)
        #x_npa=asarray(x)
        y_npa = asarray(y)
        x_axis = linspace(x[0],x[-1],len(x))
    else:
        y_bottom=-100
        ref_value=-60
        y_npa=asarray([0, 0])
        x_axis = [0, 0]
        max_abs_y = 0
        max_abs_x = 0

#################################################################################################################################################################
    # Sliders de marcadores

    # solicitar frecuencias al analizador
    sliders = []
    if x [0] != x [-1]:
        step = (x [-1] - x [0]) / len (x)
        
        if step <= 0:
            step = 1

        init = (max_abs_x * step) + x [0]

        for i in range (0, CANT_MARKERS):
            sliders.append (Slider (start=x[0], end=x[-1], value=init, step=step, title="MARKER "+str(i+1)))

    else:
        for i in range (0, CANT_MARKERS):
            sliders.append (Slider (start=0, end=1, value=0, step=1, title="MARKER "+str(i+1)))


#################################################################################################################################################################
    # Tablas de configuracion (las de solo lectura)

    source_set_an   = ColumnDataSource ()
    source_set_gen  = ColumnDataSource ()
    source_set_powm = ColumnDataSource ()

#################################################################################################################################################################
    # preparo el marcador movil

    # ve posibilidad de agregar PointDrawTool de hovertools
    # http://docs.bokeh.org/en/1.0.0/docs/user_guide/tools.html#click-tap-tools

    graf.add_tools(HoverTool(
        tooltips=[
            ( 'frec', '@x{0,0} Hz'),
            ( 'amp',  '@y dBm' ), # use @{ } for field names with spaces
        ],
            point_policy='follow_mouse',
            mode='vline'
    ))

    with open("static/js/graf_adapter.js","r") as f:
        code = f.read()

    adapter = CustomJS (args = dict (
        graf                 = graf,
        sliders              = sliders,
        source_markers       = source_markers,
        source_table         = source_table,
        source_table_share   = source_table_share,
        source_set_an        = source_set_an,
        source_set_gen       = source_set_gen,
        source_set_powm      = source_set_powm), code = code)

    source = AjaxDataSource(data_url = request.url_root + 'data/',
                            polling_interval = 1000, mode = 'replace', adapter=adapter)

    source.data = dict(x = [], y = [], y_bottom = [], ref_value = [],
        start_freq = [], stop_freq = [])#, power = [] )
        # span = [], center_freq = [], demod_time = [], ref_level = [], # ANALIZADOR
        # lf_freq = [], lf_level = [], rf_freq = [], rf_level = [], fm_mod_freq = [], am_mod_freq = [],am_mod_index= [],fm_mod_index= [],pm_mod_index= [], power = []) # GENERADOR
    
    graf.line('x', 'y', source = source, line_color = "cyan")

    ###############################################################################

    # maximos relativos
    max_rel_x = argrelextrema(y_npa, greater) #dato pasado a numpy array

    ###############################################################################

    # datos para la tabla de datos
    info  = []
    value = []

    # tabla de datos
    source_table.data = dict(x_data=info,y_data=value)
    source_table_share.data = dict(x_data=info,y_data=value)
    #source_table = source
    columns =   [ 
                    TableColumn(field="x_data", title="Information"),
                    TableColumn(field="y_data", title="Value")
                ]

    data_table = DataTable(source=source_table, columns=columns, height=200, width=400)

###############################################################################
    set_div  = Div (text = "<b>Current Settings</b>")

    # tabla de valores seteados actualmente del analizador
    source_set_an.data = dict(
            configuration=[
                "X scale",
                "Y scale",
                "Start freq",
                "Stop freq",
                "Span",
                "Center freq",
                "Ref level",
                "Demod time",
                "Demod type",
                "Input att",
                "Resolution BW",
                "Scale div",
                "Avg state",
                "Avg times"
            ],
            value=[
                "LIN",
                "LOG",
                "0.0",
                "1.0",
                "1.0",
                "1.0",
                "0.0",
                "0.0",
                "FM",
                "10",
                "100000",
                "10.0",
                "WRITe",
                "1"
            ],
        )

    columns_set_an = [
            TableColumn(field="configuration", title="Analizer"),
            TableColumn(field="value", title="value"),
        ]
    info_table_an = DataTable(source=source_set_an, columns=columns_set_an,width=220, height=180)
        

    # tabla de valuees seteados actualmente en el generador
    source_set_gen.data = dict(
            configuration=[
                "LF state",
                "LF freq",
                "LF level",
                "LF waveform",
                "RF state",
                "RF freq",
                "RF level",
                "AM state",
                "AM source",
                "AM mod freq",
                "AM mod index",
                "AM waveform",
                "Modulation type",
                "Modulation state",
                "FM mod freq",
                "FM mod index",
                "FM waveform",
                "PM mod freq",
                "PM mod index",
                "PM waveform"
            ],
            value=[
                "OFF",
                "0.0",
                "0.0",
                "SINE",
                "0.0",
                "0.0",
                "0.0",
                "OFF",
                "INT",
                "0.0",
                "0.0",
                "SINE",
                "FM",
                "OFF",
                "0.0",
                "0.0",
                "SINE",
                "0.0",
                "0.0",
                "0.0"
            ],
        )

    columns_set_gen = [
            TableColumn(field="configuration", title="Generator"),
            TableColumn(field="value", title="value"),
        ]
    info_table_gen = DataTable(source=source_set_gen, columns=columns_set_gen,width=220, height=180)


    # tabla de valuees seteados actualmente en el generador
    source_set_powm.data = dict(
            configuration=["Duty cycle","Average"],
            value=["50","1"],
        )

    columns_set_powm = [
            TableColumn(field="configuration", title="Power meter"),
            TableColumn(field="value", title="value"),
        ]
    info_table_powm = DataTable(source=source_set_powm, columns=columns_set_powm, width=200, height=180)


    #source_table = source

    ###############################################################################
    ## cosas a graficar

    # source5 = ColumnDataSource(data=dict(x5=[x_axis[max_abs_x]], y5=[max_abs_y]))
    # source4 = ColumnDataSource(data=dict(x4=[x_axis[max_abs_x]], y4=[max_abs_y]))
    # source3 = ColumnDataSource(data=dict(x3=[x_axis[max_abs_x]], y3=[max_abs_y]))
    # source2 = ColumnDataSource(data=dict(x2=[x_axis[max_abs_x]], y2=[max_abs_y]))

    # source5 = ColumnDataSource(data=dict(x5=[], y5=[]))
    # source4 = ColumnDataSource(data=dict(x4=[], y4=[]))
    # source3 = ColumnDataSource(data=dict(x3=[], y3=[]))
    # source2 = ColumnDataSource(data=dict(x2=[], y2=[]))
    
    # marcadores moviles que arrancan en el absolute maximum
    # l5=graf.circle('x5', 'y5', source=source5, color="lawngreen", line_width=8, line_alpha=0.7 )
    # l4=graf.circle('x4', 'y4', source=source4, color="lime", line_width=8, line_alpha=0.7)
    # l3=graf.circle('x3', 'y3', source=source3, color="yellow", line_width=8, line_alpha=0.7)
    # l2=graf.circle('x2', 'y2', source=source2, color="blue", line_width=8, line_alpha=0.7)

    # custom markers
    #markers_rel_dict = {}
    markers = []
    colors = ["yellow", "red", "pink", "lime"]
    for i in range (0, CANT_MARKERS):
        x_label = 'x_mark_' + str (i + 1)
        y_label = 'y_mark_' + str (i + 1)
        source_markers.data [x_label] = [x_axis[max_abs_x]]
        source_markers.data [y_label] = [max_abs_y]
        markers.append (graf.circle (x_label, y_label, source = source_markers, color = colors [i], line_width = 8, line_alpha = 0.7))

    #l1=graf.circle(x_axis[max_rel_x[0]] , y_npa[max_rel_x[0]], color="yellowgreen", **props)

    # max abs marker
    source_markers.data ['x_abs'] = [x_axis [max_abs_x]]
    source_markers.data ['y_abs'] = [max_abs_y]
    marker_abs = graf.circle (x = 'x_abs', y = 'y_abs', source = source_markers, color = "red", line_width = 8, line_alpha = 0.7)

    #marker_abs=graf.circle(x_axis[max_abs_x],max_abs_y, color="green", **props)

    ###############################################################################
    # presentacion del maximo
    #maximo=str('%.2f' % max_abs_y)+"V @ "+str('%.2f' % x_axis[max_abs_x]+" rad")

    # presentacion de maximos relativos
    max_rel=["a" for i in range(len(max_rel_x[0]))]

    for i in range(len((max_rel_x[0]))):
        max_rel[i]=(str('%.2f' % y_npa[max_rel_x[0][i]])+"V @ "+str('%.2f' % x_axis[max_rel_x[0][i]]+" rad"))

    ###############################################################################
    # Sliders de marcadores
    
    #callback unico para todos los sliders
    with open("static/js/callback_sm.js","r") as f:
        callback_sm_code=f.read()

    callback_sm = CustomJS (args = dict (source_table = source_table, source = source, source_markers = source_markers,
                                    sliders = sliders, markers = markers,
                                    graf = graf, props = props), code = callback_sm_code)

    for i in range (0, CANT_MARKERS):   
        sliders [i].js_on_change ('value', callback_sm)


    ###############################################################################

    # Acciones relativas a los checkbox
    checkbox_labels = ["Max. Abs"]
    # checkbox_labels = ["Max. Abs", "Max. Rel"]
    checkbox_preset = CheckboxGroup (labels = checkbox_labels, active = [], width = CHECKBOX_WIDTH)

    checkbox_mark = CheckboxGroup(labels=["Mark 1", "Mark 2", "Mark 3", "Mark 4"], active=[], width=CHECKBOX_WIDTH)

    #checkbox.active=[] <- indica los índices de los elementos "activados" (para activar el 1: [1], para activar el 0 y el 3: [0 3])
    #checkbox.active=[]
    #checkbox.active[0]=False
    marker_abs.visible = False
    #checkbox.active[1]=False
    for i in range (0, CANT_MARKERS):
        markers [i].visible = False
        pass

    #checkbox_mark.active=[]
    #checkbox_mark.active[0]=False
    # marker[i].visible=False
    #checkbox_mark.active[1]=False
    # marker[i].visible=False
    #checkbox_mark.active[2]=False
    # marker[i].visible=False
    #checkbox_mark.active[3]=False
    # marker[i].visible=False
    ##---------------------------------------------------------------------------##
    with open("static/js/checkbox_callback.js","r") as f:
        checkbox_code=f.read()

    cjs = CustomJS (args = dict (marker_abs = marker_abs, markers = markers,
                                checkbox_preset = checkbox_preset, checkbox_mark = checkbox_mark,
                                source_table = source_table, source = source, source_markers = source_markers,
                                source_table_share = source_table_share,
                                sliders = sliders
                                ),code = checkbox_code)
    checkbox_preset.js_on_click (cjs)

    checkbox_mark.js_on_click (cjs)

    ##---------------------------------------------------------------------------##

    sliders_col = column (sliders)

    # Ploteos
    layout_graf       = gridplot ([[graf]], sizing_mode = 'scale_width', toolbar_location = "right")
    layout_widgets    = widgetbox (row (checkbox_preset, checkbox_mark, sliders_col, data_table), sizing_mode = 'scale_width')
    layout_seteos     = widgetbox (row (info_table_an, info_table_gen, info_table_powm), sizing_mode = 'scale_width')
    analyzer_layout   = layout ([layout_graf, layout_widgets, set_div, layout_seteos], sizing_mode = 'scale_width')

    return components (analyzer_layout)
