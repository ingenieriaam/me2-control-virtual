# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------------------------------------
#                                           IMPORTS

from time import sleep
from signal import signal, SIGINT
from requests import post, get, Request
from threading import Thread, Lock, Condition, Event
#from pyvisa_utils import connectToResource, writeCommandToResource, queryCommandToResource
from simulador_pyvisa_utils import connectToResource, writeCommandToResource, queryCommandToResource

# --------------------------------------------------------------------------------------------------------------
#                                       ANALYZER'S GLOBALS

#   ---   ---   ---   ---   ---   ---   ---   ---   ---   ---   ---   ---
#   CONFIGURATION GLOBALS

__DEBUG__ = True
# If this Define is set to "True", only those "if" will be truth, not the ones with "__DEBUG__"
__DEBUG_ONLY_THIS__ = True

ANALYZER_BW_RES = "1E3"
ANALYZER_DISPLAY_ONOFF = "OFF"  # "ON"/"OFF"

CONNECTION_MUTEX_WAI_TIMEOUT = 0.5   # Seconds

SERVER_GET_CONFIG_POLLING_TIME = 2     # Seconds


#   ---   ---   ---   ---   ---   ---   ---   ---   ---   ---   ---   ---
#   FUNCTIONAL GLOBALS (DO NOT MODIFY!!, UNLESS YOU KNOW WHAT YOU ARE DOING)

data_mutex = Condition()
connection_mutex = Condition()
config_mutex = Condition()
analyzer_com_mutex = Lock()
server_com_mutex = Lock()
writing_config_semaphore = Lock()

SERVER_ANALYZER_UPDATE_URL = "/update_analyzer/"
SERVER_ANALYZER_GET_CFG_URL = "/get_analyzer_config/"

SERVER_PORT = ""
ANALYZER_IP = ""

data_readed = True

execute_threads = True
config_ready    = False

analyzer_resource = False

UP = True
DOWN = False
connection_status = DOWN

spectrum = []

commands = Request()

data = {"y": [], "start_freq": 0.0, "stop_freq": 0.0, "y_bottom": 0.0, "ref_level": 0.0}

TRACE_QUERY_FORMAT = ":FORMat:TRACe:DATA REAL,32"
GET_SPECTRUM_TRACE_CMD = ":TRACe:DATA? TRACE1"

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
    "stop_freq"     : 0.0,
    "span"          : 0.0,
    "center_freq"   : 0.0,
    "ref_level"     : 0.0,
    "demod_time"    : "FM",
    "demod_type"    : "",
    "input_att"     : 10,
    "res_bw"        : 0.0,
    "scale_div"     : 0.0,
    "avg_state"     : "WRITe",
    "avg_times"     : 1,
    "freq_or_span"  : "",
    "visa_command"  : ""
}

__DEBUG__ = (__DEBUG__ and (True != __DEBUG_ONLY_THIS__))

# --------------------------------------------------------------------------------------------------------------
#                                       ANALYZER PRIMITIVES


def debug_print(msg="Default debug Message",type="INFO", function_name="", condition=True):
    if condition:
        print_msg = "[DEBUG - "+str(type)+"]\t"+(("("+function_name+")\t") if function_name else "")+">\t"+str(msg)
        print(print_msg)

def debug_error_print(msg="Default debug Message", function_name=""):
    debug_print(msg=msg,type="ERROR", function_name=function_name, condition=True)

def debug_info_print(msg="Default debug Message", function_name=""):
    debug_print(msg=msg,type="INFO", function_name=function_name, condition=True)
    

# Función que intenta conectarse al Analizador de forma recursiva, es bloqueante
def Analyzer_recursiveConnect():

    global analyzer_resource

    analyzer_resource = False

    __DEBUG__ = True

    while (analyzer_resource == False) and (execute_threads):

        analyzer_resource = connectToResource(
            resource_ip=ANALYZER_IP, resource_name="Analyzer")

        if not analyzer_resource:
            debug_print(msg="Error when trying to connect to the Analyzer...",type="ERROR",function_name="Analyzer_recursiveConnect",condition=__DEBUG__)

            sleep(0.5)  # "Anti-Stress" Sleep

    return False if (analyzer_resource == False) else True

def Analyzer_queryBinaryCommand(cmd=":TRACe:DATA? TRACE1", datatype='f', is_big_endian=False):

    global analyzer_resource
    try:
        data_queried = analyzer_resource.query_binary_values(":TRACe:DATA? TRACE1", datatype='f', is_big_endian=False)
    except:
        data_queried = "ERROR"
        retval = False

    else:
        retval = True

    return retval, data_queried

# Bypass para el Analizador de la función writeCommandToResource
def Analyzer_writeCommand(cmd):

    global analyzer_resource
    global analyzer_com_mutex

    answer = "ERROR"

    with analyzer_com_mutex:
        answer = writeCommandToResource(resource=analyzer_resource,
                                        resource_name="Analyzer",
                                        cmd=cmd)

    return answer

# Bypass para el Analizador de la función queryCommandToResource


def Analyzer_queryCommand(cmd):

    global analyzer_resource
    global analyzer_com_mutex

    answer = "ERROR"

    # retval can be True or False, depending whether the Query was successfully made or not
    with analyzer_com_mutex:
        retval, answer = queryCommandToResource(resource=analyzer_resource,
                                                resource_name="Analyzer",
                                                cmd=cmd)

    return retval, answer


times_getconfig = 0
TIMES_TO_QUERY = 20


def Analyzer_getConfig():

    global analyzer_log_dict
    global analyzer_cmd_dict

    global times_getconfig

    times_getconfig = 0 if (times_getconfig == TIMES_TO_QUERY) else times_getconfig+1

    for key in analyzer_log_dict:

        retval = False
        answer = "ERROR"

        if key not in["freq_or_span", "visa_command"]:

            if key in ["start_freq", "stop_freq", "ref_level", "scale_div"]:
                retval, answer = Analyzer_queryCommand(analyzer_cmd_dict[key]+"?")

            elif times_getconfig == TIMES_TO_QUERY:
                retval, answer = Analyzer_queryCommand(analyzer_cmd_dict[key]+"?")

            if retval:
                analyzer_log_dict[key] = answer.replace("\n,", "")
            
            elif key in analyzer_cmd_dict:
                retval = True

        elif key in["freq_or_span", "visa_command"]:
            retval = True

    return retval


def Analyzer_getDisplayParams():

    global analyzer_log_dict

    start_freq = float(analyzer_log_dict["start_freq"])
    stop_freq = float(analyzer_log_dict["stop_freq"])
    ref_level = float(analyzer_log_dict["ref_level"])
    y_bottom = ref_level-10*float(analyzer_log_dict["scale_div"])

    return start_freq, stop_freq, ref_level, y_bottom

# --------------------------------------------------------------------------------------------------------------
#                                       ANALYZER THREADS


#   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --


#  ------>  QUERY FROM ANALYZER AND INFORM TO SERVER

def Analyzer_Query_Thread():

    global execute_threads
    global config_ready
    global do_get_config

    global data_mutex
    global analyzer_com_mutex
    global connection_mutex
    global writing_config_semaphore

    global connection_status

    global spectrum

    global analyzer_resource
    global analyzer_log_dict
    global analyzer_cmd_dict

    debug_info_print(msg="Starting Thread",function_name="Analyzer_Query_Thread")

    while execute_threads:

        if config_ready:
            sleep(0.1)
            config_ready = False

        if connection_status == DOWN:
            with connection_mutex:
                if not Analyzer_recursiveConnect():
                    exit()
                if Analyzer_writeCommand(cmd=TRACE_QUERY_FORMAT):
                    connection_status = UP
                    connection_mutex.notify()
                    do_get_config = True

        with writing_config_semaphore:
            status_ok, aux_spectrum = Analyzer_queryBinaryCommand(cmd=GET_SPECTRUM_TRACE_CMD)

        if status_ok:

            with data_mutex:
                spectrum = aux_spectrum
                data_mutex.notify()

            if do_get_config:
                with writing_config_semaphore:
                    status_ok = Analyzer_getConfig()
                do_get_config = False

            if not status_ok:
                connection_status = DOWN

        else:
            connection_status = DOWN


def Server_Post_Thread():

    global execute_threads

    global data_mutex
    global server_com_mutex

    global data
    global spectrum

    debug_info_print(msg="Starting Thread",function_name="Server_Post_Thread")

    while execute_threads:

        # Este thread solo enviará la info cuando la misma esté lista ( ver data_mutex.notify() en Analyzer_Query_Thread)
        with data_mutex:
            data_mutex.wait()

            if execute_threads == False:
                exit()

            start_freq, stop_freq, ref_level, y_bottom = Analyzer_getDisplayParams()

            # Se conforma el diccionario con la info que le será enviada al servidor
            data = {"y": spectrum, "start_freq": start_freq,
                    "stop_freq": stop_freq, "y_bottom": y_bottom, "ref_level": ref_level}

            data_sent = False
            while (not data_sent) and execute_threads:

                answer = False
                try:
                    with server_com_mutex:
                        answer = post(url=str("http://localhost:"+SERVER_PORT+SERVER_ANALYZER_UPDATE_URL), json=data)

                except:
                    debug_error_print(msg="Error when trying to post to Server, Maybe is it down? Response: "+str(answer),function_name="Server_Post_Thread")
                    sleep(1)

                else:
                    data_sent = True


#   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --


#  ------>  GET FROM SERVER AND CONFIG ANALYZER

cmd_list = []

def Analyzer_Config_Thread():

    global execute_threads
    global do_get_config
    global connection_status

    global config_mutex
    global writing_config_semaphore

    global commands
    global cmd_list

    debug_info_print(msg="Starting Thread",function_name="Analyzer_Config_Thread")

    while execute_threads:

        if connection_status == UP:

            with config_mutex:
                config_mutex.wait()  # Espera a que "Server_Get_Thread" lo habilite
                if execute_threads == False:
                    exit()
                    
                # Adds to the command list new commands (if not repeated)
                cmd_list.extend(list(set(commands)-set(cmd_list)))

            if cmd_list:  # If list not empty

                sent_cmds = []

                for cmd in cmd_list:

                    cmd_sent = False
                    # Loops until the command is sent
                    while (not cmd_sent) and (execute_threads) and cmd:

                        # Tries to write
                        with writing_config_semaphore:
                            cmd_sent = Analyzer_writeCommand(cmd=cmd)

                        if cmd_sent:
                            sent_cmds.append(cmd)

                        # Analyzer_writeCommand(cmd=cmd) == False => ERROR
                        else:
                            connection_status = DOWN
                            while (connection_status == DOWN) and (execute_threads):
                                with connection_mutex:
                                    connection_mutex.wait(CONNECTION_MUTEX_WAI_TIMEOUT)

                # Deletes from command list the commands that were sent
                cmd_list = list(set(cmd_list)-set(sent_cmds))
                do_get_config = True

        else:   # IF connection_status == DOWN
            while (connection_status == DOWN) and (execute_threads):
                with connection_mutex:
                    connection_mutex.wait(CONNECTION_MUTEX_WAI_TIMEOUT)


def Server_Get_Thread():

    global execute_threads
    global config_ready

    global config_mutex
    global server_com_mutex

    global commands

    debug_info_print(msg="Starting Thread",function_name="Server_Get_Thread")

    while execute_threads:

        sleep(SERVER_GET_CONFIG_POLLING_TIME)

        try:

            with config_mutex:
                with server_com_mutex:
                    commands = get("http://localhost:"+SERVER_PORT+SERVER_ANALYZER_GET_CFG_URL)
                commands = list(commands.json())

                if len(commands):
                    config_ready = True
                    config_mutex.notify()

        except:
            debug_error_print(msg="Error when trying to GET from Server, Maybe is it down?",function_name="Server_Get_Thread")


# --------------------------------------------------------------------------------------------------------------
#                                   INITIAL ANALYZER CONFIG

def trigger_exit():
    global execute_threads
    
    global data_mutex
    global connection_mutex
    global config_mutex
    
    execute_threads = False

    with data_mutex:
        data_mutex.notify()

    with connection_mutex:
        connection_mutex.notify()

    with config_mutex:
        config_mutex.notify()
    
    exit()

# IF CTRL+C, then
def sigint_trap(sig, frame):
    debug_info_print(msg="CTRL+C received, exiting analyzer...", function_name="sigint_trap")
    trigger_exit()


if __name__ == '__main__':

    signal(SIGINT, sigint_trap)

    with open("server_port.conf", "r") as f:
        SERVER_PORT = f.read().replace(" ", "").replace("\n","")

    with open("analyzer_ip.conf", "r") as f:
        ANALYZER_IP = f.read().replace(" ", "").replace("\n","")

    analyzer_query_thread = Thread(target=Analyzer_Query_Thread)
    analyzer_query_thread.start()
    server_post_thread = Thread(target=Server_Post_Thread)
    server_post_thread.start()

    server_get_thread = Thread(target=Server_Get_Thread)
    server_get_thread.start()
    analyzer_config_thread = Thread(target=Analyzer_Config_Thread)
    analyzer_config_thread.start()

    #   Exiting logic
    cmd = False
    while (cmd != "exit") and (execute_threads):
        cmd = input("\n[DATALOGGER - INFO]    >   Ingrese un comando cuando lo desee. Ingrese \"exit\" para cerrar el servidor.\n\n")

    debug_info_print(msg="Exit command received, exiting analyzer...",function_name="analyzer_main")

    trigger_exit()

    print("")
