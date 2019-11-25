# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------
#                       IMPORTs SECTION

from flask import Flask, render_template, jsonify, request, redirect, url_for

from numpy import linspace
from time import sleep

import random

from tornado.ioloop import IOLoop
from threading import Thread

from bokeh.resources import CDN
from widgets import ajax_getplot

import sys

#                       END IMPORTs SECTION
# -----------------------------------------------------------------------

def debug_print(msg="Default debug Message",type="INFO", function_name="", condition=True):
    if condition:
        print_msg = "[DEBUG - "+str(type)+"]\t"+(("("+function_name+")\t") if function_name else "")+">\t"+str(msg)
        print(print_msg)

def debug_error_print(msg="Default debug Message", function_name=""):
    debug_print(msg=msg,type="ERROR", function_name=function_name, condition=True)

def debug_info_print(msg="Default debug Message", function_name=""):
    debug_print(msg=msg,type="INFO", function_name=function_name, condition=True)

# -----------------------------------------------------------------------
#                       CONFIG SECTION

SERVER_PORT = ""

DEBUG_POWERMETER = True


#                       END CONFIG SECTION
# -----------------------------------------------------------------------

# -----------------------------------------------------------------------
#                       GLOBAL VARs SECTION
TRACE_LEN   = 601
y_bottom = -100
ref_level = 0
x = [i for i in range(0,TRACE_LEN)]
y = [0 for i in range(0,TRACE_LEN)]


lf_freq      = 0
lf_level     = 0
rf_freq      = 0
rf_level     = 0
fm_mod_freq  = 0
am_mod_freq  = 0
am_mod_index = 0
fm_mod_index = 0
pm_mod_index = 0

avg_times    = 0
avg_mode     = 0
visa_command = 0

power = 0

#                     END GLOBAL VARs SECTION
# -----------------------------------------------------------------------

print(">>>>>>>>>>>>> ENTRO GLOBAL")

app = Flask(__name__)

print(">>>>>>>>>>>>> ENTRO GLOBAL POST FLASK")

@app.route('/', methods=['GET', 'POST'])
def visualisation(session_type=None):
    global y_bottom
    global analyzer_log_dict
    global x
    global y

    # PARECERÍA QUE SE ENTRA UNA ÚNICA VEZ POR CLIENTE
    print("New Client Connected")
    plots = []
    plots.append(ajax_getplot(x=x,y=y,y_bottom=y_bottom,ref_value=analyzer_log_dict["ref_level"]))
    #plots2 = []
    #plots2.append(get_ajax_plot2())
    return render_template("dashboard.html",bokeh_css=CDN.render_css(),
                            bokeh_js=CDN.render_js(),plots=plots)#,plots2=plots2)

# -------------------------------------------------------------------------------------------------------------------
#                                   ANALYZER CONFIG
analyzer_cmd_dict = {
    "x_scale"       : ":DISPlay:WINdow:TRACe:X:SCALe:SPACing",
    "y_scale"       : ":DISPlay:WINdow:TRACe:Y:SCALe:SPACing",
    "start_freq"    : ":SENSe:FREQuency:STARt",
    "stop_freq"     : ":SENSe:FREQuency:STOP",
    "span"          : ":SENSe:FREQuency:SPAN",
    "center_freq"   : ":SENSe:FREQuency:CENTer",
    "ref_level"     : ":DISPlay:WINdow:TRACe:Y:SCALe:RLEVel",
    "demod_time"    : ":SENSe:DEMod:TIME",
    "demod_type"    : ":SENSe:DEMod",
    "input_att"     : ":SENSe:POWer:RF:ATTenuation",
    "res_bw"        : ":SENSe:BANDwidth:RESolution",
    "scale_div"     : ":DISPlay:WINdow:TRACe:Y:SCALe:PDIVision",
    "avg_state"     : ":TRACe1:MODE",
    "avg_times"     : ":TRACe:AVERage:COUNt",
    "freq_or_span"  : ":SENSe:FREQuency:SPAN:FULL",
    "visa_command"  : ""
}

analyzer_log_dict = {
    "x_scale"       : "LIN",
    "y_scale"       : "LOG",
    "start_freq"    : 0.0,
    "stop_freq"     : 1.0,
    "span"          : 1.0,
    "center_freq"   : 1.0,
    "ref_level"     : 0.0,
    "demod_time"    : 0.0,
    "demod_type"    : "FM",
    "input_att"     : 10,
    "res_bw"        : 100000,
    "scale_div"     : 10.0,
    "avg_state"     : "WRITe",
    "avg_times"     : 1,
    "freq_or_span"  : "",
    "visa_command"  : ""
}

analyzer_float_cmds = [
    "start_freq",
    "stop_freq",
    "span",
    "center_freq",
    "ref_level",
    "demod_time",
    "input_att",
    "res_bw",
    "scale_div",
    "avg_times"]


send_analyzer_cmd = []
@app.route('/config_analyzer/', methods=['POST','GET'])
def config_analyzer():
    global send_analyzer_cmd
    global analyzer_log_dict

    send_analyzer_cmd = []

    for var in request.form:

        if var == "visa_command" and request.form[var]:
            analyzer_log_dict[var] = request.form[var]
            send_analyzer_cmd.append(analyzer_log_dict[var])

        elif (request.form[var] != "") and (var!="freq_or_span") and (analyzer_log_dict[var] != request.form[var]):
            analyzer_log_dict[var] = request.form[var].upper()
            send_analyzer_cmd.append(analyzer_cmd_dict[var]+" "+analyzer_log_dict[var])

        elif (var=="freq_or_span") and (request.form[var]=="full"):
            send_analyzer_cmd.append(analyzer_cmd_dict[var])

            

    return redirect(url_for('visualisation',session_type="admin"))

@app.route('/get_analyzer_config/', methods=['GET'])
def get_analyzer_config():
    global send_analyzer_cmd
    send_cmd = send_analyzer_cmd
    send_analyzer_cmd = []
    return jsonify(send_cmd)

# -------------------------------------------------------------------------------------------------------------------
#                                   GENERATOR CONFIG

generator_cmd_dict = {
                "lf_state"      : ":SOURce:LFOutput:STATe",
                "lf_freq"       : ":SOURce:LFOutput:FREQuency",
                "lf_level"      : ":SOURce:LFOutput:LEVel",
                "lf_waveform"   : ":SOURce:LFOutput:SHAPe",
                "rf_state"      : ":OUTPut:STATe",
                "rf_freq"       : ":SOURce:FREQuency",
                "rf_level"      : ":SOURce:LEVel",
                "am_state"      : ":SOURce:AM:STATe",
                "am_source"     : ":SOURce:AM:SOURce",
                "am_mod_freq"   : ":SOURce:AM:FREQuency",
                "am_mod_index"  : ":SOURce:AM:DEPTh",
                "am_waveform"   : ":SOURce:AM:WAVEform",
                "fmpm_mod_type" : ":SOURce:FMPM:TYPE",
                "fmpm_state"    : ":SOURce:MODulation:STATe",
                "fm_state"      : ":SOURce:FM:STATe",
                "fm_mod_freq"   : ":SOURce:FM:FREQuency",
                "fm_mod_index"  : ":SOURce:FM:DEViation",
                "fm_waveform"   : ":SOURce:FM:WAVEform",
                "pm_state"      : ":SOURce:FM:STATe",
                "pm_mod_freq"   : ":SOURce:PM:FREQuency",
                "pm_mod_index"  : ":SOURce:PM:DEViation",
                "pm_waveform"   : ":SOURce:PM:WAVEform",
                "visa_command"  : ""
                }

generator_log_dict = {
                "lf_state"      : "OFF",
                "lf_freq"       : "0.0",
                "lf_level"      : "0.0",
                "lf_waveform"   : "SINE",
                "rf_state"      : "0.0",
                "rf_freq"       : "0.0",
                "rf_level"      : "0.0",
                "am_state"      : "OFF",
                "am_source"     : "INT",
                "am_mod_freq"   : "0.0",
                "am_mod_index"  : "0.0",
                "am_waveform"   : "SINE",
                "fmpm_mod_type" : "FM",
                "fmpm_state"    : "OFF",
                "fm_mod_freq"   : "0.0",
                "fm_mod_index"  : "0.0",
                "fm_waveform"   : "SINE",
                "pm_mod_freq"   : "0.0",
                "pm_mod_index"  : "0.0",
                "pm_waveform"   : "0.0",
                "visa_command"  : ""
                }

generator_float_cmds = []

send_generator_cmd = []
@app.route('/config_generator/', methods=['POST','GET'])
def config_generator():
    global send_generator_cmd
    global generator_cmd_dict
    global generator_log_dict
    
    for var in request.form:
        print("[DEBUG] recibido por form "+var+" : "+request.form[var])

        # IF VALID (DIRECT) COMMAND KEY
        if var in list(generator_cmd_dict.keys()):

            if var == "fmpm_mod_type":
                generator_log_dict["fm_state"] = "ON" if (request.form[var].upper()=="FM") else "OFF"
                generator_log_dict["pm_state"] = "ON" if (request.form[var].upper()=="PM") else "OFF"
                generator_log_dict[var] = request.form[var].upper()
                send_generator_cmd.append(generator_cmd_dict[var]+" "+generator_log_dict[var])
                send_generator_cmd.append(generator_cmd_dict["fm_state"]+" "+generator_log_dict["fm_state"])
                send_generator_cmd.append(generator_cmd_dict["pm_state"]+" "+generator_log_dict["pm_state"])

            elif (request.form[var] != "") and (generator_log_dict[var] != request.form[var]):
                generator_log_dict[var] = request.form[var].upper()
                send_generator_cmd.append(generator_cmd_dict[var]+" "+generator_log_dict[var])

        # IF NOT DIRECT VALID COMMAND KEY, BUT "INDIRECT"
        elif var == "fmpm_waveform" or var == "fmpm_mod_freq":

            # SEARCHS FOR MODULATION TYPE, FIRST IN NEW SET-UP, IF NOT SPECIFIED THEN IN THE CURRENT CONFIG
            if("fmpm_mod_type" in request.form):
                var_aux = var.replace("fmpm",request.form["fmpm_mod_type"].lower())
                if generator_log_dict[var_aux] != request.form[var]:
                    generator_log_dict[var_aux] = request.form[var].upper()
                    send_generator_cmd.append(generator_cmd_dict[var_aux]+" "+generator_log_dict[var_aux])

            elif("fmpm_mod_type" in generator_log_dict):
                var_aux = var.replace("fmpm",generator_log_dict["fmpm_mod_type"].lower())
                if generator_log_dict[var_aux] != request.form[var]:
                        generator_log_dict[var_aux] = request.form[var].upper()
                        send_generator_cmd.append(generator_cmd_dict[var_aux]+" "+generator_log_dict[var_aux])
        
        # IF NOT VALID COMMAND KEY
        else:
            print("[DEBUG -ERROR]   :   CMD NOT FOUND :"+var+" : "+request.form[var])

    return redirect(url_for('visualisation',session_type="admin"))

@app.route('/get_generator_config/', methods=['GET'])
def get_generator_config():
    global send_generator_cmd
    send_cmd = send_generator_cmd
    send_generator_cmd = []
    return jsonify(send_cmd)

# -------------------------------------------------------------------------------------------------------------------
#                                   POWERMETER CONFIG

GET_POWER_CMD = "CWO 1"

powmeter_cmd_dict = {
                "power"         : GET_POWER_CMD,
                "avg_times"     : "CWAVG 1, MOV, ",
                "avg_mode"      : "CWAVG 1,AUTO,",
                "ch_active"     : "CHACTIV 1",
                "ch_unit"       : "CHUNIT 1,",
                "visa_command"  : ""
                }

powmeter_log_dict = {
                "power"         : "",
                "avg_times"     : "",
                "avg_mode"      : "",
                "ch_active"     : "",
                "ch_unit"       : "",
                "visa_command"  : ""
                }

@app.route('/pow_update/', methods=['POST'])
def pow_update():
    if request.form["power"]:
        print("pow: "+request.form["power"])
        powmeter_log_dict["power"]=request.form["power"]


send_powermeter_cmd = []
@app.route('/config_powermeter/', methods=['POST','GET'])
def config_powermeter():
    global send_powermeter_cmd
    global powmeter_log_dict
    global powmeter_cmd_dict

    send_powermeter_cmd = []

    for var in request.form:
        if var in powmeter_cmd_dict:
            
            if var == "visa_command":
                send_powermeter_cmd.append(request.form["visa_command"])
            if var == "avg_mode":
                if request.form[var]=="OFF":
                    send_powermeter_cmd.append("CWAVG 1, MOV, 1")
                elif request.form[var]=="AUTO":
                    send_powermeter_cmd.append("CWAVG 1, AUTO, 1")
                elif request.form[var]=="MOVE":
                    send_powermeter_cmd.append("CWAVG 1, MOV, "+request.form["avg_times"])
                elif request.form[var]=="REPEAT":
                    send_powermeter_cmd.append("CWAVG 1, RPT, "+request.form["avg_times"])
            if var == "ch_unit":
                send_powermeter_cmd.append("CHUNIT 1,"+request.form["ch_unit"])
            if var == "calf_mode":
                if request.form["calf_mode"] == "AUTO":
                    send_powermeter_cmd.append("SNCFSRC A,FREQ")
                    send_powermeter_cmd.append("SNCFRQ A,"+str(request.form("calf_freq")))
                elif request.form["calf_mode"] == "MANUAL":
                    send_powermeter_cmd.append("SNCFSRC A,MAN")
                    send_powermeter_cmd.append("SNCFRQ A,"+str(request.form("calf_freq")))
                    send_powermeter_cmd.append("SNCFCAL A,DB,"+str(request.form("calf_val")))
        else:
            print("[DEBUG - ERROR] (config_powermeter)  >   NO SE DETECTÓ EL COMANDO: "+request.form[var])

    return redirect(url_for('visualisation',session_type="admin"))

@app.route('/get_powermeter_config/', methods=['GET'])
def get_powermeter_config():
    global send_powermeter_cmd
    send_cmd = send_powermeter_cmd
    send_powermeter_cmd = []
    return jsonify(send_cmd)

# -------------------------------------------------------------------------------------------------------------------
#

@app.route('/isalive/', methods=['POST'])
def isalive():
    return "It's Alive!"

@app.route('/update_analyzer/', methods=['POST'])
def update():
    
    global analyzer_log_dict
    global y_bottom
    global x
    global y

    calc_x = False

    for k in request.json:
        if request.json [k] != "ERROR":
            if calc_x == False:
                calc_x = True if k in ["start_freq","stop_freq"] else False

            if k in analyzer_float_cmds:
                analyzer_log_dict [k] = float (request.json [k])
            elif k == "y":
                y = request.json [k]
                y = [float(val) for val in y] 
            elif k == "y_bottom":
                y_bottom = float (request.json ['y_bottom'])
            else:
                analyzer_log_dict [k] = request.json [k]
    
    if calc_x:
        x = list (linspace (analyzer_log_dict ["start_freq"], analyzer_log_dict ["stop_freq"], len (y)))
    
    return "OK"

@app.route('/update_generator/', methods=['POST'])
def update_generator():
    global generator_log_dict
    
    for k in request.json:
        if request.json [k] != "ERROR":
            if k in generator_float_cmds:
                generator_log_dict [k] = float (request.json [k])
            else:
                generator_log_dict [k] = request.json [k]
    
    return "OK"

# DATA LO SOLICITA EL CLIENTE? Y AL CLIENTE SE LE RETORNA SOLO X e Y? (CON EL JSONIFY)
# SI ES ASÌ, NO CONVIENE ESTAR LEYENDO EL ARCHIVO CADA 2 X 3
@app.route('/data/', methods=['POST'])
def data():

    return jsonify (x = x, y = y, y_bottom = y_bottom,
            analyzer     = analyzer_log_dict,
			generator    = generator_log_dict)#,
			# span         = span,
			# center_freq  = center_freq,
			# demod_time   = demod_time,
			# ref_level    = ref_level,
			# lf_freq      = lf_freq,
			# lf_level     = lf_level,
			# rf_freq      = rf_freq,
			# rf_level     = rf_level,
			# fm_mod_freq  = fm_mod_freq,
			# am_mod_freq  = am_mod_freq,
			# am_mod_index = am_mod_index,
			# fm_mod_index = fm_mod_index,
			# pm_mod_index = pm_mod_index,
		    # avg_times   = avg_times,
			# avg_mode    = avg_mode,
            #power       = power)

@app.route('/admin_session.html/', methods=['POST'])
def isnotadmin():
    return "<h1>Ah, ah ah,,, you are not an administrator</h1>"

if __name__ == "__main__":

    with open("server_port.conf","r") as f:
        SERVER_PORT = f.read().replace(" ","").replace("\n","")

    app.config["CACHE_TYPE"] = "null"

    app.run(host='0.0.0.0', port=SERVER_PORT, debug=False)

    print(">>>>>>>>>>>>> SALGO MAIN")
    
    print("\n\nFinishing the server execution... Thanks!\n\n")
