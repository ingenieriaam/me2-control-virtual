# -*- coding: utf-8 -*-

from uuid import uuid4
from random import randint, random, uniform
from time import sleep

# -----------------------------------------------------------------------------------

analyzer_cmd_dict = {
                "spectrum"      : ":TRACe:DATA? TRACE1",
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
                "freq_or_span"  : "",
                "visa_command"  : ""
                }
                
analyzer_log_dict = {
                "spectrum"      : [],
                "x_scale"       : "",
                "y_scale"       : "",
                "start_freq"    : 99650000.0,
                "stop_freq"     : 100150000.0,
                "span"          : 0.0,
                "center_freq"   : 0.0,
                "ref_level"     : 0.0,
                "demod_time"    : 0.0,
                "demod_type"    : "",
                "input_att"     : 0,
                "res_bw"        : 0.0,
                "scale_div"     : 10,
                "freq_or_span"  : "",
                "visa_command"  : ""
                }


# Rate of failure. 1 time in X times
FAIL_RATE_1_IN_     =   20

# DO NOT MODIFY
SIMULATE_FAIL_ON    =   FAIL_RATE_1_IN_
SIMULATE_FAIL_OFF   =   FAIL_RATE_1_IN_ + 10    # IF  FAIL_RATE_1_IN_ + (>= 1)  =>  Never "fails"

# Set only SIMULATE_FAIL_ON or SIMULATE_FAIL_OFF to ENABLE / DISABLE failures simulation
SIMULATE_FAIL   =   SIMULATE_FAIL_OFF

# ENABLE / DISABLE OUTPUTS
DO_WRITE_WRITE_ANSWER_TO_FILE   =   False
DO_WRITE_QUERY_ANSWER_TO_FILE   =   False
DO_PRINT_WRITE_ANSWER_IN_SCREEN =   False
DO_PRINT_QUERY_ANSWER_IN_SCREEN =   False

# SIMULATED DELAYS

MIN_SIM_CONNECTION_DELAY    = 0
MAX_SIM_CONNECTION_DELAY    = 3

MIN_SIM_TRACE_QRY_DELAY     = 0
MAX_SIM_TRACE_QRY_DELAY     = 1

MIN_SIM_OTHERS_QRY_DELAY    = 0
MAX_SIM_OTHERS_QRY_DELAY    = 0.5

MIN_SIM_OTHERS_WRITE_DELAY  = 0
MAX_SIM_OTHERS_WRITE_DELAY  = 0.3

# -----------------------------------------------------------------------------------

def connectToResource(resource_ip, resource_name="Device"):

    resource = False

    # Simulates delay
    sleep(uniform(MIN_SIM_CONNECTION_DELAY,MAX_SIM_CONNECTION_DELAY))

    # Randomly, generates a failure (or not)
    NOT_A_FAILURE = (uniform(1,FAIL_RATE_1_IN_) != SIMULATE_FAIL)

    if NOT_A_FAILURE:

        # Randomly generated string to identify the resource, starts with a "0" for easier handling the files
        resource = "0"+str(uuid4()) 

        print("[DEBUG - INFO] (connectToResource): "+resource)

    return resource


def writeCommandToResource(resource, resource_name="Device", cmd="*IDN?"):

    NOT_A_FAILURE = (uniform(1,FAIL_RATE_1_IN_) != SIMULATE_FAIL)

    if NOT_A_FAILURE:   # Simula escritura correcta
        
        # Simulates delay
        sleep(uniform(MIN_SIM_OTHERS_WRITE_DELAY,MAX_SIM_OTHERS_WRITE_DELAY))

        if DO_WRITE_WRITE_ANSWER_TO_FILE:
            with open(resource+"_w.log","a+") as f:
                f.write(cmd+"\n") # Guarda los comandos en un log
        if DO_PRINT_WRITE_ANSWER_IN_SCREEN:
            print("**\""+cmd+"\"**")
        
        for key in analyzer_cmd_dict:
            if (analyzer_cmd_dict[key].split(" ")[0]==cmd.split(" ")[0]):
                analyzer_log_dict[key] = cmd.split(" ")[1]
                break
        
        return True

    # Simulates failure in the connection
    else:
        # Simulates delay
        sleep(uniform(1,5))
        return False

def queryCommandToResource(resource, resource_name="Device", cmd="*IDN?"):

    NOT_A_FAILURE = (uniform(1,FAIL_RATE_1_IN_) != SIMULATE_FAIL)

    answer = "ERROR"

    if NOT_A_FAILURE:   # Simula escritura correcta
        
        if DO_WRITE_QUERY_ANSWER_TO_FILE:
            with open(resource+"_q.log","a+") as f:
                f.write(cmd+"\n")   # Guarda los comandos en un log
        if DO_PRINT_QUERY_ANSWER_IN_SCREEN:
            print("**\""+cmd+"\"**")

        if  (":TRACe:DATA? TRACE1" == cmd):
            
            var = randint(0,7)  # Hay 8 Datalogs para iterar, del 0 al 7
            with open("datalogs/data"+str(var)+".log","r") as f:
                answer = f.read().split(",")

            analyzer_log_dict["start_freq"] = float(answer[1])
            analyzer_log_dict["stop_freq"]  = float(answer[2])
            analyzer_log_dict["ref_level"]  = float(answer[4])
            y_bottom                        = float(answer[3])
            analyzer_log_dict["scale_div"]  = (analyzer_log_dict["ref_level"]-y_bottom)/10

            s       = answer[5:]
            answer  = ','.join(map(str, s))     

            # Simulates delay
            sleep(uniform(MIN_SIM_TRACE_QRY_DELAY,MAX_SIM_TRACE_QRY_DELAY))

        elif ("*IDN?" == cmd):
            answer = str(resource+"_device")

        else:
            # Simulates delay
            sleep(uniform(MIN_SIM_OTHERS_QRY_DELAY,MAX_SIM_OTHERS_QRY_DELAY))

            for key in analyzer_cmd_dict:
                if (analyzer_cmd_dict[key].split(" ")[0]==cmd.split("?")[0]):
                    answer = analyzer_log_dict[key]
                    break

        return True, str(answer)

    # Simulates failure in connection
    else:
        # Simulates delay
        sleep(uniform(1,5))
        print("[DEBUG - ERROR]  > "+resource_name+": Error when trying to write")
        return False, "Wrong Answer"