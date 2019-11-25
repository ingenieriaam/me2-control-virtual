# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------------------------------------
#                                           IMPORTS

from os import popen
from time import sleep
from signal import signal, SIGINT
from requests import post, get, Request
from threading import Thread, Lock, Condition, Event
#from pyvisa_utils import connectToResource, writeCommandToResource, queryCommandToResource
from simulador_pyvisa_utils import connectToResource, writeCommandToResource, queryCommandToResource

# --------------------------------------------------------------------------------------------------------------
#                                       POWMETER'S GLOBALS

#   ---   ---   ---   ---   ---   ---   ---   ---   ---   ---   ---   ---
#   CONFIGURATION GLOBALS

__DEBUG__ = True
# If this Define is set to "True", only those "if" will be truth, not the ones with "__DEBUG__"
__DEBUG_ONLY_THIS__ = True

POWMETER_BW_RES = "1E3"
POWMETER_DISPLAY_ONOFF = "OFF"  # "ON"/"OFF"

CONNECTION_MUTEX_WAI_TIMEOUT = 0.5   # Seconds

SERVER_GET_CONFIG_POLLING_TIME = 0.5     # Seconds


#   ---   ---   ---   ---   ---   ---   ---   ---   ---   ---   ---   ---
#   FUNCTIONAL GLOBALS (DO NOT MODIFY!!, UNLESS YOU KNOW WHAT YOU ARE DOING)

data_mutex = Condition()
connection_mutex = Condition()
config_mutex = Condition()
powmeter_com_mutex = Lock()
server_com_mutex = Lock()
writing_config_semaphore = Lock()

SERVER_POWMETER_UPDATE_URL = "/pow_update/"
SERVER_POWMETER_GET_CFG_URL = "/get_powermeter_config/"

SERVER_PORT = ""
POWERMETER_IP = ""

data_readed = True

execute_threads = True

powmeter_resource = False

UP = True
DOWN = False
connection_status = DOWN

commands = Request()

power = 0

GET_POWER_CMD = "CWO 1" # TODO: o "CWO1" o "CWO 1?" o "CWO1?"....... probar cual corresponde

powmeter_cmd_dict = {
                "power"         : GET_POWER_CMD,
                "avg_times"     : "CWAVG 1,MOV,",
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

__DEBUG__ = (__DEBUG__ and (True != __DEBUG_ONLY_THIS__))

# --------------------------------------------------------------------------------------------------------------
#                                       POWMETER PRIMITIVES


def debug_print(msg="Default debug Message", debug_define=True):
    if debug_define:
        print(msg)

def Powmeter_queryCommand(cmd="*IDN?",dev_ip=""):
    
    global POWERMETER_IP

    global powmeter_com_mutex

    if dev_ip:
        POWERMETER_IP = dev_ip

    # Anritsu VISA FORM's URL
    URL = "http://"+POWERMETER_IP+"/ctl.html"
    # Curl's command
    curl_cmd = "curl '" + URL + "' --data 'cm=" + cmd + "+&q=" + "Query" + "' -s"
    print (curl_cmd)
    # Gets Curl's response (Raw HTML)
    try:
        with powmeter_com_mutex:
            response = popen(curl_cmd).read()
    except:
        answer = "ERROR"
        retval = False
    else:
        # Formats Curl's response to get the "answer"
        if response:
            answer = response.split('<textarea name="qr" id="qr" ')[1].split('</textarea')[0].split('>')[1]
            retval = True
        else:
            answer = "ERROR"
            retval = False

    return retval, answer

# q CWO 1/2
# w CHACTIV 1/2
# q CHACTIV?    -> CHACTIV 1/2
# w SNCFRQ A,50E6
# q CHUNIT? 1/2
# w CHUNIT 1/2,DBM/W/V
# w CWAVG 1, MOV, 32

def Powmeter_writeCommand(cmd="*IDN?",dev_ip=""):
    
    global POWERMETER_IP

    global powmeter_com_mutex

    if dev_ip:
        POWERMETER_IP = dev_ip

    # Anritsu VISA FORM's URL
    URL = "http://"+POWERMETER_IP+"/ctl.html"
    # Curl's command
    curl_cmd = "curl '" + URL + "' --data 'cm=" + cmd + "+&q=" + "Write" + "' -s"
    # Gets Curl's response (Raw HTML)
    try:
        with powmeter_com_mutex:
            try:
                response = popen(curl_cmd)
            except:
                print(response)
    except:
        answer = "ERROR"
        retval = False
    else:
        answer = response
        retval = True

    return retval, answer

# def Powmeter_writeCommand(cmd="*IDN?",dev_ip=POWERMETER_IP):

#     retval, answer = Powmeter_queryCommand(cmd=cmd)

#     #para borrar el warning
#     answer[0] = answer[0]

#     return retval


# Función que intenta conectarse al Analizador de forma recursiva, es bloqueante
def Powmeter_recursiveConnect():

    global powmeter_resource

    powmeter_resource = False

    __DEBUG__ = True

    print("ANTES DEL WHILE")
    while (powmeter_resource == False) and (execute_threads):
        print("EN EL WHILE")
        
        print("EN EL TRY: CMD = "+"*IDN? "+" IP = "+str(POWERMETER_IP))

        try:            
            retval, powmeter_resource = Powmeter_queryCommand(cmd="*IDN?",dev_ip=POWERMETER_IP)

            if retval:
                print(powmeter_resource)
            else:
                print("RETVAL FALSE")

        except:
            if __DEBUG__:
                print("[DEBUG - ERROR]  (Powmeter_recursiveConnect) >   Error when trying to connect to the Powmeter...")

            sleep(0.5)  # "Anti-Stress" Sleep

        else:
            if not powmeter_resource:
                powmeter_resource = False
                if __DEBUG__:
                    print("[DEBUG - ERROR]  (Powmeter_recursiveConnect) >   Error when trying to connect to the Powmeter...")

            sleep(0.5)  # "Anti-Stress" Sleep

    return False if (retval == False) else True


def Powmeter_getConfig():

    global powmeter_log_dict
    global powmeter_cmd_dict

    for key in powmeter_log_dict:

        retval = False
        answer = "ERROR"

        #retval, answer = Powmeter_queryCommand(powmeter_cmd_dict[key]+"?")  # TODO: Chequear esto que funcione, sino ver bien cómo se hace para el POWMETER

        if retval:
            powmeter_log_dict[key] = answer.replace("\n,", "")

    return retval

# --------------------------------------------------------------------------------------------------------------
#                                       POWMETER THREADS


#   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --


#  ------>  QUERY FROM POWMETER AND INFORM TO SERVER

def Powmeter_Query_Thread():

    global execute_threads

    global data_mutex
    global powmeter_com_mutex
    global connection_mutex
    global writing_config_semaphore

    global connection_status

    global powmeter_log_dict
    global powmeter_cmd_dict

    global power

    if __DEBUG__:
        print("[DEBUG - INFO]   (Powmeter_Query_Thread)     >   Starting Thread")

    while execute_threads:

        if connection_status == DOWN:
            with connection_mutex:
                if not Powmeter_recursiveConnect():
                    exit()
                connection_status = UP
                connection_mutex.notify()

        #with writing_config_semaphore:
            #status_ok = Powmeter_getConfig()

        if True: #status_ok:
            with writing_config_semaphore:
                status_ok, aux_power = Powmeter_queryCommand(GET_POWER_CMD)

            if status_ok:
                with data_mutex:
                    power = aux_power
                    print("POWERRRRRRRR : "+str(power)+powmeter_log_dict["ch_unit"])
                    data_mutex.notify()

            else:
                #debug_print("[DEBUG]    (Powmeter_Query_Thread) >   ENTRA EN DOWN 1")
                connection_status = DOWN

        if not status_ok:
            #debug_print("[DEBUG]    (Powmeter_Query_Thread) >   ENTRA EN DOWN 2")
            connection_status = DOWN


def Server_Post_Thread():

    global execute_threads

    global data_mutex
    global server_com_mutex

    global data

    if __DEBUG__:
        print("[DEBUG - INFO]   (Server_Post_Thread)    >   Starting Thread")

    while execute_threads:

        # Este thread solo enviará la info cuando la misma esté lista ( ver data_mutex.notify() en Powmeter_Query_Thread)
        with data_mutex:
            data_mutex.wait()

            if execute_threads == False:
                exit()

            # Se conforma el diccionario con la info que le será enviada al servidor
            data = {"power": power}

            data_sent = False
            while (not data_sent) and execute_threads:

                answer = False
                try:
                    with server_com_mutex:
                        answer = post(url=str("http://localhost:"+SERVER_PORT+SERVER_POWMETER_UPDATE_URL), json=data)

                except:
                    print(
                        "[DEBUG - ERROR]  (Server_Post_Thread)    >   Error when trying to post to Server, Maybe is it down? Response: "+str(answer))
                    sleep(1)

                else:
                    data_sent = True


#   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --   --


#  ------>  GET FROM SERVER AND CONFIG POWMETER

cmd_list = []


def Powmeter_Config_Thread():

    global execute_threads

    global config_mutex
    global connection_status
    global writing_config_semaphore

    global commands
    global cmd_list

    if __DEBUG__:
        print("[DEBUG - INFO]   (Powmeter_Config_Thread)    >   Starting Thread")

    while execute_threads:

        if connection_status == UP:

            with config_mutex:
                config_mutex.wait()  # Espera a que "Server_Get_Thread" lo habilite
                if execute_threads == False:
                    exit()

                # Adds to the command list new commands (if not repeated)
                cmd_list.extend(list(set(commands)-set(cmd_list)))

            #debug_print("[DEBUG - INFO] (Powmeter_Config_Thread)    >   CMD LIST:",__DEBUG_ONLY_THIS__)
            # #debug_print(("\n".join(cmd_list)),__DEBUG_ONLY_THIS__)

            if cmd_list:  # If list not empty

                sent_cmds = []

                with writing_config_semaphore:
                    for cmd in cmd_list:

                        cmd_sent = False
                        # Loops until the command is sent
                        while (not cmd_sent) and (execute_threads) and cmd:

                            #debug_print("[DEBUG - INFO] (Powmeter_Config_Thread)    >   BEFORE WRITING")
                            # Tries to write
                            cmd_sent = Powmeter_writeCommand(cmd=cmd)
                            #debug_print("[DEBUG - INFO] (Powmeter_Config_Thread)    >   AFTER WRITING")

                            if cmd_sent:
                                #debug_print("[DEBUG - INFO] (Powmeter_Config_Thread)    >   SENT: "+cmd,__DEBUG_ONLY_THIS__)
                                sent_cmds.append(cmd)

                            # Powmeter_writeCommand(cmd=cmd) == False => ERROR
                            else:
                                #debug_print("[DEBUG]    (Powmeter_Config_Thread) >   ENTRA EN DOWN 3")
                                connection_status = DOWN
                                while (connection_status == DOWN) and (execute_threads):
                                    with connection_mutex:
                                        connection_mutex.wait(
                                            CONNECTION_MUTEX_WAI_TIMEOUT)
                        
                        sleep(1)

                # Deletes from command list the commands that were sent
                cmd_list = list(set(cmd_list)-set(sent_cmds))

        else:   # IF connection_status == DOWN
            #debug_print("[DEBUG]    (Powmeter_Config_Thread) >   ENTRA EN DOWN 4")
            while (connection_status == DOWN) and (execute_threads):
                with connection_mutex:
                    connection_mutex.wait(CONNECTION_MUTEX_WAI_TIMEOUT)


def Server_Get_Thread():

    global execute_threads

    global config_mutex
    global server_com_mutex

    global commands

    if __DEBUG__:
        print("[DEBUG - INFO]   (Server_Get_Thread)     >   Starting Thread")

    while execute_threads:

        sleep(SERVER_GET_CONFIG_POLLING_TIME)

        try:

            with config_mutex:
                with server_com_mutex:
                    commands = get("http://localhost:" + SERVER_PORT+SERVER_POWMETER_GET_CFG_URL)
                commands = list(commands.json())

                if len(commands):
                    config_mutex.notify()

                    for command in commands:
                        print(command)

        except:
            print(
                "[DEBUG - ERROR]  (Server_Get_Thread) >   Error when trying to GET from Server, Maybe is it down?")


# --------------------------------------------------------------------------------------------------------------
#                                   INITIAL POWMETER CONFIG

# IF CTRL+C, then
def sigint_trap(sig, frame):
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

    print("\n[DEBUG - sigint_trap] CTRL+C Received, exiting...")

    exit()


if __name__ == '__main__':

    signal(SIGINT, sigint_trap)

    with open("server_port.conf", "r") as f:
        SERVER_PORT = f.read().replace(" ", "")

    with open("powmeter_ip.conf", "r") as f:
        POWERMETER_IP = f.read().replace(" ", "").replace("\n","")

    Powmeter_recursiveConnect()

    powmeter_query_thread = Thread(target=Powmeter_Query_Thread)
    powmeter_query_thread.start()
    server_post_thread = Thread(target=Server_Post_Thread)
    server_post_thread.start()

    server_get_thread = Thread(target=Server_Get_Thread)
    server_get_thread.start()
    powmeter_config_thread = Thread(target=Powmeter_Config_Thread)
    powmeter_config_thread.start()

    #   Exiting logic
    cmd = False
    while (cmd != "exit") and (execute_threads):
        cmd = input(
            "\n[DATALOGGER - INFO]    >   Ingrese un comando cuando lo desee. Ingrese \"exit\" para cerrar el servidor.\n\n")

    execute_threads = False

    print("[DATALOGGER - INFO]    >   Exit command received, exiting datalogger...")

    print("")
