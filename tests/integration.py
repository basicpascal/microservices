import unittest
import requests
import psycopg2
from time import sleep
import json

notes_url = 'http://localhost:8080'
categories_url = 'http://localhost:8081'
add_note_url = f'{notes_url}/notes'
get_note_by_id_url = f'{notes_url}/notes'


class TestIntegration(unittest.TestCase):
    # CMD: python tests/integration.py
    def test_ticket_get(self):
        res = requests.get(f"{get_note_by_id_url}/1").json()
        self.assertTrue('title' in res.keys())
        self.assertTrue('content' in res.keys())


if __name__ == '__main__':
    unittest.main()
