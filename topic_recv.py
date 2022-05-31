import os 
import sys

import pika

RMQ_HOST = os.environ['RMQ_HOST']
RMQ_PASS = os.environ['RMQ_PASS']

assert len(sys.argv) >= 2, "Usage: python topic_recv.py [binding_key]..."
binding_keys = sys.argv[1:]

# RabbitMQ 패스워드로 크레덴셜
cred = pika.PlainCredentials('rabbit', RMQ_PASS)

# RabbitMQ 주소로 커넥션 초기화 
conn = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=RMQ_HOST,
        credentials=cred,
    )
)

# 채널 생성
chan = conn.channel()

chan.exchange_declare(exchange='top', exchange_type='topic')

res = chan.queue_declare(queue='', exclusive=True)
queue_name = res.method.queue
for bkey in binding_keys:
    chan.queue_bind(queue=queue_name, exchange='top', routing_key=bkey)

def callback(ch, method, prop, body):
    print("Recv", method.routing_key, body.decode('utf-8'))
    ch.basic_ack(delivery_tag=method.delivery_tag)

chan.basic_consume(queue_name, callback)
chan.start_consuming()