import unittest
from unittest.mock import patch, MagicMock
import sys
import types

# Provide minimal stubs for external dependencies so the library can be imported
requests_stub = types.ModuleType('requests')
requests_stub.post = lambda *args, **kwargs: None
requests_stub.get = lambda *args, **kwargs: None
sys.modules.setdefault('requests', requests_stub)

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

if __name__ == '__main__':
    unittest.main()
