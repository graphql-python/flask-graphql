from json import JSONEncoder


class TestJSONEncoder(JSONEncoder):
    def encode(self, o):
        return 'TESTSTRING'
