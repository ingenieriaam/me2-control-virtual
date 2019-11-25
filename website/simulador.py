from time import sleep
from requests import post, get

SERVER_PORT = str(8889)
SERVER_UPDATE_URL = "/update/"
SERVER_GET_CONFIG_URL = "/get_config/"

i = 0
while True:
    with open('data'+str(i)+'.log','r') as fr:
        file_data = fr.read().split(",")
        start_freq  = float(file_data[1])
        stop_freq   = float(file_data[2])
        bottom_y    = float(file_data[3])
        top_y       = float(file_data[4])
        lst_data    = file_data[5:]
        lst_data[0] = lst_data[0][12:]
        data = { "y":lst_data , "fi":start_freq, "ff":stop_freq, "yb":bottom_y, "yt":top_y }
        try:
            r = post(url=str("http://localhost:"+SERVER_PORT+SERVER_UPDATE_URL), json = data )
        except:
            print("[ERROR]  >   Error when trying to post to Server, Maybe is it down?")
            sleep(5)
        else:
            print("[INFO]   >   Data sent to Server")
        #with open('data.log','w') as fw:
            #fw.write(fr.read())
    
    try:
        commands = get("http://localhost:"+SERVER_PORT+SERVER_GET_CONFIG_URL)
    except:
        print("[ERROR]  >   Error when trying to get from Server, Maybe is it down?")
        sleep(5)
    else:
        print("[INFO]   >   Data queried from Server:")
        lista = list(commands.json())
        print(lista)

    sleep(1)

    i+=1
    if i==8:
        i = 0