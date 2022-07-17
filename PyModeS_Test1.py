import pyModeS as pms
import socket
import time
import os
from os.path import exists
import json #https://www.w3schools.com/python/python_json.asp 
import gc



def updateJson(msg):
    
    if(len(msg) < 28):
        #short message (probably ACAS / TCAS), send to file - TODO
        return
    
    df = pms.decoder.adsb.df(msg)
    icao = (pms.decoder.adsb.icao(msg)).lower()
    print("msg:" + msg)
    print("icao = " + icao.lower())
    print("df = " + str(df))
    filenameJSON = icao + ".json"

    #if file doesnt exist, create it and fill with empty variables
    if(not exists(filenameJSON)):
        f = open(filenameJSON, 'a')
        #fill it with blank variables
        
        f.write('{"msg":"' + msg + '", "utcTime":' + str(round(time.time() * 1000)) + ',"df":' + str(df) + ',"tc":-1,"squawk":"-1","callsign":"-1","category":-1,"isOdd":-1,"lastSurfacePositionMessage":-1,"lastAirbornePositionMessage":-1,"surfaceSpeed":-1,"surfaceHeading":-1,"speedType":"-1","altitude":-1,"altitudeDiff":-1,"airborneSpeed":-1,"airborneHeading":-1,"verticalSpeed":-1,"aircraftLat":-1.0,"aircraftLng":-1.0}\n')
        f.close()
        
    
    #find last line in file
    #https://www.codingem.com/how-to-read-the-last-line-of-a-file-in-python/
    
    with open(filenameJSON, "rb") as file:
        try:
            file.seek(-2, os.SEEK_END)
            while file.read(1) != b'\n':
                file.seek(-2, os.SEEK_CUR)
        except OSError:
            file.seek(0)
        #decode from a byte array to a string
        lastLine = file.readline().decode()
        
    #decode that string to a json file
    lastAircraftData = json.loads(lastLine)

    #update local variables
    oldUtcTime = lastAircraftData["utcTime"]
    squawk = lastAircraftData["squawk"]
    callsign = lastAircraftData["callsign"]
    category = lastAircraftData["category"]
    isOdd = lastAircraftData["isOdd"]
    lastSurfacePositionMessage = lastAircraftData["lastSurfacePositionMessage"]
    lastAirbornePositionMessage = lastAircraftData["lastAirbornePositionMessage"]
    surfaceSpeed = lastAircraftData["surfaceSpeed"]
    surfaceHeading = lastAircraftData["surfaceHeading"]
    speedType = lastAircraftData["speedType"]
    altitude = lastAircraftData["altitude"]
    altitudeDiff = lastAircraftData["altitudeDiff"]
    airborneSpeed = lastAircraftData["airborneSpeed"]
    airborneHeading = lastAircraftData["airborneHeading"]
    verticalSpeed = lastAircraftData["verticalSpeed"]
    aircraftLat = lastAircraftData["aircraftLat"]
    aircraftLng = lastAircraftData["aircraftLng"]





    
    if(df == 4):
        #altitude code
        x = False
        del x
        #idk how this is different from the other "Altitude"
        #but it throws an error when I use it
        #so im not using it
        
    elif(df == 5):
        #squawk code
        squawk = pms.common.idcode(msg)
        print("squawk = " + squawk)
        
        
    elif(df == 17):
        tc = pms.decoder.adsb.typecode(msg)
        print("tc: " + str(tc))
        
        if(tc >= 1 and tc <= 4):
            #aircraft identification and catagory
            callsign = pms.decoder.bds.bds08.callsign(msg)
            catagory = pms.decoder.bds.bds08.category(msg)
            print("callsign/catagory: " + callsign + "," + str(catagory))
            
        elif(tc >= 5 and tc <= 8):
            #surface position
            isOdd = pms.decoder.adsb.oe_flag(msg)
            surfaceSpeed, surfaceHeading, justZero, speedType = pms.decoder.bds.bds06,surface_velocity(msg)
            print("speed = " + str(surfaceSpeed) + ", heading = " + str(surfaceHeading) + ", type = " + str(speedType))
            print("position odd/even (0/1): " + str(isOdd))
            
        elif(tc >= 9 and tc <= 18):
            #airborne position

            #save isOdd and update from new msg
            oldOddFlag = isOdd
            isOdd = pms.decoder.adsb.oe_flag(msg)
            print("position odd/even (0/1): " + str(isOdd))
            
            if(aircraftLat != -1 and aircraftLng != -1):#if we have previous coords, use them
                aircraftLat, aircraftLng = pms.decoder.bds.bds05.airborne_position_with_ref(msg,aircraftLat,aircraftLng)
                print("Lat/Lng: " + str(aircraftLat) + " / " + str(aircraftLng))
                
            elif(lastAirbornePositionMessage != "-1" and oldOddFlag != isOdd and oldOddFlag != -1): #we have a previous message and odd flags are different, find coords
                if(oldOddFlag == 0):
                    aircraftlat, aircraftLng = pms.decoder.bds.bds05.airborne_position(lastAirbornePositionMessage, msg, oldUtcTime, round(time.time() * 1000))
                else: #just flip odd/even pair
                    aircraftLat, aircraftLng = pms.decoder.bds.bds05.airborne_position(msg, lastAirbornePositionMessage, round(time.time() * 1000), oldUtcTime)
                print("Lat/Lng: " + str(aircraftLat) + " / " + str(aircraftLng))
                
            altitude = pms.decoder.bds.bds05.altitude(msg)
            print("altitude: " + str(altitude))
            
            lastAirbornePositionMessage = msg
            del oldOddFlag
            
            
            
        elif(tc == 19):
            #airborne velocity
            airborneSpeed, airborneHeading, verticalSpeed, speedType = pms.decoder.bds.bds09.airborne_velocity(msg)
            altitude_difference = pms.decoder.bds.bds09.altitude_diff(msg)
            print("airspeed: " + str(airborneSpeed) + ", heading:" + str(airborneHeading) + ", VS:" + str(verticalSpeed) + ", " + speedType)
            print("alt diff: " + str(altitude_difference))
            
        elif(tc == 28):
            #airborne staus (to be added)
            print("TC=28 - " + msg)
        elif(tc == 29):
            #target state and status info
            print("TC=29 - " + msg)
            
        elif(tc == 31):
            #aircraft operational status
            print("TC=31 - " + msg)
        else:
            #unknown message
            print("unknown message: " + msg)


    #create new json with updated variables
    newAircraftdata = {"msg":msg,
                       "utcTime":round(time.time() * 1000),
                       "df":df,
                       "tc":tc,
                       "squawk":squawk,
                       "callsign":callsign,
                       "category":category,
                       "isOdd":isOdd,
                       "lastSurfacePositionMessage":lastSurfacePositionMessage,
                       "lastAirbornePositionMessage":lastAirbornePositionMessage,
                       "surfaceSpeed":surfaceSpeed,
                       "surfaceHeading":surfaceHeading,
                       "speedType":speedType,
                       "altitude":altitude,
                       "altitudeDiff":altitudeDiff,
                       "airborneSpeed":airborneSpeed,
                       "airborneHeading":airborneHeading,
                       "verticalSpeed":verticalSpeed,
                       "aircraftLat":aircraftLat,
                       "aircraftLng":aircraftLng
                       }
    #now all variables are updated, put back into string and append to file
    f = open(filenameJSON, 'a')
    jsonText = json.dumps(newAircraftdata) + "\n"
    f.write(jsonText)
    f.close()

    del newAircraftdata
    del lastAircraftData
    del msg
    del oldUtcTime
    del squawk
    del callsign
    del category
    del isOdd
    del lastSurfacePositionMessage
    del lastAirbornePositionMessage
    del surfaceSpeed
    del surfaceHeading
    del speedType
    del altitude
    del altitudeDiff
    del airborneSpeed
    del airborneHeading
    del verticalSpeed
    del aircraftLat
    del aircraftLng
    del lastLine
    del df
    del icao
    gc.collect()




inputKind = input()
if(inputKind == 'f'): #file
    with open("ADS-B_HEX.txt") as file:
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]
    for data in lines:
        if(len(data) < 28): #FIX THIS, the 14 char messages are there, idk what to do with them tho
            continue
        print("--------------------------------------")
        input()
        currentTime = round(time.time() * 1000)
        updateJson(data)






            

elif(inputKind == 'r'): #radio
    while True:
        UDP_IP = "127.0.0.1" #localhost address
        UDP_PORT = 31022 #port jetvision RTL1090 DVB-T to Mode S converter uses
        sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sock.bind((UDP_IP, UDP_PORT))

        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        byte_array = bytearray(data)
        #print("received message: %s" % data)
        recievedData = ''.join('{:02x}'.format(x) for x in byte_array)
        recievedData = recievedData[18:] #just want from 18 chars in to the end (first 18 are UDP stuffs i think)
        currentTime = round(time.time() * 1000)
        f = open("ADS-B_HEX.txt", "a")
        f.write(str(currentTime) + "," + recievedData + "\n")
        f.close()
        print(str(currentTime) + "," + recievedData)




















    


        
        
        
        
