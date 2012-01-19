# Copyright Douglas Squirrel 2011
# This program comes with ABSOLUTELY NO WARRANTY. 
# It is free software, and you are welcome to redistribute it under certain conditions; see the GPLv3 license in the file LICENSE for details.

import messageboard

def mock(mb, message):
    global queue
    if message.key == 'mock':
        message_key = str(message.content['message_key'])
        response_key = str(message.content['response_key'])
        mocks[message_key] = {'key': response_key}

        if 'response_content' in message.content:
            mocks[message_key]['content'] = message.content['response_content']
        else:
            mocks[message_key]['content'] = None

        if 'correlation_id' in message.content:
            mocks[message_key]['correlation_id'] = str(message.content['correlation_id'])
        else:
            mocks[message_key]['correlation_id'] = None

        mb.watch_for(keys=[message_key], queue=queue)
        mb.post(key='ready_to_mock.%s' % message_key)
    elif message.key in mocks:
        correlation_id = message.correlation_id if (mocks[message.key]['correlation_id'] is None) else mocks[message.key]['correlation_id']
        mb.post(key=mocks[message.key]['key'], content=mocks[message.key]['content'], correlation_id=correlation_id)
        del mocks[message.key]

mocks = {}
mb = messageboard.MessageBoard()
queue = mb.watch_for(keys=['mock'])
mb.post(key='process_ready.mocker')
mb.start_receive_loop(queue, callback=mock)
