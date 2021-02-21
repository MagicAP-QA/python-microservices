from bson.objectid import ObjectId
import pika, json

from main import mongo

#TODO change to local
params = pika.URLParameters('amqps://abrurlec:NVuz1ApXob9L6STGkhhR27pHCplBzcWQ@eagle.rmq.cloudamqp.com/abrurlec')

connection = pika.BlockingConnection(params)

channel = connection.channel()

channel.queue_declare(queue='main')


def callback(ch, method, properties, body):
    print('Received in main')
    data = json.loads(body)
    print(data)

    if properties.content_type == 'product_created':
        print("=====================****************")
        print(data)
        qry = {"title": data['title'], "image": data['image']}
        result = mongo.db.product.insert_one(qry)
        print(f'Product Created with id: {result.inserted_id}')

    elif properties.content_type == 'product_updated':
        # qry = {"_id": ObjectId(data['id'])}
        qry = {"_id": data['id']}
        newvalues = { "$set": { "title": data['title'],  'image': data['image']} }
        mongo.db.product.update_one(qry, newvalues)        
        print('Product Updated')

    elif properties.content_type == 'product_deleted':
        # qry = {"_id": ObjectId(data['id'])}
        qry = {"_id": data['id']}
        mongo.db.product.delete_one(qry)        
        print('Product Deleted')


channel.basic_consume(queue='main', on_message_callback=callback, auto_ack=True)

print('Started Consuming')

channel.start_consuming()

channel.close()
