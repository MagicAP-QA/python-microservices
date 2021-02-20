import pika, json

params = pika.URLParameters('amqps://abrurlec:NVuz1ApXob9L6STGkhhR27pHCplBzcWQ@eagle.rmq.cloudamqp.com/abrurlec')

connection = pika.BlockingConnection(params)

channel = connection.channel()


def publish(method, body):
    properties = pika.BasicProperties(method)
    channel.basic_publish(exchange='', routing_key='main', body=json.dumps(body), properties=properties)
