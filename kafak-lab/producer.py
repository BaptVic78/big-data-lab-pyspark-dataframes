# %%
import os
import socket
import time
from confluent_kafka import Producer
from datetime import datetime, timedelta


# %%
print(datetime.now().strftime("%H:%M"))
# %%
conf = {'bootstrap.servers': 'localhost:9092',
        'client.id': socket.gethostname()}

producer = Producer(conf)

# %%
topic='BookLecture'
# Seconds between two lines; set PRODUCER_DELAY=0 to send the whole book at once
delay = float(os.environ.get('PRODUCER_DELAY', '1'))

with open("book.txt", encoding="utf-8") as f:
    for line in f:
        producer.produce(
            topic=topic,
            value=line.encode("utf-8")
        )
        producer.poll(0)
        print(line.rstrip())
        time.sleep(delay)

producer.flush()
producer.close()