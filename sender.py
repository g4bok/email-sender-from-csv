import csv
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pywhatkit
import datetime
import time

def send_email(email_address, message):
    """
    Invia un'email al paziente utilizzando SMTP
    """
    
    sender_email = os.environ.get("EmailCheSmalto")
    if not sender_email:
        print("❌ Errore: la variabile d'ambiente 'EmailCheSmalto' non è impostata.")
        return False
    
    password = os.environ.get("PassCheSmalto")
    if not password:
        print("❌ Errore: la variabile d'ambiente 'PassCheSmalto' non è impostata.")
        return False

    # Creazione del messaggio
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = email_address
    msg["Subject"] = "Torna a trovarci – Abbiamo un regalo per te! 🎁🦷"

    # Aggiungi il messaggio al corpo dell'email
    msg.attach(MIMEText(message, "plain"))

    try:
        # Connessione al server SMTP
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # Sicurezza della connessione
        server.login(sender_email, password)

        # Invio email
        server.send_message(msg)
        print(f"✓ Email inviata con successo a {email_address}")

        # Chiusura connessione
        server.quit()
        return True
    except Exception as e:
        print(f"❌ Errore nell'invio dell'email a {email_address}: {str(e)}")
        return False



def send_whatsapp(phone_number, message):
    """
    Invia un messaggio WhatsApp utilizzando pywhatkit
    """
    try:
        # Formatta il numero di telefono (rimuovi spazi, trattini, ecc.)
        clean_number = ''.join(filter(str.isdigit, phone_number))
        
        # Aggiungi il prefisso internazionale se non presente
        if not clean_number.startswith('+'):
            clean_number = '+39' + clean_number  # Presumo prefisso italiano, modificalo se necessario
        
        # Imposta orario di invio (tra 1 minuto)
        now = datetime.datetime.now()
        hour = now.hour
        minute = (now.minute + 1) % 60  # Incrementa di 2 minuti per sicurezza

        # Se il minuto è 0, incrementa l'ora
        if now.minute + 1 >= 60:
            hour = (hour + 1) % 24

        print(f"Invio messaggio a {clean_number} alle {hour}:{minute}")

        # Invia il messaggio WhatsApp
        pywhatkit.sendwhatmsg(clean_number, message, hour, minute, wait_time=15)
        print(f"✓ Messaggio WhatsApp inviato con successo a {phone_number}")
        
        # Attendi un po
        # ' per non sovraccaricare WhatsApp
        time.sleep(10)
        return True
    except Exception as e:
        print(f"❌ Errore nell'invio del messaggio WhatsApp a {phone_number}: {str(e)}")
        return False
    

def process_patients_file(csv_path, message):
    """
    Legge il file CSV dei pazienti e invia i messaggi appropriati
    """
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        
        for row in csv_reader:
            print(row.get('Telefono'))
            patient_name = row.get('Nome', '') + ' ' + row.get('Cognome', '')
            email = row.get('Email', '').strip()
            phone = row.get('Telefono', '').strip()
            
            # Personalizza il messaggio per ogni paziente
            personalized_message = f"Gentile {patient_name},\n\n{message}"
            
            # Se è disponibile l'email, invia per email
            if email:
                print(f"📧 Inviando email a {patient_name} ({email})...")
                send_email(email, personalized_message)
            # Altrimenti, se è disponibile il numero di telefono, invia su WhatsApp
            elif phone:
                send_whatsapp(phone, personalized_message)
            else:
                print(f"⚠️ Nessun contatto disponibile per {patient_name}")

def main():
    # Configurazione
    csv_file = "test.csv"
    
    # Messaggio da inviare
    message = """Che Smalto! è felice di averti tra i suoi pazienti e per questo vorrebbe ringraziarti per la fiducia che gli hai accordato nel prenderti cura del tuo sorriso.

Per questo motivo, ha pensato a una promozione esclusiva solo per i suoi pazienti abituali:
🎉 Solo per questa promozione la tua prossima seduta di igiene dentale professionale ti costerà 69,00€!!!! Solo fino al 31 maggio 2025.

✨ E non finisce qui!
Se porti un amico o un familiare che non è ancora nostro paziente,
riceverete entrambi un ulteriore 10% di sconto sul vostro prossimo trattamento!

Un piccolo regalo per dire grazie… e per continuare a far sorridere chi ti sta vicino 😊

👉 Prenota il tuo appuntamento (e segnala chi porterai con te!): Prenota cliccando https://prenota.alfadocs.com/p/porto-torres-che-smalto--25179 oppure chiamando il numero 3291133429.

⚠️ Promozione valida fino al [31/05/2025] – non lasciartela scappare!

Grazie ancora per la tua fiducia,
A presto!
Dott.ssa Luciana Chessa

Che Smalto!
Via Azuni, 17 Porto Torres SS
Email: chesmalto.id@gmail.com
Telefono: 3291133429
"""
    
    # Verifica che il file esista
    if not os.path.exists(csv_file):
        print(f"❌ Il file {csv_file} non esiste!")
        return
    
    # Elabora il file e invia i messaggi
    print("\n📤 Avvio l'invio dei messaggi...")
    process_patients_file(csv_file, message)
    print("\n✅ Processo completato!")

if __name__ == "__main__":
    # Richiede l'installazione di pywhatkit: pip install pywhatkit
    print("📱 Sistema di notifica pazienti")
    print("-------------------------------")
    main()
