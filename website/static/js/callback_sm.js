/*
args = dict
(
    source_table = source_table, source = source, source_markers = source_markers,
    sliders = sliders, markers = markers,
    graf = graf, props = props,
    frec_start = x [0],
)
*/



/********************************************************
 *                      CONSTANTS
 ********************************************************/

const FILENAME = "callback_sm.js"
const CANT_MARKERS = 4; // al modificar esto, modificar tambien CANT_MARKERS en widgets.py y checkbox_callback.js



/********************************************************
 *                      AUX FUNCTIONS
 ********************************************************/

// si no existe la fila, la crea
function write_table_row (source_table, information_str, value)
{    
    idx = source_table.data ['x_data'].indexOf (information_str)
    if (idx >= 0) 
    {
        source_table.data ['y_data'] [idx] = value;
    }
    else
    {
        source_table.data ['x_data'].push (information_str);
        source_table.data ['y_data'].push (value);
    }
}

// si no existe la FileReader, no hace nada
function edit_table_row (source_table, information_str, value)
{    
    idx = source_table.data ['x_data'].indexOf (information_str)
    if (idx >= 0) 
    {
        source_table.data ['y_data'] [idx] = value;
    }
}



/********************************************************
 *                  MAIN CALLBACK DECLARATIONS
 ********************************************************/

console.log ('COMIENZA');

var x = source.data ['x'];
var y = source.data ['y'];
var frec_start = x [0];
var step  = x [1] - x [0];
var x_new;
var y_new;
var x_label;
var y_label;
var delta_x;
var delta_y;



/********************************************************
 *                  MAIN CALLBACK FUNCTION
 ********************************************************/

// Actualizo marker

for (var i = 0; i < CANT_MARKERS; i ++)
{
    if(Object.is (cb_obj, sliders [i]))
    {
        x_label = 'x_mark_' + (i + 1).toString ();
        y_label = 'y_mark_' + (i + 1).toString ();
        x_new   = cb_obj.value;
        y_new   = y [Math.round ((x_new - frec_start) / step)];
        step    = cb_obj.step;

        console.log ('SLIDER');
        console.log (x_new);
        console.log (y_new);

        source_markers.data [x_label] = [x_new];
        source_markers.data [y_label] = [y_new];

        // actualizo valor en la tabla
        var marker_label_str = 'Marker ' + (i + 1).toString ();
        var marker_value_str = y_new.toFixed (2).toString () + 'dBm @ ' + (x_new.toFixed (2)).toString () + ' Hz';
        edit_table_row (source_table, marker_label_str, marker_value_str)
    }
}

// Actualizo delta

if ((source_table.data ['x_data'].indexOf ("Marker 1") >= 0) && 
    (source_table.data ['x_data'].indexOf ("Marker 2") >= 0))
{
    var x0_idx = (sliders [0].value - frec_start) / step;
    var x1_idx = (sliders [1].value - frec_start) / step;

    delta_x = sliders [1].value - sliders [0].value
    delta_y = y [Math.round (x1_idx)] - y [Math.round (x0_idx)];
    sliders [0].step  = step

    // actualizo valor en la tabla
    var marker_label_str = 'Delta 2 to 1';
    var marker_value_str = delta_y.toFixed (2).toString () + 'dBm @ ' + (delta_x.toFixed (2)).toString () + ' Hz';
    edit_table_row (source_table, marker_label_str, marker_value_str)
}

source_table.change.emit   ();
source_markers.change.emit ();