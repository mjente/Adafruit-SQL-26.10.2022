# Importerer relevante bibliotek
import pyfirmata
from Adafruit_IO import Client, Feed, RequestError
import time
import datetime
import mysql.connector

#Definerer kva ip, brukernamn, passord og database som skal brukast.
mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "elev1234",
    database = "adafruit 26.10.2022"
)

# Sett inn brukernamn og 'Script' key henta frå dashboardet på Adafruit. 
ADAFRUIT_IO_USERNAME = "mjente"
ADAFRUIT_IO_KEY = "aio_klXB97Mypqy9HMi5Abktsmd8DKhE"

# Bruker brukernamnet og nøkkelen til å sette opp ein klient. 
aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

mycursor = mydb.cursor()

print("Connection to SQL established")

# Setter opp ein link og starta kommunikasjon med Arduino.
# Legg merke til at COM-port kan variere. 
board = pyfirmata.Arduino('COM5')
it = pyfirmata.util.Iterator(board)
it.start()

print("Connection to Arduino established...")

# Setter opp innganger og utganger fra Arduinoen.
led = board.get_pin('d:13:o')
analog_input = board.get_pin('a:0:i')


# Sjekker om der er ein feed ved namn "digital".
# Om der ikkje er ein lager den ein ny feed. 
try:
    digital = aio.feeds("digital")
except RequestError:
    feed = Feed(name = "digital")
    digital = aio.create_feed(feed)

try:
    analog = aio.feeds("analog")
except RequestError:
    feed = Feed(name = "analog")
    analog = aio.create_feed(feed)



while True:
    # data leser av "digital" feeden.
    data = aio.receive(digital.key)

    # Definerer kva å kor ting skal bli sendt til SQL.
    sql = "INSERT INTO sensor(verdi, tid) VALUES (%s, %s)"

    # Definerer verdi og tid til SQL. 
    verdi = analog_input.value
    tid = datetime.datetime.now()

    # Legger sammen verdi og tid til ein variabel so det kan lettere sendast til SQL.
    val = (verdi, tid)

    # Om data er på er led på, om ikkje er led av.
    if data.value == "ON":
        led.write(True)
    else:
        led.write(False)

    # Sender verdien av "analog_input" aka potensiometeret til "analog" feeden.
    aio.send_data("analog", analog_input.value)

    # Gjer klart der som skal sendast til SQL og sender det. 
    mycursor.execute(sql, val)
    mydb.commit()

    # Liten delay for å prøve å unngå "throttling" på Adafruit
    time.sleep(3)