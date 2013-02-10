'''
This file is part of the Python EJTP library.

The Python EJTP library is free software: you can redistribute it 
and/or modify it under the terms of the GNU Lesser Public License as
published by the Free Software Foundation, either version 3 of the 
License, or (at your option) any later version.

the Python EJTP library is distributed in the hope that it will be 
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser Public License for more details.

You should have received a copy of the GNU Lesser Public License
along with the Python EJTP library.  If not, see 
<http://www.gnu.org/licenses/>.
'''

import ejtp.crypto
from ejtp.util.py2and3 import JSONBytesEncoder

class Identity(object):
    def __init__(self, name, encryptor, location, **kwargs):
        '''
        >>> ident = Identity("joe", ['rotate', 8], None)
        >>> ident.name
        'joe'
        >>> e =  ident.encryptor
        >>> e # doctest: +ELLIPSIS
        <ejtp.crypto.rotate.RotateEncryptor object at ...>
        >>> e == ident.encryptor # Make sure this is cached
        True
        >>> plaintext = "example"
        >>> sig = ident.sign(plaintext)
        >>> sig
        RawData(48d050d89056c477583982a704bda350773aba4f0280388da1e0c4a4c8ee4c54)
        >>> ident.verify_signature(sig, plaintext)
        True
        '''
        self._contents = {
            'name': name,
            'encryptor': encryptor,
            'location': location,
        }
        self._contents.update(kwargs)
        self._encryptor = None

    def __getitem__(self, i):
        return self._contents[i]

    def __setitem__(self, i, v):
        self._contents[i] = v

    def __delitem__(self, i):
        del self._contents[i]

    def sign(self, plaintext):
        return self.encryptor.sign(plaintext)

    def verify_signature(self, signature, plaintext):
        return self.encryptor.sig_verify(plaintext, signature)

    def public(self):
        '''
        Return a copy of this Identity with only the public component of
        its encryptor object.

        >>> from ejtp import testing
        >>> ident = testing.identity()
        >>> "PRIVATE" in str(ident.encryptor.proto()[1])
        True
        >>> "PUBLIC" in str(ident.encryptor.proto()[1])
        False
        >>> "PRIVATE" in str(ident.public().encryptor.proto()[1])
        False
        >>> "PUBLIC" in str(ident.public().encryptor.proto()[1])
        True
        '''
        public_proto = self.encryptor.public()
        return Identity(self.name, public_proto, self.location)

    def is_public(self):
        return self.encryptor.is_public()

    def can_encrypt(self):
        return self.encryptor.can_encrypt()

    def serialize(self):
        '''
        Serialize Identity object to dict.

        >>> from ejtp import testing
        >>> import json
        >>> json_data = json.dumps(
        ...     testing.identity().serialize(),
        ...     indent=4,
        ...     default=JSONBytesEncoder,
        ... )
        >>> data = json.loads(json_data)
        >>> data["encryptor"] #doctest: +ELLIPSIS
        [...'rsa', ...'...']
        >>> data["location"] #doctest: +ELLIPSIS
        [...'local', None, ...'mitzi']
        '''
        self['encryptor'] = self.encryptor.proto()
        return self._contents

    @property
    def name(self):
        return self['name']

    @name.setter
    def name(self, v):
        self['name'] = v

    @property
    def location(self):
        return self['location']

    @location.setter
    def location(self, v):
        self['location'] = v

    @property
    def encryptor(self):
        if not self._encryptor:
            self._encryptor = ejtp.crypto.make(self['encryptor'])
        return self._encryptor

    @encryptor.setter
    def encryptor(self, new_encryptor):
        self._encryptor = ejtp.crypto.make(new_encryptor)
        self['encryptor'] = self.encryptor.proto()

def deserialize(ident_dict):
    '''
    Deserialize a dict into an Identity.

    >>> id_dict = {}
    >>> ident = deserialize(id_dict)
    Traceback (most recent call last):
    ValueError: Missing ident property: 'name'
    >>> id_dict['name'] = "Calvin"
    >>> ident = deserialize(id_dict)
    Traceback (most recent call last):
    ValueError: Missing ident property: 'location'
    >>> id_dict['location'] = ["local", None, "calvin-freckle-mcmurray"]
    >>> ident = deserialize(id_dict)
    Traceback (most recent call last):
    ValueError: Missing ident property: 'encryptor'
    >>> id_dict['encryptor'] = ['rotate', 4]
    >>> id_dict['comment'] = "Lives dangerously under Rocky's \\"guidance.\\""
    >>> ident = deserialize(id_dict)
    >>> ident.name
    'Calvin'
    >>> ident.location
    ['local', None, 'calvin-freckle-mcmurray']
    >>> ident.encryptor #doctest: +ELLIPSIS
    <ejtp.crypto.rotate.RotateEncryptor object at ...>
    >>> ident['comment']
    'Lives dangerously under Rocky\\'s "guidance."'
    '''
    for req in ('name', 'location', 'encryptor'):
        if not req in ident_dict:
            raise ValueError("Missing ident property: %r" % req)

    name      = ident_dict['name']
    location  = ident_dict['location']
    encryptor = ident_dict['encryptor']

    cleaned = {}
    cleaned.update(ident_dict)
    del cleaned['name'], cleaned['location'], cleaned['encryptor']

    return Identity(name, encryptor, location, **cleaned)
