import unittest
from unittest.mock import patch, MagicMock
import sys
import types

# Provide minimal stubs for external dependencies
requests_stub = sys.modules.setdefault('requests', types.ModuleType('requests'))
requests_stub.post = getattr(requests_stub, 'post', lambda *a, **k: None)
requests_stub.get = getattr(requests_stub, 'get', lambda *a, **k: None)
requests_stub.put = getattr(requests_stub, 'put', lambda *a, **k: None)

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

    @patch('requests.get')
    @patch('requests.post')
    def test_get_message_and_update(self, mock_post, mock_get):
        access_resp = MagicMock()
        access_resp.ok = True
        access_resp.json.return_value = {'access_token': 'tok'}

        init_resp = MagicMock()
        init_resp.ok = True
        init_resp.json.return_value = []

        message_resp = MagicMock()
        message_resp.ok = True
        message_resp.json.return_value = {'id': 5}

        mock_get.side_effect = [init_resp, message_resp]

        put_resp = MagicMock()
        put_resp.ok = True

        with patch('requests.put', return_value=put_resp) as mock_put:
            mock_post.return_value = access_resp
            creds = {
                'account_id': '3',
                'client_id': 'cid',
                'client_secret': 'secret',
                'redirect_uri': 'uri',
                'refresh_token': 'ref',
            }

            Basecamp(credentials=creds)
            board = MessageBoard(project_id=1, message_board_id=2)
            data = board.get_all_messages()
            self.assertEqual(data, [])
            data = board.get_message(5)
            self.assertEqual(data, {'id': 5})
            board.update_message(5, 's', 'c')
            mock_put.assert_called_once()

    @patch('requests.get')
    @patch('requests.post')
    def test_comments_methods(self, mock_post, mock_get):
        access_resp = MagicMock()
        access_resp.ok = True
        access_resp.json.return_value = {'access_token': 'tok'}

        init_resp = MagicMock()
        init_resp.ok = True
        init_resp.json.return_value = []

        comments_resp = MagicMock()
        comments_resp.ok = True
        comments_resp.json.return_value = ['c']

        comment_resp = MagicMock()
        comment_resp.ok = True
        comment_resp.json.return_value = {'body': 'x'}

        mock_get.side_effect = [init_resp, comments_resp, comment_resp]

        post_resp = MagicMock()
        post_resp.ok = True

        with patch('requests.post', side_effect=[access_resp, post_resp]) as post_patch, \
             patch('requests.put', return_value=post_resp) as put_patch:
            creds = {
                'account_id': '3',
                'client_id': 'cid',
                'client_secret': 'secret',
                'redirect_uri': 'uri',
                'refresh_token': 'ref',
            }

            Basecamp(credentials=creds)
            board = MessageBoard(project_id=1, message_board_id=2)
            self.assertEqual(board.get_all_comments(4), ['c'])
            self.assertEqual(board.get_comment(1), {'body': 'x'})
            board.create_comment(4, 'hello')
            board.update_comment(1, 'u')
            self.assertTrue(post_patch.called)
            self.assertTrue(put_patch.called)

    @patch('requests.get')
    @patch('requests.post')
    def test_methods_error_paths(self, mock_post, mock_get):
        access_resp = MagicMock()
        access_resp.ok = True
        access_resp.json.return_value = {'access_token': 'tok'}

        init_resp = MagicMock()
        init_resp.ok = True
        init_resp.json.return_value = []

        mock_post.return_value = access_resp
        mock_get.return_value = init_resp

        creds = {
            'account_id': '3',
            'client_id': 'cid',
            'client_secret': 'secret',
            'redirect_uri': 'uri',
            'refresh_token': 'ref',
        }

        Basecamp(credentials=creds)
        board = MessageBoard(project_id=1, message_board_id=2)

        fail = MagicMock()
        fail.ok = False
        fail.status_code = 500
        fail.reason = 'err'
        fail.text = 'fail'

        with patch('requests.post', return_value=fail):
            with self.assertRaises(Exception):
                board.create_message('s', 'c')
            with self.assertRaises(Exception):
                board.create_comment(1, 'c')

        with patch('requests.put', return_value=fail):
            with self.assertRaises(Exception):
                board.update_message(1, 's', 'c')
            with self.assertRaises(Exception):
                board.update_comment(1, 'x')

        with patch('requests.get', return_value=fail):
            with self.assertRaises(Exception):
                board.get_message(1)
            with self.assertRaises(Exception):
                board.get_all_comments(1)
            with self.assertRaises(Exception):
                board.get_comment(1)

    @patch('requests.get')
    @patch('requests.post')
    def test_init_failure(self, mock_post, mock_get):
        access_resp = MagicMock()
        access_resp.ok = True
        access_resp.json.return_value = {'access_token': 'tok'}

        fail_resp = MagicMock()
        fail_resp.ok = False
        fail_resp.status_code = 500
        fail_resp.reason = 'err'
        fail_resp.text = 'fail'

        mock_post.return_value = access_resp
        mock_get.return_value = fail_resp

        creds = {
            'account_id': '3',
            'client_id': 'cid',
            'client_secret': 'secret',
            'redirect_uri': 'uri',
            'refresh_token': 'ref',
        }

        Basecamp(credentials=creds)
        with self.assertRaises(Exception):
            MessageBoard(project_id=1, message_board_id=2)

if __name__ == '__main__':
    unittest.main()
