import unittest
from unittest.mock import patch, MagicMock
import sys
import types

# Provide minimal stubs for external dependencies so the library can be imported
requests_stub = sys.modules.setdefault('requests', types.ModuleType('requests'))
requests_stub.post = getattr(requests_stub, 'post', lambda *a, **k: None)
requests_stub.get = getattr(requests_stub, 'get', lambda *a, **k: None)
requests_stub.put = getattr(requests_stub, 'put', lambda *a, **k: None)

from basecampapi import Basecamp

class TestBasecamp(unittest.TestCase):
    @patch('requests.post')
    def test_init_with_refresh_token(self, mock_post):
        # mock access token response
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {'access_token': 'token123'}
        mock_post.return_value = mock_response

        creds = {
            'account_id': '99',
            'client_id': 'cid',
            'client_secret': 'secret',
            'redirect_uri': 'uri',
            'refresh_token': 'ref',
        }

        Basecamp(credentials=creds)

        self.assertEqual(Basecamp._Basecamp__base_url, 'https://3.basecampapi.com/99')
        self.assertEqual(Basecamp._Basecamp__credentials['access_token'], 'token123')
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_init_missing_refresh_token_raises(self, mock_post):
        creds = {
            'account_id': '1',
            'client_id': 'cid',
            'client_secret': 'secret',
            'redirect_uri': 'uri',
        }

        with self.assertRaises(Exception) as ctx:
            Basecamp(credentials=creds)
        self.assertIn('Access denied', str(ctx.exception))
        self.assertTrue(mock_post.called is False)

    @patch('requests.post')
    def test_init_with_verification_code(self, mock_post):
        # First call exchanges code for refresh token, second for access token
        resp_code = MagicMock()
        resp_code.ok = True
        resp_code.json.return_value = {'refresh_token': 'newref'}

        resp_access = MagicMock()
        resp_access.ok = True
        resp_access.json.return_value = {'access_token': 'acc'}

        mock_post.side_effect = [resp_code, resp_access]

        creds = {
            'account_id': '4',
            'client_id': 'cid',
            'client_secret': 'secret',
            'redirect_uri': 'uri',
        }

        Basecamp(credentials=creds, verification_code='code123')

        self.assertEqual(Basecamp._Basecamp__credentials['refresh_token'], 'newref')
        self.assertEqual(Basecamp._Basecamp__credentials['access_token'], 'acc')
        self.assertEqual(mock_post.call_count, 2)

    @patch('requests.post')
    def test_get_access_failure_raises(self, mock_post):
        # simulate __get_access failing
        resp = MagicMock()
        resp.ok = False
        resp.status_code = 401
        resp.reason = 'fail'
        resp.text = 'oops'
        mock_post.return_value = resp

        creds = {
            'account_id': '5',
            'client_id': 'cid',
            'client_secret': 'secret',
            'redirect_uri': 'uri',
            'refresh_token': 'badref',
        }

        with self.assertRaises(Exception):
            Basecamp(credentials=creds)

    @patch('requests.post')
    def test_verification_failure_raises(self, mock_post):
        fail_resp = MagicMock()
        fail_resp.ok = False
        fail_resp.status_code = 400
        fail_resp.reason = 'bad'
        fail_resp.text = 'err'
        mock_post.return_value = fail_resp

        creds = {
            'account_id': '6',
            'client_id': 'cid',
            'client_secret': 'secret',
            'redirect_uri': 'uri',
        }

        with self.assertRaises(Exception):
            Basecamp(credentials=creds, verification_code='x')

if __name__ == '__main__':
    unittest.main()
