import json, binascii, random
from ecdsa import SigningKey, VerifyingKey, NIST192p
from collections import OrderedDict

class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.nonce = random.randint(0,1000000)

        self.signature = ''
        self.jsonmsg = None
        
    def to_json(self):
        datadict = OrderedDict({
            "sender" : self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "nonce": self.nonce
        }) 

        toprintjson = json.dumps(datadict, sort_keys=True)
        return toprintjson
        
    @classmethod   
    def from_json(cls, jsondata):
        data = json.loads(jsondata)
        return cls(data['sender'], data['receiver'], data['amount'], data['nonce'])

        
    def sign(self, data, privatekey):
        signkey = SigningKey.from_string(privatekey, curve = NIST192p)
        signed = signkey.sign(data.encode('utf-8'))
        self.signature = signed
        return signed

    def validate_signature(self, jsonobj, signature, spubkey):
        loaded_data = json.loads(jsonobj)
        self.signature = None
        self.sender = loaded_data.get('sender')
        self.receiver = loaded_data.get('receiver')
        self.amount = loaded_data.get('amount')
        self.nonce = loaded_data.get('nonce')
        
        self.jsonmsg = self.to_json()

        verifykey = VerifyingKey.from_string(spubkey, curve = NIST192p)
        validity = verifykey.verify(signature,self.jsonmsg.encode('utf-8'))

        return validity 