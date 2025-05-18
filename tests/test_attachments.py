import unittest
from unittest.mock import patch, MagicMock
import sys
import types

# Provide minimal stubs so modules import without external packages
requests_stub = sys.modules.setdefault('requests', types.ModuleType('requests'))
requests_stub.post = getattr(requests_stub, 'post', lambda *a, **k: None)
requests_stub.get = getattr(requests_stub, 'get', lambda *a, **k: None)
requests_stub.put = getattr(requests_stub, 'put', lambda *a, **k: None)

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

    @patch('filetype.guess')
    @patch('requests.post')
    def test_upload_from_bytes_error(self, mock_post, mock_guess):
        access_resp = MagicMock()
        access_resp.ok = True
        access_resp.json.return_value = {'access_token': 'tok'}

        fail_resp = MagicMock()
        fail_resp.ok = False
        fail_resp.status_code = 500
        fail_resp.reason = 'err'
        fail_resp.text = 'fail'

        mock_post.side_effect = [access_resp, fail_resp]

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
        with self.assertRaises(Exception):
            att.upload_from_bytes(b'data', 'img.png')

    @patch('mimetypes.MimeTypes.guess_type')
    @patch('requests.post')
    def test_upload_file(self, mock_post, mock_guess):
        access_resp = MagicMock()
        access_resp.ok = True
        access_resp.json.return_value = {'access_token': 'tok'}

        upload_resp = MagicMock()
        upload_resp.ok = True
        upload_resp.json.return_value = {'attachable_sgid': 'sg'}

        mock_post.side_effect = [access_resp, upload_resp]

        mock_guess.return_value = ('text/plain', None)

        creds = {
            'account_id': '2',
            'client_id': 'cid',
            'client_secret': 'secret',
            'redirect_uri': 'uri',
            'refresh_token': 'ref',
        }

        Basecamp(credentials=creds)
        att = Attachments()

        import tempfile
        with tempfile.NamedTemporaryFile('wb', delete=False) as tmp:
            tmp.write(b'hi')
            tmp_path = tmp.name

        att.upload_file(tmp_path, 'f.txt')
        self.assertIn('f.txt', att.files)
        mock_post.assert_called_with(f"https://3.basecampapi.com/2/attachments.json?name={tmp_path}", headers={'Authorization': 'Bearer tok', 'Content-Type': 'text/plain', 'Content-Length': str(2)}, data=unittest.mock.ANY)

    @patch('mimetypes.MimeTypes.guess_type')
    @patch('requests.post')
    def test_upload_file_error(self, mock_post, mock_guess):
        access_resp = MagicMock()
        access_resp.ok = True
        access_resp.json.return_value = {'access_token': 'tok'}

        fail_resp = MagicMock()
        fail_resp.ok = False
        fail_resp.status_code = 500
        fail_resp.reason = 'err'
        fail_resp.text = 'fail'

        mock_post.side_effect = [access_resp, fail_resp]
        mock_guess.return_value = ('text/plain', None)

        creds = {
            'account_id': '2',
            'client_id': 'cid',
            'client_secret': 'secret',
            'redirect_uri': 'uri',
            'refresh_token': 'ref',
        }

        Basecamp(credentials=creds)
        att = Attachments()

        import tempfile
        with tempfile.NamedTemporaryFile('wb', delete=False) as tmp:
            tmp.write(b'hi')
            tmp_path = tmp.name

        with self.assertRaises(Exception):
            att.upload_file(tmp_path, 'f.txt')

if __name__ == '__main__':
    unittest.main()
