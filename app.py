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
    """Hache un UID avec SHA-256. A implementer en Phase 6."""
    return hashlib.sha256(uid.encode()).hexdigest() # Convertie le badge brut en son hash

def validate_badge_id(badge_id):
    if len(badge_id) != 0 and re.match(r'^[0-9A-F]+$', badge_id) and 4 <= len(badge_id) <= 20:
        return True
    return False

@app.route('/scan', methods=['POST'])
def scan():
    """
    Route principale de scan RFID.
    Recoit : { 'badge_id': 'A3F2B1C4', 'api_key': '...' }
    Retourne : { 'status': 'granted'/'denied', 'message': '...' }
    """
    data = request.get_json()

    if data is None: # Verifie que data n'est pas None
        return jsonify({"erreur": "Pas de données JSON trouver"}), 400


    badge_id = data.get("badge_id") # Verifie la presence de 'badge_id' dans data
    if not badge_id: # Verifie si badge_id est None ou vide
        return jsonify({"erreur": "Le badge_id est manquant"}), 400 


    if (data.get('api_key') != API_KEY):
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
       # database.log_access(badge_id, action="scan", status="denied", ip_source=request.remote_addr)
       # return jsonify({"status": "denied", "message": "badge inconnu"}), 200
    #else:
        #database.log_access(badge_id, action="scan", status="granted", ip_source=request.remote_addr)
        #return jsonify({"status": "granted", "message": "accès autorisé"}), 200
    # TODO : Enregistrer l'evenement (Phase 4/5)

"""
def test_hash(badge_id):
    b_b = badge_id
    b_h = hash_uid(b_b)
    print(f"Badge brut: {b_b} | Badge hash: {b_h} | Le badge brut genere toujours le meme hash : {b_h == b_h}")
"""
    
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

    #test_hash('A3F2B1C4')
    database.init_db()  # Cree les tables si elles n'existent pas
    app.run(debug=True, port=5000)
