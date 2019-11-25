/*
args = dict
(
    graf = graf, sliders = sliders
    source_markers       = source_markers,
    source_table         = source_table,
    source_table_share   = source_table_share,
    source_set_an        = source_set_an,
    source_set_gen       = source_set_gen,
    source_set_powm      = source_set_powm,
    graf_limits          = graf_limits
)
*/



/********************************************************
 *                      CONSTANTS
 ********************************************************/

const FILENAME = 'graf_adapter.js'
const CANT_MARKERS = 4; // al modificar esto, modificar tambien CANT_MARKERS en widgets.py y checkbox_callback.js
const TRACE_LEN = 601;



/********************************************************
 *                  MAIN CALLBACK DECLARATIONS
 ********************************************************/

if (window.first_time === undefined)
{
    window.first_time = true;

    // GRAPH
    window.x = new Array (TRACE_LEN).fill (0);
    window.y = new Array (TRACE_LEN).fill (0);
    
    // ANALIZADOR
    window.start_freq  = [0];
    window.stop_freq   = [2];
    window.span        = [2];
    window.center_freq = [1];
    window.demod_time  = [1];
    window.ref_level   = [0];

    // GENERADOR
    window.lf_freq      = [0];
    window.lf_level     = [0];
    window.rf_freq      = [0];
    window.rf_level     = [0];
    window.fm_mod_freq  = [0];
    window.am_mod_freq  = [0];
    window.am_mod_index = [0];
    window.fm_mod_index = [0];
    window.pm_mod_index = [0];

    window.power       = [0];
}

// GRAPH
window.x = 'x' in cb_data.response ? cb_data.response ['x'] : window.x;
window.y = 'y' in cb_data.response ? cb_data.response ['y'] : window.y;

// ANALIZADOR
window.start_freq  = 'start_freq'  in cb_data.response ? [cb_data.response ['start_freq']]  : window.start_freq0;
window.stop_freq   = 'stop_freq'   in cb_data.response ? [cb_data.response ['stop_freq']]   : window.stop_freq0;
window.span        = 'span'        in cb_data.response ? [cb_data.response ['span']]        : window.span0;
window.center_freq = 'center_freq' in cb_data.response ? [cb_data.response ['center_freq']] : window.center_freq0;
window.demod_time  = 'demod_time'  in cb_data.response ? [cb_data.response ['demod_time']]  : window.demod_time0;
window.ref_level   = 'ref_level'   in cb_data.response ? [cb_data.response ['ref_level']]   : window.ref_level0;

// GENERADOR
window.lf_freq      = 'lf_freq'      in cb_data.response ? [cb_data.response ['lf_freq']]      : window.lf_freq0;
window.lf_level     = 'lf_level'     in cb_data.response ? [cb_data.response ['lf_level']]     : window.lf_level0;
window.rf_freq      = 'rf_freq'      in cb_data.response ? [cb_data.response ['rf_freq']]      : window.rf_freq0;
window.rf_level     = 'rf_level'     in cb_data.response ? [cb_data.response ['rf_level']]     : window.rf_level0;
window.fm_mod_freq  = 'fm_mod_freq'  in cb_data.response ? [cb_data.response ['fm_mod_freq']]  : window.fm_mod_freq0;
window.am_mod_freq  = 'am_mod_freq'  in cb_data.response ? [cb_data.response ['am_mod_freq']]  : window.am_mod_freq0;
window.am_mod_index = 'am_mod_index' in cb_data.response ? [cb_data.response ['am_mod_index']] : window.am_mod_index0;
window.fm_mod_index = 'fm_mod_index' in cb_data.response ? [cb_data.response ['fm_mod_index']] : window.fm_mod_index0;
window.pm_mod_index = 'pm_mod_index' in cb_data.response ? [cb_data.response ['pm_mod_index']] : window.pm_mod_index0;

window.power       = 'power' in cb_data.response ? [cb_data.response ['power']] : window.power0;


/********************************************************
 *                      AUX FUNCTIONS
 ********************************************************/

// si no existe la fila, la crea
function write_table_row (source_table_share, information_str, value)
{    
    idx = source_table_share.data ['x_data'].indexOf (information_str)
    if (idx >= 0) 
    {
        source_table_share.data ['y_data'] [idx] = value;
    }
    else
    {
        source_table_share.data ['x_data'].push (information_str);
        source_table_share.data ['y_data'].push (value);
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

 function get_max_abs (y)
 {
    var max_abs_y = Math.max.apply (null, y);
    var max_abs_x = x [y.indexOf (max_abs_y)];

    return {'x' : max_abs_x, 'y' : max_abs_y};
 }

// function find_peaks (list)
// {
//     maxes = []
//     maxes_idx = []
    
//     for (var i = 1; i < list.length - 1; ++ i)
//     {
//         if (list [i - 1] < list [i] && list [i] > list [i + 1])
//         {
//             maxes.push (list [i])
//             maxes_idx.push (i)
//         }
//     }

//     return [maxes_idx, maxes]
// }



/********************************************************
 *                  UPDATE FUNCTIONS
 ********************************************************/

function update_graf (x, cb_data)
{
    graf.x_range.start = x [0];
    graf.x_range.end   = x [(x.length) - 1];
    graf.y_range.start = float(cb_data.response ['y_bottom']);
    graf.y_range.end   = float(cb_data.response ['ref_value']);
    graf.source        = cb_data.response;
}

function update_table (x, y, source_table_share)
{
	// Absolute Maximum
    var max_abs = get_max_abs (y);
    var row_value_str = max_abs ['y'].toFixed (2).toString () + 'dBm @ ' + max_abs ['x'].toFixed (2).toString () + ' Hz';
	var frec_start = x [0];

    write_table_row (source_table_share, "Absolute maximum", row_value_str);
    edit_table_row  (source_table, "Absolute maximum", row_value_str);

    // Markers
    for (var i = 0; i < CANT_MARKERS; i ++)
    {
        var x_label = 'x_mark_' + (i + 1).toString ();
        var y_label = 'y_mark_' + (i + 1).toString ();
        var x_new   = sliders [i].value;
        var step    = sliders [i].step;
        var y_new   = y [Math.round ((x_new - frec_start) / step)];

        source_markers.data [x_label] = [x_new];
        source_markers.data [y_label] = [y_new];

        // actualizo valor en la tabla
        var marker_label_str = 'Marker ' + (i + 1).toString ();
        var marker_value_str = y_new.toFixed (2).toString () + 'dBm @ ' + (x_new.toFixed (2)).toString () + ' Hz';
	    
	    write_table_row (source_table_share, marker_label_str, marker_value_str);
        edit_table_row  (source_table, marker_label_str, marker_value_str)
	}

	// Actualizo delta

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

	    // actualizo valor en la tabla
	    var marker_label_str = 'Delta 2 to 1';
	    var marker_value_str = delta_y.toFixed (2).toString () + 'dBm @ ' + (delta_x.toFixed (2)).toString () + ' Hz';
	    write_table_row (source_table_share, marker_label_str, marker_value_str)
	    edit_table_row (source_table, marker_label_str, marker_value_str)
	}

    source_table_share.change.emit();
    source_table.change.emit();
}

function update_markers (y, source_markers)
{
    var max_abs = get_max_abs (y);

    source_markers.data ['x_abs'] = [max_abs ['x']];
    source_markers.data ['y_abs'] = [max_abs ['y']];

    var step = x [1] - x [0];
    for (var i = 0; i < CANT_MARKERS; i ++)
    {
        x_label = 'x_mark_' + (i + 1).toString ();
        y_label = 'y_mark_' + (i + 1).toString ();

        // actualizo valor de los markers
    	var mark_x = source_markers.data [x_label];
        source_markers.data [y_label] = [y [Math.floor ((mark_x - x [0]) / step)]];
    }

    source_markers.change.emit();
}

function update_sliders ()
{
	var step = (x [x.length - 1] - x [0]) / x.length

    for (var i = 0; i < CANT_MARKERS; i ++)
    {
        sliders [i].start = x [0];
        sliders [i].end   = x [x.length - 1];
        sliders [i].step = (x [x.length - 1] - x [0]) / x.length
    }
}

function update_config_tables ()
{
    // ANALIZADOR
	source_set_an.data ['value'] = [start_freq, stop_freq, span, center_freq, demod_time, ref_level];

	// GENERADOR
	source_set_gen.data ['value'] = [lf_freq, lf_level, rf_freq, rf_level, fm_mod_freq, am_mod_freq, am_mod_index, fm_mod_index, pm_mod_index];
    
    source_set_an.change.emit();
    source_set_gen.change.emit();
}


/********************************************************
 *                  MAIN CALLBACK FUNCTION
 ********************************************************/
graf_limits ['x_start'] = x [0];
graf_limits ['x_end']   = x [x.length - 1];
graf_limits ['y_start'] = y [0];
graf_limits ['y_end']   = y [y.length - 1];

update_graf    (x, cb_data);
update_table   (x, y, source_table_share);
update_markers (y, source_markers);
update_sliders ();
update_config_tables ();

console.log ("ADAPTER FINISH OK")

return cb_data.response
