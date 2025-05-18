import unittest
from unittest.mock import patch, MagicMock
import sys
import types

# stub requests so imports succeed
requests_stub = sys.modules.setdefault('requests', types.ModuleType('requests'))
requests_stub.post = getattr(requests_stub, 'post', lambda *a, **k: None)
requests_stub.get = getattr(requests_stub, 'get', lambda *a, **k: None)
requests_stub.put = getattr(requests_stub, 'put', lambda *a, **k: None)

from basecampapi import Basecamp, Campfire

class TestCampfire(unittest.TestCase):
    @patch('requests.post')
    @patch('requests.get')
    def test_campfire_methods(self, mock_get, mock_post):
        access_resp = MagicMock()
        access_resp.ok = True
        access_resp.json.return_value = {'access_token': 'tok'}

        init_resp = MagicMock()
        init_resp.ok = True
        init_resp.json.return_value = {'campfire': 'info'}

        lines_resp = MagicMock()
        lines_resp.ok = True
        lines_resp.json.return_value = ['line']

        mock_get.side_effect = [init_resp, lines_resp]

        write_resp = MagicMock()
        write_resp.ok = True
        mock_post.side_effect = [access_resp, write_resp]

        creds = {
            'account_id': '3',
            'client_id': 'cid',
            'client_secret': 'secret',
            'redirect_uri': 'uri',
            'refresh_token': 'ref',
        }

        Basecamp(credentials=creds)
        camp = Campfire(project_id=1, campfire_id=2)
        self.assertEqual(camp.info, {'campfire': 'info'})
        self.assertEqual(camp.get_lines(), ['line'])
        camp.write('hi')
        mock_post.assert_called_with(
            'https://3.basecampapi.com/3/buckets/1/chats/2/lines.json',
            headers={'Authorization': 'Bearer tok', 'Content-Type': 'application/json'},
            json={'content': 'hi'}
        )

    @patch('requests.post')
    @patch('requests.get')
    def test_init_failure(self, mock_get, mock_post):
        access_resp = MagicMock()
        access_resp.ok = True
        access_resp.json.return_value = {'access_token': 'tok'}
        fail_resp = MagicMock()
        fail_resp.ok = False
        fail_resp.status_code = 500
        fail_resp.reason = 'err'
        fail_resp.text = 'fail'

        mock_get.return_value = fail_resp
        mock_post.return_value = access_resp

        creds = {
            'account_id': '3',
            'client_id': 'cid',
            'client_secret': 'secret',
            'redirect_uri': 'uri',
            'refresh_token': 'ref',
        }

        Basecamp(credentials=creds)
        with self.assertRaises(Exception):
            Campfire(project_id=1, campfire_id=2)

    @patch('requests.post')
    @patch('requests.get')
    def test_error_paths(self, mock_get, mock_post):
        access_resp = MagicMock()
        access_resp.ok = True
        access_resp.json.return_value = {'access_token': 'tok'}

        init_resp = MagicMock()
        init_resp.ok = True
        init_resp.json.return_value = {'campfire': 'info'}

        mock_get.side_effect = [init_resp]
        mock_post.return_value = access_resp

        creds = {
            'account_id': '3',
            'client_id': 'cid',
            'client_secret': 'secret',
            'redirect_uri': 'uri',
            'refresh_token': 'ref',
        }

        Basecamp(credentials=creds)
        camp = Campfire(project_id=1, campfire_id=2)

        fail_resp = MagicMock()
        fail_resp.ok = False
        fail_resp.status_code = 500
        fail_resp.reason = 'err'
        fail_resp.text = 'fail'

        with patch('requests.get', return_value=fail_resp):
            with self.assertRaises(Exception):
                camp.get_lines()

        with patch('requests.post', return_value=fail_resp):
            with self.assertRaises(Exception):
                camp.write('bad')

if __name__ == '__main__':
    unittest.main()
