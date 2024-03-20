import requests
import unittest
import json

notes_url = 'http://localhost:8080'
categories_url = 'http://localhost:8081'
add_note_url = f'{notes_url}/notes'
get_note_by_id_url = f'{notes_url}/notes'
get_notes_url = f'{notes_url}/notes'


class TestIntegration(unittest.TestCase):

    def add_note(self):
        note = {
            "id": 88,
            "title": "To-Do list",
            "content": "Write code",
        }
        res = requests.post(add_note_url, json=note)
        self.assertEqual(res, "Success")

    def test_note_get(self):
        res = requests.get(f"{get_note_by_id_url}/1").json()
        self.assertEqual(res['title'], "Test")
        self.assertEqual(res['content'], "test")

    def fetch_notes(self):
        res = requests.get(get_notes_url)
        self.assertTrue(res != "Cant access database!")


if __name__ == '__main__':
    unittest.main()
