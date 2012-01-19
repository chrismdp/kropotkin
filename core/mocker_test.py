# Copyright Douglas Squirrel 2011
# This program comes with ABSOLUTELY NO WARRANTY. 
# It is free software, and you are welcome to redistribute it under certain conditions; see the GPLv3 license in the file LICENSE for details.

import messageboard

def _register_mock(message_key, response_key, response_content=None, correlation_id=None):
    post_content={'message_key': message_key, 'response_key': response_key}
    if response_content is not None:
        post_content['response_content'] = response_content
    if correlation_id is not None:
        post_content['correlation_id'] = correlation_id
    return mb.post_and_check(post_key='mock', post_content=post_content, response_key='ready_to_mock.%s' % message_key)

def mock_one_message_without_content(mb):
    if not _register_mock(message_key='mock_test_message', response_key='mock_test_response'):
        return False

    return mb.post_and_check(post_key='mock_test_message', response_key='mock_test_response')
    
def mock_response_matches_correlation_id_if_not_specified(mb):
    if not _register_mock(message_key='mock_test_message', response_key='mock_test_response'):
        return False

    queue = mb.watch_for(keys=['mock_test_response'])
    mb.post(key='mock_test_message', correlation_id='test_id')
    message = mb.get_one_message(queue, 'test_id')
    return (message is not None) and ('mock_test_response' == message.key)

def mock_one_message_with_correlation_id(mb):
    if not _register_mock(message_key='mock_test_message_cid', response_key='mock_test_response_cid', correlation_id='mock_id'):
        return False

    return mb.post_and_check(post_key='mock_test_message_cid', response_key='mock_test_response_cid', correlation_id='mock_id')

def mock_two_messages_with_content(mb):
    if not    _register_mock(message_key='first_mock_test_message',  response_key='first_mock_test_response', 
                             response_content={'datum': '1+1=2'}) \
       or not _register_mock(message_key='second_mock_test_message', response_key='second_mock_test_response', 
                             response_content={'datum': '2+2=4'}):
        return False

    result = mb.post_and_check(post_key='first_mock_test_message', response_key='first_mock_test_response', 
                               response_content={'datum': '1+1=2'}) and \
             mb.post_and_check(post_key='second_mock_test_message', response_key='second_mock_test_response', 
                               response_content={'datum': '2+2=4'})
    return result

def stops_mocking_after_response(mb):
    if (not _register_mock(message_key='mock_test_message', response_key='mock_test_response')) or \
       (not mb.post_and_check(post_key='mock_test_message', response_key='mock_test_response')):
        return False

    return not mb.post_and_check(post_key='mock_test_message', response_key='mock_test_response')

def mocker_test(mb, message):
    result = mock_one_message_without_content(mb) and \
             mock_one_message_with_correlation_id(mb) and \
             mock_two_messages_with_content(mb) and \
             mock_response_matches_correlation_id_if_not_specified(mb) and \
             stops_mocking_after_response(mb)

    mb.post(key='mocker_test_result', content=result)

mb = messageboard.MessageBoard()
queue = mb.watch_for(keys=['component_ready.core'])
mb.post(key='process_ready.mocker_test')
mb.start_receive_loop(queue, callback=mocker_test)
