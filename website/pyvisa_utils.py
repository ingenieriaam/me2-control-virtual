import pyvisa

# -----------------------------------------------------------------------------------

def connectToResource(resource_ip, parent_log=None, resource_name="Device"):
    
    Resource = False
    
    ResourcesManager = pyvisa.highlevel.ResourceManager()
    
    try:
        Resource = ResourcesManager.open_resource("TCPIP0::" + resource_ip + "::INSTR")

    except:
        Resource = False

    else:
        try:
            answer = Resource.query("*IDN?")
        except:
            Resource = False
        else:
            print("[DEBUG - INFO] (connectToResource): "+answer)
    
    return Resource



def writeCommandToResource(resource, parent_log=None, resource_name="Device", cmd="*IDN?"):

    try:
        resource.write(cmd)

    except:
        print("[DEBUG - ERROR]  > "+resource_name+": Error when trying to write")
        return False

    else:
        return True

def queryCommandToResource(resource, parent_log=None, resource_name="Device", cmd="*IDN?"):
    
    answer = False
    
    try:
        answer = resource.query(cmd)

    except:
        print("[DEBUG - ERROR]  > "+resource_name+": Error when trying to query: "+cmd)
        return False, answer

    else:
        answer = answer.rstrip()
        return True, answer
