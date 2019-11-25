# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------------------------------------
#                                           IMPORTS

# import numpy as np
# import pyvisa
# from requests import post, get
# from time import sleep
# import os
# import sys

# --------------------------------------------------------------------------------------------------------------
#                                       ANALYZER PRIMITIVES

# with open("server_port.conf","r") as f:
#     SERVER_PORT = f.read()

# ANALYZER_IP     = "192.168.1.2"
# GENERATOR_IP    = "192.168.1.3"
# POWERMETER_IP   = "192.168.1.4"

# SERVER_UPDATE_URL           = "/update/"
# GET_ANALYZER_CONFIG_URL     = "/get_analyzer_config/"
# GET_GENERATOR_CONFIG_URL    = "/get_generator_config/"

# Analyzer_centralFrequency       = "99.9E6"
# Analyzer_frequencySpan          = "500E3"
# Analyzer_bandwidthResolution    = "1E3"
# ANALYZER_DISPLAY_ONOFF          = "OFF" # "ON"/"OFF"
# Analyzer_demodulatorState       = "OFF" # "ON"


# DISPLAY_VALUES_CMD = ":TRACe:DATA? TRACE1"

# analyzer_cmd_dict = {
#                 "x_scale"       : ":DISPlay:WINdow:TRACe:X:SCALe:SPACing",
#                 "y_scale"       : ":DISPlay:WINdow:TRACe:Y:SCALe:SPACing",
#                 "start_freq"    : ":SENSe:FREQuency:STARt",
#                 "stop_freq"     : ":SENSe:FREQuency:STOP",
#                 "span"          : ":SENSe:FREQuency:SPAN",
#                 "center_freq"   : ":SENSe:FREQuency:CENTer",
#                 "ref_level"     : ":DISPlay:WINdow:TRACe:Y:SCALe:RLEVel",
#                 "demod_time"    : ":SENSe:DEMod:TIME",
#                 "demod_type"    : ":SENSe:DEMod",
#                 "input_att"     : ":SENSe:POWer:RF:ATTenuation",
#                 "res_bw"        : ":SENSe:BANDwidth:RESolution",
#                 "scale_div"     : ":DISPlay:WINdow:TRACe:Y:SCALe:PDIVision",
#                 "freq_or_span"  : "",
#                 "visa_command"  : ""
#                 }

# analyzer_log_dict = {
#                 "x_scale"       : "",
#                 "y_scale"       : "",
#                 "start_freq"    : "",
#                 "stop_freq"     : "",
#                 "span"          : "",
#                 "center_freq"   : "",
#                 "ref_level"     : "",
#                 "demod_time"    : "",
#                 "demod_type"    : "",
#                 "input_att"     : "",
#                 "res_bw"        : "",
#                 "scale_div"     : "",
#                 "freq_or_span"  : "",
#                 "visa_command"  : ""
#                 }

# generator_cmd_dict = {
#                 "lf_state"      : ":SOURce:LFOutput:STATe",
#                 "lf_freq"       : ":SOURce:LFOutput:FREQuency",
#                 "lf_level"      : ":SOURce:LFOutput:LEVel",
#                 "lf_waveform"   : ":SOURce:LFOutput:SHAPe",
#                 "rf_state"      : ":OUTPut:STATe",
#                 "rf_freq"       : ":SOURce:FREQuency",
#                 "rf_level"      : ":SOURce:LEVel",
#                 "am_state"      : ":SOURce:AM:STATe",
#                 "am_source"     : ":SOURce:AM:SOURce",
#                 "am_mod_freq"   : ":SOURce:AM:FREQuency",
#                 "am_mod_index"  : ":SOURce:AM:DEPTh",
#                 "am_waveform"   : ":SOURce:AM:WAVEform",
#                 "fmpm_mod_type" : ":SOURce:FMPM:TYPE",
#                 "fmpm_state"    : ":SOURce:MODulation:STATe",
#                 "fm_state"      : ":SOURce:FM:STATe",
#                 "fm_mod_freq"   : ":SOURce:FM:FREQuency",
#                 "fm_mod_index"  : ":SOURce:FM:DEViation",
#                 "fm_waveform"   : ":SOURce:FM:WAVEform",
#                 "pm_state"      : ":SOURce:FM:STATe",
#                 "pm_mod_freq"   : ":SOURce:PM:FREQuency",
#                 "pm_mod_index"  : ":SOURce:PM:DEViation",
#                 "pm_waveform"   : ":SOURce:PM:WAVEform",
#                 "visa_command"  : ""
#                 }

# generator_log_dict = {
#                 "lf_state"      : "",
#                 "lf_freq"       : "",
#                 "lf_level"      : "",
#                 "lf_waveform"   : "",
#                 "rf_state"      : "",
#                 "rf_freq"       : "",
#                 "rf_level"      : "",
#                 "am_state"      : "",
#                 "am_source"     : "",
#                 "am_mod_freq"   : "",
#                 "am_mod_index"  : "",
#                 "am_waveform"   : "",
#                 "fmpm_mod_type" : "",
#                 "fmpm_state"    : "ON",
#                 "fm_state"      : "",
#                 "fm_mod_freq"   : "",
#                 "fm_mod_index"  : "",
#                 "fm_waveform"   : "",
#                 "pm_state"      : "",
#                 "pm_mod_freq"   : "",
#                 "pm_mod_index"  : "",
#                 "pm_waveform"   : "",
#                 "visa_command"  : ""
#                 }

# powermeter_cmd_dict = {
#                 "avg_times"     : "CWAVG 1,MOV,",
#                 "avg_mode"      : "CWAVG 1,AUTO,",
#                 "visa_command"  : ""
#                 }

# powermeter_log_dict = {
#                 "avg_times"     : "",
#                 "avg_mode"      : "",
#                 "visa_command"  : ""
#                 }

# --------------------------------------------------------------------------------------------------------------
#                                       ANALYZER PRIMITIVES

# def Analyzer_getDisplayParams():
#     global start_freq
#     global stop_freq
#     global y_top
#     global y_bottom
#     global analyzer_log_dict

#     start_freq  = int(analyzer_log_dict["start_freq"])
#     stop_freq   = int(analyzer_log_dict["stop_freq"])
#     y_top       = float(analyzer_log_dict["ref_level"])
#     y_bottom    = y_top-10*float(analyzer_log_dict["scale_div"])




# def Analyzer_getConfig(rc,dev_ip=ANALYZER_IP,dev_name="Device"):
#     global analyzer_log_dict
#     global analyzer_cmd_dict

#     for key in analyzer_log_dict:
#         if analyzer_cmd_dict[key]!="":
#             querying = True
#             while querying:
#                 try:
#                     print("[INFO]   > QUERY : "+analyzer_cmd_dict[key]+"?")
#                     analyzer_log_dict[key] = rc.query(analyzer_cmd_dict[key]+"?").replace("\n,","")
#                 except:
#                     print("[ERROR]  > "+dev_name+": Error when trying to query")
#                     rc = connectToResource(dev_ip)
#                 else:
#                     querying = False




# def Generator_getConfig(rc,dev_ip=GENERATOR_IP,dev_name="Device"):
#     global generator_log_dict
#     global generator_cmd_dict

#     for key in generator_log_dict:
#         if generator_cmd_dict[key]!="":
#             querying = True
#             while querying:
#                 try:
#                     print("[INFO]   > QUERY : "+generator_cmd_dict[key]+"?")
#                     generator_log_dict[key] = rc.query(generator_cmd_dict[key]+"?").replace("\n,","")
#                 except:
#                     print("[ERROR]  > "+dev_name+": Error when trying to query")
#                     rc = connectToResource(dev_ip)
#                 else:
#                     querying = False





# def queryCommandToPowermeter(cmd="*IDN?",dev_ip=POWERMETER_IP):
#     global powermeter_log_dict
#     global powermeter_cmd_dict

#     # Anritsu VISA FORM's URL
#     URL = "http://"+POWERMETER_IP+"/ctl.html"
#     # Curl's command
#     curl_cmd = "curl '" + URL + "' --data 'cm=" + cmd + "+&q=" + "WRITE" + "' -s"
#     # Gets Curl's response (Raw HTML)
#     response = os.popen(curl_cmd).read()
#     # Formats Curl's response to get the "answer"
#     answer = response.split('<textarea name="qr" id="qr" ')[1].split('</textarea')[0].split('>')[1]

#     return answer


# def writeCommandToDevice(rc,dev_ip,dev_name="Device",cmd="*IDN?"):
#     commandSent = False
#     while commandSent == False:
#         try:
#             rc.write(cmd)
#         except:
#             print("[ERROR]  > "+dev_name+": Error when trying to write")
#             rc = connectToResource(dev_ip)
#         else:
#             commandSent = True



# def connectToResource(dev_ip,dev_name="Device"):
    
#     ResourcesManager = pyvisa.highlevel.ResourceManager()
#     isConnected = False
#     while isConnected == False:
#         try:
#             Resource = ResourcesManager.open_resource("TCPIP0::" + dev_ip + "::INSTR")
#         except:
#             sleep(1)
#         else:
#             print("[DEBUG]"+Resource.query("*IDN?"))
#             isConnected = True
    
#     return Resource

# SERVER_PORT = str(SERVER_PORT)

# analyzer_resource = connectToResource(ANALYZER_IP)
# generator_resource = connectToResource(GENERATOR_IP)
# queryCommandToPowermeter(cmd="*IDN?",dev_ip=POWERMETER_IP)
# --------------------------------------------------------------------------------------------------------------
# #                                   INITIAL ANALYZER CONFIG

# analyzer_resource.write(":DISPlay:ENABle " + ANALYZER_DISPLAY_ONOFF)

# analyzer_resource.write(":SYSTem:SPEaker:STATe ON")

# --------------------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------------------
#                                   INITIAL GENEARATOR CONFIG

# --------------------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------------------
#                                   INITIAL POWERMETER CONFIG

# --------------------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------------------
#                                       CONTINOUS QUERIES

# print("\nObtaining Analyzer Parameters:")
# Analyzer_getConfig(analyzer_resource)
# print("\nObtaining Generator Parameters:")
# Generator_getConfig(generator_resource)
# print("")

# while True:
    
#     try:
#         print("[DEBUG]   > Querying data from Device")
#         Analyzer_getDisplayParams()
#         spectrum = analyzer_resource.query(":TRACe:DATA? TRACE1").split(",")
#         spectrum[0] = spectrum[0][12:]
#         power = queryCommandToPowermeter(cmd="CWO 1",dev_ip=POWERMETER_IP)

#     except:
#         isConnected = False
#         excepted = False

#         while isConnected == False:

#             try:
#                 analyzer_resource = connectToResource(dev_ip=ANALYZER_IP,dev_name="Analyzer")

#             except:
#                 excepted = True
#                 print("[ERROR]  > "+"Analyzer"+": Error when trying to connect")
#                 sleep(1)

#             else:
#                 if excepted:
#                     Analyzer_getConfig(analyzer_resource)
#                     Generator_getConfig(generator_resource)
#                     Analyzer_getDisplayParams()

#                 print("[INFO]   > "+"Analyzer"+": Successfully connected")
#                 isConnected = True

#     else:
#         data = { "y":spectrum , "fi":start_freq, "ff":stop_freq, "yb":y_bottom, "yt":y_top }
#         print("[DEBUG]   > ANALYZER: Data Queried")

#         try:
#             r = post(url=str("http://localhost:"+SERVER_PORT+SERVER_UPDATE_URL), json = data )

#         except:
#             print("[ERROR]  > Error when trying to post to Server, Maybe is it down?")
#             sleep(1)
#             Analyzer_getConfig(analyzer_resource)
#             Generator_getConfig(generator_resource)
            
#         else:
#             print("[DEBUG]   > Data sent to Server")
    
#     try:
#         print("[DEBUG]   > Getting info from Server")
#         commands = get("http://localhost:"+SERVER_PORT+GET_ANALYZER_CONFIG_URL)
#     except:
#         print("[ERROR]  > Error when trying to get from Server, Maybe is it down?")
#         sleep(1)
#         Analyzer_getConfig(analyzer_resource)
#         Generator_getConfig(generator_resource)
#     else:
#         cmd_list = list(commands.json())
#         if cmd_list:
#             print("[DEBUG]   > ANALYZER's Data queried from Server:")
#             for cmd in cmd_list:
#                 print("[DEBUG - Data Queried]   > "+cmd)
#                 writeCommandToDevice(rc=analyzer_resource,dev_name="Analyzer",dev_ip=ANALYZER_IP,cmd=cmd)
#             Analyzer_getConfig(analyzer_resource)

#     try:
#         print("[DEBUG]   > Getting info from Server")
#         commands = get("http://localhost:"+SERVER_PORT+GET_GENERATOR_CONFIG_URL)
#     except:
#         print("[ERROR]  > Error when trying to get from Server, Maybe is it down?")
#         sleep(1)
#         Analyzer_getConfig(analyzer_resource)
#         Generator_getConfig(generator_resource)
#     else:
#         cmd_list = list(commands.json())
#         if cmd_list:
#             print("[DEBUG]   > GENERATOR's Data queried from Server:")
#             for cmd in cmd_list:
#                 print("[DEBUG - Data Queried]   > "+cmd)
#                 writeCommandToDevice(rc=generator_resource,dev_name="Generator",dev_ip=GENERATOR_IP,cmd=cmd)
#             Generator_getConfig(generator_resource)

#     try:
#         print("[DEBUG]   > Getting info from Server")
#         commands = get("http://localhost:"+SERVER_PORT+GET_POWERMETER_CONFIG_URL)
#     except:
#         print("[ERROR]  > Error when trying to get from Server, Maybe is it down?")
#         sleep(1)
#         Analyzer_getConfig(analyzer_resource)
#     else:
#         cmd_list = list(commands.json())
#         if cmd_list:
#             print("[DEBUG]   > POWERMETER's Data queried from Server:")
#             for cmd in cmd_list:
#                 print("[DEBUG - Data Queried]   > "+cmd)
#                 writeCommandToDevice(rc=powermeter_resource,dev_name="Powermeter",dev_ip=GENERATOR_IP,cmd=cmd)
#             Powermeter_getConfig(powermeter_resource)