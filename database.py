import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "rfid_system.db")

print("DB utilisée :", DB_PATH)

def get_connection():
    """Retourne une connexion a la base de donnees."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Acces par nom de colonne
    return conn




def init_db():
    """Cree les tables si elles n'existent pas."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY AUTOINCREMENT" \
                                                      ", badge_hash TEXT NOT NULL  UNIQUE " \
                                                      ", nom TEXT NOT NULL" \
                                                      ", prenom TEXT NOT NULL" \
                                                      ", groupe TEXT" \
                                                      ", actif INTEGER DEFAULT 1" \
                                                      ", created_at TEXT DEFAULT (datetime('now')))")

    cur.execute("CREATE TABLE IF NOT EXISTS access_logs (id INTEGER PRIMARY KEY AUTOINCREMENT" \
                                                      ", badge_hash TEXT NOT NULL " \
                                                      ", action TEXT NOT NULL" \
                                                      ", timestamp TEXT DEFAULT (datetime('now')) " \
                                                      ", status TEXT NOT NULL" \
                                                      ", ip_source TEXT " \
                                                      ", duration_minutes  REAL  DEFAULT NULL " \
                                                      ", FOREIGN KEY (badge_hash) REFERENCES students(badge_hash))")
    conn.commit()
    conn.close() # Ferme la connexion




def get_student_by_badge(badge_hash):
    """Retourne l'etudiant correspondant au badge_hash, ou None."""
    conn = get_connection() # Ouvre la connexion
    cur = conn.cursor() 
    res = cur.execute("SELECT nom, prenom FROM  students WHERE students.badge_hash = ?",(badge_hash,)) # utilisation de parametres lies (?) pour eviter les sql injection {badges_hash}
    ligne = res.fetchone()
    conn.close() # Ferme la connexion
   
    if ligne:
        return ligne
    return None


def log_access(badge_hash, action, status, ip_source=None, duration_minutes=None):
    """Enregistre un evenement d'acces dans access_logs."""

    conn = get_connection() # Ouvre la connexion
    cur = conn.cursor() 
    cur.execute("INSERT INTO access_logs (badge_hash, action, status, ip_source, duration_minutes) \
                      VALUES (?, ?, ?, ?, ?)",(badge_hash, action, status, ip_source, duration_minutes))
    conn.commit()
    conn.close() # Ferme la connexion



def get_last_action(badge_hash):
    """
    Retourne la derniere action enregistree pour ce badge.
    Utilise en Phase 5 pour detecter entree/sortie.
    """
    conn = get_connection() # Ouvre la connexion
    cur = conn.cursor() 
    res = cur.execute("SELECT action FROM access_logs WHERE badge_hash = ? " \
                        "ORDER BY timestamp DESC LIMIT 1",(badge_hash,))
    ligne = res.fetchone() # ligne = {"action": "entry"} 
    conn.close() # Ferme la connexion
    if ligne:
        return ligne["action"]
    return None


    

def get_all_access_logs(limit=100):
    """Retourne les derniers acces pour le tableau de bord."""
    conn = get_connection() # Ouvre la connexion
    cur = conn.cursor() 
    res = cur.execute("SELECT nom, prenom, access_logs.action, access_logs.timestamp, status FROM access_logs" \
                        " JOIN students ON students.badge_hash = access_logs.badge_hash" \
                        " ORDER BY timestamp DESC" \
                        " LIMIT ?",(limit,))
    ligne = res.fetchall()
    conn.close()
    return ligne

def process_scan(badge_hash, ip_source=None):
    conn = get_connection() # Ouvre la connexion
    cur = conn.cursor() 
    res = cur.execute("SELECT timestamp FROM access_logs" \
                      " WHERE action = 'entry' AND access_logs.badge_hash = ?" \
                     " ORDER BY timestamp DESC LIMIT 1",(badge_hash,))
    row = res.fetchone()
    conn.close()
    if row:
        last_timestamp = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S') #temps de la derniere entrée convertie de string a datetime
    else:
        last_timestamp = None
    act = get_last_action(badge_hash)
    if not act or act == 'exit':
        action = 'entry'
        duration_minutes = None

        log_access(badge_hash, action, "granted", ip_source, duration_minutes)

        return {
                "action": action,
                "status": "granted",
                "message": "Entree d'eleve", 
                "duration_minutes": duration_minutes
                }

    elif act == 'entry':
        action = 'exit'

        if last_timestamp:
            now = datetime.now()
            duration = now - last_timestamp
            duration_minutes = "{:.2f}".format(duration.total_seconds() / 60)
    
        else:
            duration_minutes = None
        log_access(badge_hash, action, "granted", ip_source, duration_minutes)

        return {
                "action": action,
                "status": "granted",
                "message": "Sortie d'eleve", 
                "duration_minutes": duration_minutes
                }
    return {
                "status": "denied",
                "message": "Accès refusé", 
                }


#"""
def add_student(badge_hash,nom, prenom, groupe, actif):
    #try:    
        conn = get_connection() # Ouvre la connexion
        cur = conn.cursor() 
        cur.execute("INSERT INTO students (badge_hash, nom, prenom, groupe, actif) \
                        VALUES (?, ?, ?, ?, ?)",(badge_hash, nom, prenom, groupe, actif))
        conn.commit()
        conn.close() # Ferme la connexion
    #execpt:

#"""

        

        