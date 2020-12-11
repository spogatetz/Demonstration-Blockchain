import hashlib

class Block:
    def __init__(self):
        self.data = 1
        self.previous_hash = ""
        self.nonce = 0
        self.sender = ""
        self.recipient = ""
        self.index = 0
        self.difficulty = 0

    def __init__(self, data, prev_hash, nonce, sender, recip, index, diff):
        self.data = data
        self.previous_hash = prev_hash
        self.nonce = nonce
        self.sender = sender
        self.recipient = recip
        self.index = index
        self.difficulty = diff

    def set_difficulty(self, diff):
        self.difficulty = diff

    def get_difficulty(self):
        return self.difficulty

    def set_data(self, new_data):
        self.data = new_data

    def get_data(self):
        return self.data

    def set_previous_hash(self, new_hash):
        self.previous_hash = new_hash

    def get_previous_hash(self):
        return self.previous_hash

    def set_nonce(self, new_nonce):
        self.nonce = new_nonce

    def get_nonce(self):
        return self.nonce

    def set_sender(self, new_sender):
        self.sender = new_sender

    def get_sender(self):
        return self.sender

    def set_recipient(self, new_recip):
        self.recipient = new_recip

    def get_recipient(self):
        return self.recipient

    def set_index(self, idx):
        self.index = idx

    def get_index(self):
        return self.index

    def hash(self):
        hash_string = str.encode(str(self.data) + str(self.previous_hash) + str(self.nonce) + self.sender + self.recipient)
        h = hashlib.sha256(hash_string).hexdigest()
        return h

    def find_nonce(self):
        my_hash = ""
        while True:
            my_hash = self.hash()
            if my_hash[:self.get_difficulty()] == "0" * self.get_difficulty():
                break
            self.set_nonce(int(self.get_nonce()) + 1)
        return my_hash

    def get_dict_representation(self):
        my_dict = {
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "sender": self.sender,
            "recipient": self.recipient,
            "difficulty": self.difficulty,
            "index": str(self.index)
        }
        return my_dict
