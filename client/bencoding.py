from collections import OrderedDict
from functools import reduce

INT_TOKEN = b'i'
LIST_TOKEN = b'l'
DICT_TOKEN = b'd'
END_TOKEN = b'e'
STRING_SEPARATOR_TOKEN = b':'


class Decoder:
    def __init__(self, data: bytes):
        if not isinstance(data, bytes):
            raise TypeError('Argument "data" must be of type bytes')
        self._data = data
        self._index = 0

    def decode(self):
        c = self._first()
        if c == INT_TOKEN:
            self._skip()
            return self._decode_int()
        elif c == LIST_TOKEN:
            self._skip()
            return self._decode_list()
        elif c == DICT_TOKEN:
            self._skip()
            return self._decode_dict()
        elif c in b'0123456789':
            return self._decode_string()
        else:
            raise RuntimeError('Invalid token at {0}'.format(str(self._index)))

    def _first(self):
        if self._index + 1 >= len(self._data):
            return None
        return self._data[self._index]

    def _skip(self):
        self._index += 1

    def _read(self, length):
        if self._index + length > len(self._data):
            raise IndexError('The string length is too large')

        res = self._data[self._index:self._index + length]
        self._index += 1
        return res

    def _read_until(self, token):
        try:
            occurrence = self._data.index(token, self._index)
            res = self._data[self._index:occurrence]
            self._index = occurrence + 1
            return res
        except ValueError:
            raise RuntimeError('Unable to find token {0}'.format(str(token)))

    def _decode_int(self):
        return int(self._read_until(END_TOKEN))

    def _decode_list(self):
        res = []
        while self._data[self._index] != END_TOKEN:
            res.append(self.decode())
        self._skip()
        return res

    def _decode_dict(self):
        res = OrderedDict()
        while self._data[self._index] != END_TOKEN:
            key = self.decode()
            value = self.decode()
            res[key] = value
        self._skip()
        return res

    def _decode_string(self):
        length = self._read_until(STRING_SEPARATOR_TOKEN)
        data = self._read(length)
        return data


class Encoder:
    def __init__(self, data):
        self._data = data

    def encode(self) -> bytes:
        return self._encode_next(self._data)

    def _encode_next(self, _data):
        if type(_data) == str:
            return self._encode_str(_data)
        elif type(_data) == int:
            return self._encode_int(_data)
        elif type(_data) == list:
            return self._encode_list(_data)
        elif type(_data) == dict:
            return self._encode_dict(_data)
        elif type(_data) == bytes:
            return self._encode_bytes(_data)
        else:
            return None

    @staticmethod
    def _encode_str(_data):
        res = str(len(_data)) + ':' + _data
        return str.encode(res)

    @staticmethod
    def _encode_int(_data):
        return str.encode('i' + _data + 'e')

    def _encode_list(self, _data):
        return reduce(
            lambda acc, elem: acc + self._encode_next(elem),
            _data,
            initial=b'l') + b'e'

    def _encode_dict(self, _data):
        return reduce(
            lambda acc, pair: acc + self._encode_next(pair[0]) + self._encode_next(pair[1]),
            _data.items(),
            initial=b'd') + b'e'

    @staticmethod
    def _encode_bytes(_data):
        return str.encode(str(len(_data))) + b':' + _data
