from flask import Flask, request, jsonify, render_template
import serial
from dotenv import load_dotenv
import os
import database
import hashlib
import time
import re

app = Flask(__name__)
load_dotenv()
API_KEY = os.getenv("CLE_API")


def hash_uid(uid):
    return hashlib.sha256(uid.encode()).hexdigest() # Convertie le badge brut en son hash

def validate_badge_id(badge_id):
    if len(badge_id) != 0 and re.match(r'^[0-9A-F]+$', badge_id) and 4 <= len(badge_id) <= 20:
        return True
    return False

def verify_api_key(data):
    if not data:
        return False
    api_key = data.get("api_key")
    return API_KEY == api_key
    



@app.route('/scan', methods=['POST'])
def scan():
    """ Route principale de scan RFID """
    data = request.get_json()

    if data is None: # Verifie que data n'est pas None
        return jsonify({"erreur": "Pas de données JSON trouver"}), 400


    badge_id = data.get("badge_id") # Verifie la presence de 'badge_id' dans data
    if not badge_id: # Verifie si badge_id est None ou vide
        return jsonify({"erreur": "Le badge_id est manquant"}), 400 


    if not verify_api_key(data):
        return jsonify({"erreur": "mauvaise clé API"}), 403 
    


    badge_id = data.get('badge_id', '').upper().strip()
    if not validate_badge_id(badge_id):
        return jsonify({"erreur": "Le format du badge_id n'est pas respecté"}), 400 
    badge_hash = hash_uid(badge_id)
    student = database.get_student_by_badge(badge_hash) # Verifie si le badge existe dans la base de donnees
    print("UID BRUT: ", badge_id)
    print("HASH CALC: ", badge_hash)

    if not student:
        database.log_access(badge_hash, action="None", status="denied", ip_source=request.remote_addr, duration_minutes=None)
        return jsonify({
                        "status": "denied",
                        "message": "Accès refusé", 
                        }), 200

    result = database.process_scan(badge_hash, ip_source=request.remote_addr)
    
    return jsonify(result)

    
@app.route('/health', methods=['GET'])
def health():
    """Route de verification - utile pour le debogage."""
    return jsonify({'status': 'ok', 'timestamp': time.time()})

if __name__ == '__main__':
    #"""
    nom = "Fayemi" 
    prenom = "Paterson"
    badge_hash = "2e56ca1971adcc5256bc6ea6c15dd033d40145adbb9bf2fd9000b04235ba1968"
    if database.add_student(badge_hash, nom, prenom, 'INFO3', 1):
        print(f"etudiant {nom} {prenom} ajouter dans la BDD")
    #"""
    database.init_db()  # Cree les tables si elles n'existent pas
    app.run(debug=True, port=5000)
