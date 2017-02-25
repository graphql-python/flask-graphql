from json import JSONEncoder, JSONDecoder
from json.decoder import WHITESPACE


class TestJSONEncoder(JSONEncoder):
    def encode(self, o):
        return 'TESTSTRING'


class TestJSONDecoder(JSONDecoder):
    def decode(self, s, _w=WHITESPACE.match):
        return {'query': '{test}'}
