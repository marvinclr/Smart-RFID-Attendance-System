import serial
from dotenv import load_dotenv
import time
import re
import requests
import os


PORT = 'COM5'       
BAUD_RATE = 9600    # Serial.begin(9600) dans Arduino
TIMEOUT = 1         # Secondes d'attente maximum par lecture
load_dotenv()
API_KEY = os.getenv("CLE_API")

def parse_uid(raw_line):
    uid=""
    if not raw_line.startswith('UID:'):
        return None
    
    uid = raw_line[4:].strip()

    if re.match(r'^[0-9A-F]+$', uid):
        return uid   
    return None


def send_to_backend(uid, ser):
    try:
        url = "http://127.0.0.1:5000/scan"

        data = {"badge_id": uid, "api_key": API_KEY}

        reponse = requests.post(url, json= data )  # envoyer requête

        print("Reponse serveur :", reponse.json())

        command=""
        data = reponse.json()
        status = data.get("status")
        if status == "granted":
            command = 'GREEN'
        else:
            command = 'RED'
        ser.write((command + "\n").encode())

    except Exception as e:
        print("Erreur :", e)




def read_rfid_loop():
    try:
        ser = serial.Serial(PORT, BAUD_RATE, timeout=TIMEOUT) # Assure la connection au moniteur série
        print(f'Connecte au port {PORT} a {BAUD_RATE} baud')

        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip() # Lis la premiere lignes du port serie et Decode avec .decode('utf-8', errors='ignore').strip()                                                             
            if line:  # Ignore les lignes vides
                uid = parse_uid(line)
                if uid:
                    print(f'[{time.strftime("%H:%M:%S")}] Badge detecte : {uid}')
                    send_to_backend(uid, ser)
                else:
                    print(line) # Affiche les autres lignes du moniteur serie ne correspondant pas a l'UID

    except serial.SerialException as e:
        print(f'Erreur serie : {e}')
    except KeyboardInterrupt:
        print('Arret demande par l utilisateur')
    finally:
        print("Le programme a été arreté")

if __name__ == '__main__':
    read_rfid_loop()
