import unittest
from unittest.mock import patch, MagicMock
import sys
import types

# Provide minimal stubs so modules import without external packages
requests_stub = types.ModuleType('requests')
requests_stub.post = lambda *args, **kwargs: None
requests_stub.get = lambda *args, **kwargs: None
sys.modules.setdefault('requests', requests_stub)

filetype_stub = types.ModuleType('filetype')
filetype_stub.guess = lambda *args, **kwargs: None
sys.modules.setdefault('filetype', filetype_stub)

from basecampapi import Basecamp, Attachments

class TestAttachments(unittest.TestCase):
    @patch('filetype.guess')
    @patch('requests.post')
    def test_upload_from_bytes(self, mock_post, mock_guess):
        # mock responses for Basecamp.__get_access and Attachments.upload_from_bytes
        access_resp = MagicMock()
        access_resp.ok = True
        access_resp.json.return_value = {'access_token': 'tok'}

        upload_resp = MagicMock()
        upload_resp.ok = True
        upload_resp.json.return_value = {'attachable_sgid': 'sgid123'}

        mock_post.side_effect = [access_resp, upload_resp]

        dummy_type = MagicMock()
        dummy_type.mime = 'image/png'
        mock_guess.return_value = dummy_type

        creds = {
            'account_id': '2',
            'client_id': 'cid',
            'client_secret': 'secret',
            'redirect_uri': 'uri',
            'refresh_token': 'ref',
        }

        Basecamp(credentials=creds)
        att = Attachments()
        att.upload_from_bytes(b'data', 'img.png')

        self.assertIn('img.png', att.files)
        info = att.files['img.png']
        self.assertEqual(info['filename'], 'img.png')
        self.assertEqual(info['sgid'], 'sgid123')
        mock_post.assert_called_with(f"https://3.basecampapi.com/2/attachments.json?name=img.png", headers={'Authorization': 'Bearer tok', 'Content-Type': 'image/png', 'Content-Length': '4'}, data=b'data')

if __name__ == '__main__':
    unittest.main()
