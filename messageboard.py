# Copyright Douglas Squirrel 2011
# This program comes with ABSOLUTELY NO WARRANTY. 
# It is free software, and you are welcome to redistribute it under certain conditions; see the GPLv3 license in the file LICENSE for details.

import datetime, json, os, pika, time

def get_connection():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='kropotkin', type='topic')
    queue_name = channel.queue_declare(exclusive=True).method.queue
    return {'channel': channel, 'queue_name': queue_name}
    
def bind(connection, key):
    channel, queue_name = connection['channel'], connection['queue_name']
    channel.queue_bind(exchange='kropotkin', queue=queue_name, routing_key=key)

def start_consuming(connection, name, callback):
    channel, queue_name = connection['channel'], connection['queue_name']
    stop_key = 'stop.%s' % name
    def dispatch_message(channel, method, properties, body):
        if method.routing_key == stop_key:
            channel.stop_consuming()
            post(connection, key="process_stopped", body=name)
        else:
            callback(connection, body)
    
    bind(connection, stop_key)

    channel.basic_consume(dispatch_message, queue=queue_name, no_ack=True)
    post(connection, key="process_ready", body=name)
    channel.start_consuming()

def get_one_message(connection, seconds_to_wait=10):
    channel, queue_name = connection['channel'], connection['queue_name']
    for i in range(seconds_to_wait):
        method, properties, body = channel.basic_get(queue=queue_name, no_ack=True)
        if method.NAME != 'Basic.GetEmpty':
            return (method, body)
        time.sleep(1)
    return (None, None)

def post(connection, key, body=None):
    channel = connection['channel']
    channel.basic_publish(exchange='kropotkin', routing_key=key, body=body)
    print "PID=%s %s: %s %s" % (os.getpid(), datetime.datetime.now(), key, body)
