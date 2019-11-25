# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------------------------------------
#                                           IMPORTS

from time import sleep
from signal import signal, SIGINT
from requests import post, get, Request
from threading import Thread, Lock, Condition, Event
from pyvisa_utils import connectToResource, writeCommandToResource, queryCommandToResource
#from simulador_pyvisa_utils import connectToResource, writeCommandToResource, queryCommandToResource
from log import Log
from copy import deepcopy

# --------------------------------------------------------------------------------------------------------------
#                                       GENERATOR'S GLOBALS

#   ---   ---   ---   ---   ---   ---   ---   ---   ---   ---   ---   ---
#   CONFIGURATION GLOBALS


GENERATOR_BW_RES = "1E3"
GENERATOR_DISPLAY_ONOFF = "OFF"  # "ON"/"OFF"

CONNECTION_MUTEX_WAI_TIMEOUT = 0.5   # Seconds

SERVER_GET_CONFIG_POLLING_TIME = 0.5     # Seconds


#   ---   ---   ---   ---   ---   ---   ---   ---   ---   ---   ---   ---
#   FUNCTIONAL GLOBALS (DO NOT MODIFY!!, UNLESS YOU KNOW WHAT YOU ARE DOING)

data_mutex = Condition()
connection_mutex = Condition()
config_mutex = Condition()
generator_com_mutex = Lock()
server_com_mutex = Lock()
writing_config_semaphore = Lock()

SERVER_GENERATOR_UPDATE_URL = "/update_generator/"
SERVER_GENERATOR_GET_CFG_URL = "/get_generator_config/"

SERVER_PORT = ""
GENERATOR_IP = ""

data_readed = True

execute_threads = True

generator_resource = False

UP = True
DOWN = False
connection_status = DOWN

commands = Request()

data = {"y": [], "fi": 0.0, "ff": 0.0, "yb": 0.0, "yt": 0.0}

# hace query 1 de cada TIMES_TO_QUERY veces. 'force_query' fuerza el query ignorando el TIMES_TO_QUERY
force_query = False

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
                "fm_mod_freq"   : ":SOURce:FM:FREQuency",
                "fm_mod_index"  : ":SOURce:FM:DEViation",
                "fm_waveform"   : ":SOURce:FM:WAVEform",
                "pm_mod_freq"   : ":SOURce:PM:FREQuency",
                "pm_mod_index"  : ":SOURce:PM:DEViation",
                "pm_waveform"   : ":SOURce:PM:WAVEform",
                "visa_command"  : ""
                }

generator_log_dict = {
                "lf_state"      : "OFF",
                "lf_freq"       : 0.0,
                "lf_level"      : 0.0,
                "lf_waveform"   : "SINE",
                "rf_state"      : 0.0,
                "rf_freq"       : 0.0,
                "rf_level"      : 0.0,
                "am_state"      : "OFF",
                "am_source"     : "INT",
                "am_mod_freq"   : 0.0,
                "am_mod_index"  : 0.0,
                "am_waveform"   : "SINE",
                "fmpm_mod_type" : "FM",
                "fmpm_state"    : "OFF",
                "fm_mod_freq"   : 0.0,
                "fm_mod_index"  : 0.0,
                "fm_waveform"   : "SINE",
                "pm_mod_freq"   : 0.0,
                "pm_mod_index"  : 0.0,
                "pm_waveform"   : 0.0,
                "visa_command"  : ""
                }

# Los querys vitales se hacen todas las veces, las demas se hacen 1 vez cada TIMES_TO_QUERY veces
vital_queries = [] # Para el generador no hay querys vitales

# Comandos que NO son query. Son Srite o se usan internamente para otra cosa
not_query_commands = ['visa_command']

# --------------------------------------------------------------------------------------------------------------
#                                       GENERATOR PRIMITIVES


# Función que intenta conectarse al Analizador de forma recursiva, es bloqueante
def Generator_recursiveConnect(parent_log):
    
    global generator_resource

    generator_resource = False

    log = Log (parent_log = parent_log, func_name = "Generator_recursiveConnect")

    while generator_resource == False:
        sleep(0.1)
        log.debug("Connecting to the GENERATOR...")
        generator_resource = connectToResource(resource_ip=GENERATOR_IP, parent_log=log, resource_name="GENERATOR")
        if not generator_resource:
            log.debug("Error when trying to connect to the GENERATOR...")

            sleep(0.5)  # "Anti-Stress" Sleep

    return False if (generator_resource == False) else True

# Bypass para el Analizador de la función writeCommandToResource
def Generator_writeCommand(cmd, parent_log):

    global generator_resource
    global generator_com_mutex

    log = Log (parent_log = parent_log, func_name = "Generator_writeCommand")
    answer = "ERROR"
    #log.debug ("cmd=" + str (cmd))

    # Returns True or False
    with generator_com_mutex:
        answer = writeCommandToResource(resource=generator_resource, 
                                        parent_log=log, 
                                        resource_name="GENERATOR", 
                                        cmd=cmd)

    #log.debug ("[DEBUG] (Generator_writeCommand)  > ans="+str(ans))

    return answer

# Bypass para el Analizador de la función queryCommandToResource
def Generator_queryCommand(cmd, parent_log):

    global generator_resource
    global generator_com_mutex

    log = Log (parent_log = parent_log, func_name = "Generator_queryCommand")

    # retval can be True or False, depending whether the Query was successfully made or not

    answer = "ERROR"
    
    with generator_com_mutex:
        retval, answer = queryCommandToResource(resource=generator_resource, 
                                                parent_log = log,
                                                resource_name="GENERATOR",
                                                cmd=cmd)

    log.debug("QUERY : " + cmd + " = " + str (answer))
    #log.debug ("[DEBUG] (Generator_queryCommand)  > retval="+str(retval))
    #log.debug ("[DEBUG] (Generator_queryCommand)  > answer="+str(answer))

    return retval, answer

times_getconfig = 0

def Generator_getConfig (parent_log):

    global generator_log_dict
    global generator_cmd_dict
    global times_getconfig
    global force_query

    log = Log (parent_log = parent_log, func_name = "Generator_getConfig")

    TIMES_TO_QUERY = 5

    if (force_query == True):
        times_getconfig = TIMES_TO_QUERY
        force_query     = False

    times_getconfig = 0 if (times_getconfig == TIMES_TO_QUERY) else times_getconfig+1
    retval = False

    for key in generator_log_dict:

        retval = False
        answer = "ERROR"

        #log.debug ("KEY : " + str (key))

        if key not in not_query_commands:

            if key in vital_queries:
                retval, answer = Generator_queryCommand (generator_cmd_dict [key] + "?", parent_log = log)

            elif times_getconfig == TIMES_TO_QUERY:
                retval, answer = Generator_queryCommand (generator_cmd_dict [key] + "?", parent_log = log)

            if retval:
                generator_log_dict [key] = answer
            
            elif key in generator_cmd_dict:
                retval = True

        elif key in not_query_commands:
            retval = True
    
    return retval


def Generator_getDisplayParams (parent_log):

    global generator_log_dict
    
    log = Log (parent_log = parent_log, func_name = "Generator_getDisplayParams")

    start_freq  = float (generator_log_dict ["start_freq"])
    stop_freq   = float (generator_log_dict ["stop_freq"])
    y_top       = float (generator_log_dict ["ref_level"])
    y_bottom    = y_top - 10 * float (generator_log_dict ["scale_div"])

    return start_freq, stop_freq, y_top, y_bottom

# --------------------------------------------------------------------------------------------------------------
#                                       GENERATOR THREADS


#   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --


#  ------>  QUERY FROM GENERATOR AND INFORM TO SERVER

def Generator_Query_Thread (print_lock):

    global execute_threads

    global data_mutex
    global generator_com_mutex
    global connection_mutex
    global writing_config_semaphore

    global connection_status

    global generator_resource
    global generator_log_dict
    global generator_cmd_dict

    log = Log (func_name = "Generator_Query_Thread", print_lock = print_lock)

    log.debug ("Starting Thread")

    while execute_threads:

        sleep (1)

        if connection_status == DOWN:
            with connection_mutex:
                if not Generator_recursiveConnect (parent_log = log):
                    exit ()
                connection_status = UP
                connection_mutex.notify ()
                #log.debug ("GENERATOR Successfully reconnected")

        with writing_config_semaphore:
            status_ok = Generator_getConfig (parent_log = log)

        if status_ok:
            with data_mutex:
                data_mutex.notify ()

        else:
            #log.debug ("[DEBUG]    (Generator_Query_Thread) >   ENTRA EN DOWN 2")
            connection_status = DOWN

            log.debug ("Connection DOWN") 


def Server_Post_Thread(print_lock):

    global execute_threads

    global data_mutex
    global server_com_mutex

    global data
    global spectrum

    log = Log (func_name = "Server_Post_Thread", print_lock = print_lock)

    log.debug ("Starting Thread")

    while execute_threads:

        # Este thread solo enviará la info cuando la misma esté lista ( ver data_mutex.notify() en Generator_Query_Thread)
        with data_mutex:
            data_mutex.wait()

            if execute_threads == False:
                exit()
                
            # Se conforma el diccionario con la info que le será enviada al servidor
            data = deepcopy (generator_log_dict)

            data_sent = False
            while (not data_sent) and execute_threads:

                answer = False
                try:
                    with server_com_mutex:
                        answer = post (
                            url = str ("http://localhost:" + SERVER_PORT + SERVER_GENERATOR_UPDATE_URL),
                                json = data)

                except:
                    log.error ("Error when trying to post to Server, Maybe is it down? Response: " + str (answer))
                    sleep (1)
                else:
                    data_sent = True


#   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --


#  ------>  GET FROM SERVER AND CONFIG GENERATOR

cmd_list = []

def Generator_Config_Thread (print_lock):

    global execute_threads

    global config_mutex
    global connection_status
    global writing_config_semaphore

    global commands
    global cmd_list

    log = Log (func_name = "Generator_Config_Thread", print_lock = print_lock)

    log.debug ("Starting Thread")

    while execute_threads:

        if connection_status == UP:

            with config_mutex:
                config_mutex.wait()  # Espera a que "Server_Get_Thread" lo habilite
                if execute_threads == False:
                    exit()

                # Adds to the command list new commands (if not repeated)
                cmd_list.extend(list(set(commands)-set(cmd_list)))

            #log.debug ("[DEBUG - INFO] (Generator_Config_Thread)    >   CMD LIST:",__DEBUG_ONLY_THIS__)
            # #log.debug (("\n".join(cmd_list)),__DEBUG_ONLY_THIS__)

            if cmd_list:  # If list not empty

                sent_cmds = []

                with writing_config_semaphore:
                    for cmd in cmd_list:

                        cmd_sent = False
                        # Loops until the command is sent
                        while (not cmd_sent) and (execute_threads) and cmd:

                            #log.debug ("[DEBUG - INFO] (Generator_Config_Thread)    >   BEFORE WRITING")
                            # Tries to write
                            cmd_sent = Generator_writeCommand(cmd=cmd, parent_log = log)
                            #log.debug ("[DEBUG - INFO] (Generator_Config_Thread)    >   AFTER WRITING")

                            if cmd_sent:
                                #log.debug ("[DEBUG - INFO] (Generator_Config_Thread)    >   SENT: "+cmd,__DEBUG_ONLY_THIS__)
                                sent_cmds.append(cmd)

                            # Generator_writeCommand(cmd=cmd) == False => ERROR
                            else:
                                #log.debug ("[DEBUG]    (Generator_Config_Thread) >   ENTRA EN DOWN 3")
                                connection_status = DOWN
                                while (connection_status == DOWN) and (execute_threads):
                                    with connection_mutex:
                                        connection_mutex.wait(
                                            CONNECTION_MUTEX_WAI_TIMEOUT)

                # Deletes from command list the commands that were sent
                cmd_list = list(set(cmd_list)-set(sent_cmds))

        else:   # IF connection_status == DOWN
            #log.debug ("[DEBUG]    (Generator_Config_Thread) >   ENTRA EN DOWN 4")
            while (connection_status == DOWN) and (execute_threads):
                with connection_mutex:
                    connection_mutex.wait(CONNECTION_MUTEX_WAI_TIMEOUT)


def Server_Get_Thread(print_lock):

    global execute_threads

    global config_mutex
    global server_com_mutex

    global commands

    log = Log (func_name = "Server_Get_Thread", print_lock = print_lock)

    log.debug("Starting Thread")

    log.debug("Getting info from Server")
    
    while execute_threads:

        sleep (SERVER_GET_CONFIG_POLLING_TIME)

        try:

            with config_mutex:
                with server_com_mutex:
                    commands = get("http://localhost:" +
                                   SERVER_PORT+SERVER_GENERATOR_GET_CFG_URL)
                commands = list(commands.json())

                if len(commands):
                    config_mutex.notify()

        except:
            log.debug("Error when trying to GET from Server, Maybe is it down?")




# --------------------------------------------------------------------------------------------------------------
#                                   INITIAL GENERATOR CONFIG

print_lock = Lock ()

# IF CTRL+C, then
def sigint_trap(sig, frame):
    global execute_threads
    global data_mutex
    global connection_mutex
    global config_mutex

    log = Log (func_name = "sigint_trap", print_lock = print_lock)

    execute_threads = False
    with data_mutex:
        data_mutex.notify()

    with connection_mutex:
        connection_mutex.notify()

    with config_mutex:
        config_mutex.notify()

    log.debug("\nCTRL+C Received, exiting...")

    exit ()


if __name__ == '__main__':
    
    log = Log (func_name = "Datalogger", print_lock = print_lock)

    signal(SIGINT, sigint_trap)

    with open("server_port.conf", "r") as f:
        SERVER_PORT = f.read().replace(" ", "")

    with open("generator_ip.conf", "r") as f:
        GENERATOR_IP = f.read().replace(" ", "").replace("\n", "")

    server_post_thread = Thread(target=Server_Post_Thread, args = (print_lock,))
    server_post_thread.start()
    generator_query_thread = Thread(target=Generator_Query_Thread, args = (print_lock,))
    generator_query_thread.start()

    server_get_thread = Thread(target=Server_Get_Thread, args = (print_lock,))
    server_get_thread.start()
    generator_config_thread = Thread(target=Generator_Config_Thread, args = (print_lock,))
    generator_config_thread.start()

    # Exiting logic
    cmd = False
    while (cmd!="exit") and (execute_threads): 
        log.info("Ingrese un comando cuando lo desee. Ingrese \"exit\" para cerrar el servidor.")
        cmd = input()

    execute_threads = False
    
    log.info("Exit command received, exiting datalogger...")
