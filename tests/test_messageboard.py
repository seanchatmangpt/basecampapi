import unittest
from unittest.mock import patch, MagicMock
import sys
import types

# Provide minimal stubs for external dependencies
requests_stub = types.ModuleType('requests')
requests_stub.post = lambda *args, **kwargs: None
requests_stub.get = lambda *args, **kwargs: None
sys.modules.setdefault('requests', requests_stub)

from basecampapi import Basecamp, MessageBoard

class TestMessageBoard(unittest.TestCase):
    @patch('requests.post')
    @patch('requests.get')
    def test_create_message(self, mock_get, mock_post):
        # first post for access token then create message
        access_resp = MagicMock()
        access_resp.ok = True
        access_resp.json.return_value = {'access_token': 'tok'}

        # GET request for initialization of MessageBoard
        get_resp = MagicMock()
        get_resp.ok = True
        get_resp.json.return_value = []
        mock_get.return_value = get_resp

        post_resp = MagicMock()
        post_resp.ok = True
        mock_post.side_effect = [access_resp, post_resp]

        creds = {
            'account_id': '3',
            'client_id': 'cid',
            'client_secret': 'secret',
            'redirect_uri': 'uri',
            'refresh_token': 'ref',
        }

        Basecamp(credentials=creds)
        board = MessageBoard(project_id=1, message_board_id=2)
        board.create_message('subj', 'body')

        mock_post.assert_called_with(
            'https://3.basecampapi.com/3/buckets/1/message_boards/2/messages.json',
            headers={'Authorization': 'Bearer tok', 'Content-Type': 'application/json'},
            data='{"subject": "subj", "content": "body", "status": "active"}'
        )

if __name__ == '__main__':
    unittest.main()
