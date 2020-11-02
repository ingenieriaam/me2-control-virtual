/*
args = dict
(
    marker_abs = marker_abs,
    markers = markers,
    checkbox_preset = checkbox_preset,
    checkbox_mark = checkbox_mark,
    source_table = source_table,
    source = source
    source_markers = source_markers
    source_table_share = source_table_share
    graf_limits = graf_limits,
    sliders = sliders
)
*/



/********************************************************
 *                      CONSTANTS
 ********************************************************/

const FILENAME = "checkbox_callback.js"
const CANT_MARKERS = 4; // al modificar esto, modificar tambien CANT_MARKERS en widgets.py y graf_adapter.js



/********************************************************
 *                      AUX FUNCTIONS
 ********************************************************/

function remove_table_rows (source_table, information_str, marker)
{
    // x_str = typeof x_str !== 'undefined' ? x_str : 'x_data'; // default arg

    if (marker !== undefined)
    {
        marker.visible = false;
    }
    var idx;
    do 
    {
        idx = source_table.data ['x_data'].indexOf (information_str)
        if (idx >= 0) 
        {
            source_table.data ['x_data'].splice (idx, 1);
            source_table.data ['y_data'].splice (idx, 1);
        }
    }
    while (idx >= 0);
}

function copy_table_row (source_table, information_str, source_table_share, marker)
{
    if (marker !== undefined)
    {
        marker.visible = true;
    }

    source_table.data ['x_data'].push (information_str);
    
    idx = source_table_share.data ['x_data'].indexOf (information_str)
    if (idx >= 0) 
    {
        source_table.data ['y_data'].push (source_table_share.data ['y_data'] [idx]);
    }
    else
    {
        source_table.data ['y_data'].push ("");
    }
}

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



/********************************************************
 *                  MAIN CALLBACK DECLARATIONS
 ********************************************************/

// console.log (FILENAME + ": START");

var x = source.data ['x'];
var y = source.data ['y'];
// var maxEnableRel = Boolean(false);



/********************************************************
 *                  MAIN CALLBACK FUNCTION
 ********************************************************/
 
if (Object.is (cb_obj, checkbox_preset))
{
    var maxEnable = Boolean(false);

    cb_obj.active.forEach (function (element) 
        {
            // EN CASO DE ACTIVARSE EL CHECK BOX
            switch (element)
            {
                case 0: // maximo abs
                    maxEnable = true;
                    break;
                // case 1: // maximos relativos
                //     maxEnableRel = true
                //     break;

                default:
                    break;
            }
        });

    remove_table_rows (source_table, "Absolute maximum", marker_abs)
    if (maxEnable) 
    {
        copy_table_row (source_table, "Absolute maximum", source_table_share, marker_abs);
    }
}
else if (Object.is (cb_obj, checkbox_mark))
{
    var mark_enable = new Array (CANT_MARKERS).fill (false);

    cb_obj.active.forEach (function (element) 
        {
            // EN CASO DE ACTIVARSE EL CHECK BOX
            mark_enable [element] = true;
        });

    for (var i = 0; i < CANT_MARKERS; i++)
    {
        var mark_label = "Marker "   + (i + 1).toString ();
        remove_table_rows (source_table, mark_label, markers [i])
        if (mark_enable [i]) 
        {
            copy_table_row (source_table, mark_label, source_table_share, markers [i]);
        }
    }
}

// Actualizo delta

var marker_label_str = 'Delta 2 to 1';
remove_table_rows (source_table, marker_label_str)
if ((source_table.data ['x_data'].indexOf ("Marker 1") >= 0) && 
    (source_table.data ['x_data'].indexOf ("Marker 2") >= 0))
{
    var frec_start = x [0];
    var step  = x [1] - x [0];
    var x0_idx = (sliders [0].value - frec_start) / step;
    var x1_idx = (sliders [1].value - frec_start) / step;

    delta_x = sliders [1].value - sliders [0].value
    delta_y = y [Math.round (x1_idx)] - y [Math.round (x0_idx)];
    sliders [0].step  = step

    // actualizo valor en la tablax
    var marker_value_str = delta_y.toFixed (2).toString () + 'dBm @ ' + (delta_x.toFixed (2)).toString () + ' Hz';
    copy_table_row (source_table, marker_label_str, source_table_share);
}

source_table.change.emit();
source_markers.change.emit();

// console.log (FILENAME + ": END");
