#include <SPI.h>
#include <MFRC522.h> // Bibliotheque utile pour detecter, lire des badges RFID

#define SS_PIN   10   // Broche Slave Select
#define RST_PIN  9    // Broche Reset
#define LED_VERT 7    // LED verte - acces autorise
#define LED_ROUGE 6   // LED rouge - acces refuse

MFRC522 mfrc522(SS_PIN, RST_PIN); // Instance de la classe MFRC522
void setup() {
  Serial.begin(9600);   // Initialiser la communication serie
  SPI.begin();          // Initialiser le bus SPI
  mfrc522.PCD_Init();// Appeler de la methode d'initialisation de mfrc522
                     // Indice : cherchez PCD_Init() dans la documentation
  pinMode(LED_VERT, OUTPUT);
  pinMode(LED_ROUGE, OUTPUT);
  Serial.println("Veuillez passer votre badge étudiant");
}

void loop() {
  if ( ! mfrc522.PICC_IsNewCardPresent()){
    return;
  }                                       // TODO : Verifier si un badge est present
                                          // Indice : utilisez mfrc522.PICC_IsNewCardPresent()
                                          // et mfrc522.PICC_ReadCardSerial()
                                          // Si aucun badge : retourner immediatement
  if ( ! mfrc522.PICC_ReadCardSerial()){
    return;
  }
  // TODO : Construire la chaine UID
  // L'UID se trouve dans mfrc522.uid.uidByte[]
  // et sa taille dans mfrc522.uid.size
  String uid = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    // TODO : Ajouter chaque octet en hexadecimal (2 chiffres, majuscules)
    uid += String(mfrc522.uid.uidByte[i], HEX); // Indice : utilisez String(mfrc522.uid.uidByte[i], HEX) et toUpperCase()
  }
  uid.toUpperCase();
  Serial.println("UID:" + uid);  // Format obligatoire pour Python

    // Attente de reponse python
    while (!Serial.available()) {
    delay(10);
  }

  String command = Serial.readStringUntil('\n');
  command.trim();

  if (command == "GREEN"){
    digitalWrite(7, HIGH);
    delay(1000);
    digitalWrite(7, LOW);
  }

  else if (command == "RED"){
    digitalWrite(6, HIGH);
    delay(1000);
    digitalWrite(6, LOW);
  }




  /* TODO : Allumer la LED verte 1 seconde puis l'eteindre
  digitalWrite(7, HIGH);
  delay(1000);
  digitalWrite(7, LOW);
  */
  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();

  delay(1500);  // Eviter les lectures multiples du meme badge
}
