/*
args = dict
(
    graf               = graf,
    sliders            = sliders
    source_markers     = source_markers,
    source_table       = source_table,
    source_table_share = source_table_share,
    source_set_an      = source_set_an,
    source_set_gen     = source_set_gen,
    source_set_powm    = source_set_powm
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
    //console.log ("Initializing adapter vars")
    window.first_time = true;

    // GRAPH (Analizador)
    window.x = new Array (TRACE_LEN).fill (0);
    window.y = new Array (TRACE_LEN).fill (0);
    window.y_bottom = -100;
    
    // ANALIZADOR
    window.x_scale     = 'LIN';
    window.y_scale     = 'LOG';
    window.start_freq  = 0.0;
    window.stop_freq   = 1.0;
    window.span        = 1.0;
    window.center_freq = 1.0;
    window.ref_level   = 0.0;
    window.demod_time  = 0.0;
    window.demod_type  = 'FM';
    window.input_att   = 10;
    window.res_bw      = 100000;
    window.scale_div   = 10.0;
    window.avg_state   = 'WRITe';
    window.avg_times   = 1;

    // GENERADOR
    window.lf_state      = 'OFF';
    window.lf_freq       = '0.0';
    window.lf_level      = '0.0';
    window.lf_waveform   = 'SINE';
    window.rf_state      = '0.0';
    window.rf_freq       = '0.0';
    window.rf_level      = '0.0';
    window.am_state      = 'OFF';
    window.am_source     = 'INT';
    window.am_mod_freq   = '0.0';
    window.am_mod_index  = '0.0';
    window.am_waveform   = 'SINE';
    window.fmpm_mod_type = 'FM';
    window.fmpm_state    = 'OFF';
    window.fm_mod_freq   = '0.0';
    window.fm_mod_index  = '0.0';
    window.fm_waveform   = 'SINE';
    window.pm_mod_freq   = '0.0';
    window.pm_mod_index  = '0.0';
    window.pm_waveform   = '0.0';

    window.power       = [0];
}

// GRAPH (Analizador)
window.x        = 'x'        in cb_data.response ? cb_data.response ['x']        : window.x;
window.y        = 'y'        in cb_data.response ? cb_data.response ['y']        : window.y;
window.y_bottom = 'y_bottom' in cb_data.response ? cb_data.response ['y_bottom'] : window.y_bottom;

// ANALIZADOR
if ('analyzer' in cb_data.response)
{
    window.x_scale      = 'x_scale'      in cb_data.response ['analyzer'] ? [cb_data.response ['analyzer']['x_scale']      ] : window.x_scale;
    window.y_scale      = 'y_scale'      in cb_data.response ['analyzer'] ? [cb_data.response ['analyzer']['y_scale']      ] : window.y_scale;
    window.start_freq   = 'start_freq'   in cb_data.response ['analyzer'] ? [cb_data.response ['analyzer']['start_freq']   ] : window.start_freq;
    window.stop_freq    = 'stop_freq'    in cb_data.response ['analyzer'] ? [cb_data.response ['analyzer']['stop_freq']    ] : window.stop_freq;
    window.span         = 'span'         in cb_data.response ['analyzer'] ? [cb_data.response ['analyzer']['span']         ] : window.span;
    window.center_freq  = 'center_freq'  in cb_data.response ['analyzer'] ? [cb_data.response ['analyzer']['center_freq']  ] : window.center_freq;
    window.ref_level    = 'ref_level'    in cb_data.response ['analyzer'] ? [cb_data.response ['analyzer']['ref_level']    ] : window.ref_level;
    window.demod_time   = 'demod_time'   in cb_data.response ['analyzer'] ? [cb_data.response ['analyzer']['demod_time']   ] : window.demod_time;
    window.demod_type   = 'demod_type'   in cb_data.response ['analyzer'] ? [cb_data.response ['analyzer']['demod_type']   ] : window.demod_type;
    window.input_att    = 'input_att'    in cb_data.response ['analyzer'] ? [cb_data.response ['analyzer']['input_att']    ] : window.input_att;
    window.res_bw       = 'res_bw'       in cb_data.response ['analyzer'] ? [cb_data.response ['analyzer']['res_bw']       ] : window.res_bw;
    window.scale_div    = 'scale_div'    in cb_data.response ['analyzer'] ? [cb_data.response ['analyzer']['scale_div']    ] : window.scale_div;
    window.avg_state    = 'avg_state'    in cb_data.response ['analyzer'] ? [cb_data.response ['analyzer']['avg_state']    ] : window.avg_state;
    window.avg_times    = 'avg_times'    in cb_data.response ['analyzer'] ? [cb_data.response ['analyzer']['avg_times']    ] : window.avg_times;
}

// GENERADOR
if ('generator' in cb_data.response)
{
    window.lf_state      = 'lf_state'      in cb_data.response ['generator'] ? [cb_data.response ['generator']['lf_state']      ] : window.lf_state;
    window.lf_freq       = 'lf_freq'       in cb_data.response ['generator'] ? [cb_data.response ['generator']['lf_freq']       ] : window.lf_freq;
    window.lf_level      = 'lf_level'      in cb_data.response ['generator'] ? [cb_data.response ['generator']['lf_level']      ] : window.lf_level;
    window.lf_waveform   = 'lf_waveform'   in cb_data.response ['generator'] ? [cb_data.response ['generator']['lf_waveform']   ] : window.lf_waveform;
    window.rf_state      = 'rf_state'      in cb_data.response ['generator'] ? [cb_data.response ['generator']['rf_state']      ] : window.rf_state;
    window.rf_freq       = 'rf_freq'       in cb_data.response ['generator'] ? [cb_data.response ['generator']['rf_freq']       ] : window.rf_freq;
    window.rf_level      = 'rf_level'      in cb_data.response ['generator'] ? [cb_data.response ['generator']['rf_level']      ] : window.rf_level;
    window.am_state      = 'am_state'      in cb_data.response ['generator'] ? [cb_data.response ['generator']['am_state']      ] : window.am_state;
    window.am_source     = 'am_source'     in cb_data.response ['generator'] ? [cb_data.response ['generator']['am_source']     ] : window.am_source;
    window.am_mod_freq   = 'am_mod_freq'   in cb_data.response ['generator'] ? [cb_data.response ['generator']['am_mod_freq']   ] : window.am_mod_freq;
    window.am_mod_index  = 'am_mod_index'  in cb_data.response ['generator'] ? [cb_data.response ['generator']['am_mod_index']  ] : window.am_mod_index;
    window.am_waveform   = 'am_waveform'   in cb_data.response ['generator'] ? [cb_data.response ['generator']['am_waveform']   ] : window.am_waveform;
    window.fmpm_mod_type = 'fmpm_mod_type' in cb_data.response ['generator'] ? [cb_data.response ['generator']['fmpm_mod_type'] ] : window.fmpm_mod_type;
    window.fmpm_state    = 'fmpm_state'    in cb_data.response ['generator'] ? [cb_data.response ['generator']['fmpm_state']    ] : window.fmpm_state;
    window.fm_mod_freq   = 'fm_mod_freq'   in cb_data.response ['generator'] ? [cb_data.response ['generator']['fm_mod_freq']   ] : window.fm_mod_freq;
    window.fm_mod_index  = 'fm_mod_index'  in cb_data.response ['generator'] ? [cb_data.response ['generator']['fm_mod_index']  ] : window.fm_mod_index;
    window.fm_waveform   = 'fm_waveform'   in cb_data.response ['generator'] ? [cb_data.response ['generator']['fm_waveform']   ] : window.fm_waveform;
    window.pm_mod_freq   = 'pm_mod_freq'   in cb_data.response ['generator'] ? [cb_data.response ['generator']['pm_mod_freq']   ] : window.pm_mod_freq;
    window.pm_mod_index  = 'pm_mod_index'  in cb_data.response ['generator'] ? [cb_data.response ['generator']['pm_mod_index']  ] : window.pm_mod_index;
    window.pm_waveform   = 'pm_waveform'   in cb_data.response ['generator'] ? [cb_data.response ['generator']['pm_waveform']   ] : window.pm_waveform;

    // transformo a 'YES' o 'NO':
    window.lf_state   = window.lf_state   == '1' ? 'ON' : 'OFF';
    window.rf_state   = window.rf_state   == '1' ? 'ON' : 'OFF';
    window.am_state   = window.am_state   == '1' ? 'ON' : 'OFF';
    window.fmpm_state = window.fmpm_state == '1' ? 'ON' : 'OFF';
}

window.power       = 'power' in cb_data.response ? [cb_data.response ['power']] : window.power0;


/********************************************************
 *                      AUX FUNCTIONS
 ********************************************************/

// si no existe la fila, la crea
function write_table_row (source_table_share, information_str, value)
{    
    idx = source_table_share.data ['x_data'].indexOf (information_str);
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
    idx = source_table.data ['x_data'].indexOf (information_str);
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
    graf.y_range.start = cb_data.response ['y_bottom'];
    graf.y_range.end   = cb_data.response ['ref_value'];
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
        var x_label   = 'x_mark_' + (i + 1).toString ();
        var y_label   = 'y_mark_' + (i + 1).toString ();
        var x_new     = sliders [i].value;
        var step      = sliders [i].step <= 0 ? 1 : sliders [i].step;
        var y_new_idx = Math.round ((x_new - frec_start) / step);
        var y_new     = 0;
        
        if (y_new_idx < y.length)
        {
            y_new     = y [y_new_idx];
        }
        else
        {
            y_new     = y [y.length - 1];
        }

        source_markers.data [x_label] = [x_new];
        source_markers.data [y_label] = [y_new];

        // actualizo valor en la tabla
        var marker_label_str = 'Marker ' + (i + 1).toString ();
        var marker_value_str = y_new.toFixed (2).toString () + 'dBm @ ' + (x_new.toFixed (2)).toString () + ' Hz';
	    
	    write_table_row (source_table_share, marker_label_str, marker_value_str);
        edit_table_row  (source_table, marker_label_str, marker_value_str);
	}

	// Actualizo delta

	if ((source_table.data ['x_data'].indexOf ("Marker 1") >= 0) && 
	    (source_table.data ['x_data'].indexOf ("Marker 2") >= 0))
	{
	    var frec_start = x [0];
	    var step  = x [1] !== x [0] ? x [1] - x [0] : 1;
	    var x0_idx = (sliders [0].value - frec_start) / step;
	    var x1_idx = (sliders [1].value - frec_start) / step;

        delta_x = sliders [1].value - sliders [0].value;
        var delta_y_idx0 = Math.round (x0_idx);
        var delta_y_idx1 = Math.round (x1_idx);
        delta_y = 0;
        
        var delta_y     = 0;
        
        if (delta_y_idx0 > y.length)
        {
            delta_y_idx0 = y.length;
        }
        if (delta_y_idx1 > y.length)
        {
            delta_y_idx1 = y.length;
        }
        delta_y = y [delta_y_idx1] - y [delta_y_idx0];

        sliders [0].step  = step

	    // actualizo valor en la tabla
        var marker_label_str = 'Delta 2 to 1';
	    var marker_value_str = delta_y.toFixed (2).toString () + 'dBm @ ' + (delta_x.toFixed (2)).toString () + ' Hz';
	    write_table_row (source_table_share, marker_label_str, marker_value_str);
	    edit_table_row (source_table, marker_label_str, marker_value_str);
	}

    source_table_share.change.emit();
    source_table.change.emit();
}

function update_markers (y, source_markers)
{
    var max_abs = get_max_abs (y);

    source_markers.data ['x_abs'] = [max_abs ['x']];
    source_markers.data ['y_abs'] = [max_abs ['y']];

    var step  = x [1] !== x [0] ? x [1] - x [0] : 1;
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
    for (var i = 0; i < CANT_MARKERS; i ++)
    {
        sliders [i].start = x [0];

        if (x [0] != x [x.length - 1])
        {
            sliders [i].end  = x [x.length - 1];
            sliders [i].step = (x [x.length - 1] - x [0]) / x.length;
        }
        else
        {
            sliders [i].end  = x [0] + 1;
            sliders [i].step = 1;
        }
    }
}

function update_config_tables ()
{
    // ANALIZADOR
    source_set_an.data ['value'] = [
        window.x_scale,
        window.y_scale,
        window.start_freq.toString (),
        window.stop_freq.toString (),
        window.span.toString (),
        window.center_freq.toString (),
        window.ref_level.toString (),
        window.demod_time.toString (),
        window.demod_type,
        window.input_att.toString (),
        window.res_bw.toString (),
        window.scale_div.toString (),
        window.avg_state,
        window.avg_times.toString ()
    ];

	// GENERADOR
	source_set_gen.data ['value'] = [
        window.lf_state,
        window.lf_freq,
        window.lf_level,
        window.lf_waveform,
        window.rf_state,
        window.rf_freq,
        window.rf_level,
        window.am_state,
        window.am_source,
        window.am_mod_freq,
        window.am_mod_index,
        window.am_waveform,
        window.fmpm_mod_type,
        window.fmpm_state,
        window.fm_state,
        window.fm_mod_freq,
        window.fm_mod_index,
        window.fm_waveform,
        window.pm_state,
        window.pm_mod_freq,
        window.pm_mod_index,
        window.pm_waveform
    ];
    
    source_set_an.change.emit();
    source_set_gen.change.emit();
}


/********************************************************
 *                  MAIN CALLBACK FUNCTION
 ********************************************************/

update_graf    (x, cb_data);
update_table   (x, y, source_table_share);
update_markers (y, source_markers);
update_sliders ();
update_config_tables ();

//console.log ("ADAPTER FINISH OK")

return cb_data.response;
