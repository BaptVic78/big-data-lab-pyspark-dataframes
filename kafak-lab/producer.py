# %%
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

with open("book.txt", encoding="utf-8") as f:
    for line in f:
        producer.produce(
            topic=topic,
            value=line.encode("utf-8")
        )
        producer.poll(0)
        print(line.rstrip())
        time.sleep(1)

producer.flush()
producer.close()