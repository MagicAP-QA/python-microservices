import pika, json

#TODO change to local
# params = pika.URLParameters('amqps://abrurlec:NVuz1ApXob9L6STGkhhR27pHCplBzcWQ@eagle.rmq.cloudamqp.com/abrurlec')
credentials = pika.PlainCredentials('acmweb','acmweb')
params = pika.ConnectionParameters(host='localhost', port=2703, credentials=credentials)

connection = pika.BlockingConnection(params)

channel = connection.channel()


def publish(method, body):
    properties = pika.BasicProperties(method)
    channel.basic_publish(exchange='', routing_key='admin', body=json.dumps(body), properties=properties)
