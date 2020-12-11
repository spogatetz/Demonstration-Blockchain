from block import Block
from pymongo import MongoClient
from pymongo import errors
import json


class Blockchain:
    def __init__(self):
        self.current_difficulty = 2
        self.blocks = []
        self.__main__()

    def __main__(self):
        file = input("File w/o extension with db connection: ")
        while not self.__is_valid_filename__(file):
            if file == "":
                break
            file = input("Invalid characters, try again: ")
        self.__establish_db_connections__(file + ".txt")
        self.__import_blockchain__()
        # Enter prompt loop
        while True:
            self.__display_menu__()
            option = input("Enter an option: ")
            print("\n" * 100)
            if option == "1":
                self.__add_transaction__()
            if option == "2":
                self.__verify_blockchain__()
            if option == "3":
                self.__display_blockchain__()
            if option == "4":
                self.__corrupt_blockchain__()
            if option == "5":
                self.__fix_blockchain__()
            if option == "6":
                self.__export_blockchain__()
            if option == "7":
                self.__query__()
            if option == "8":
                self.__change_difficulty__()
            if option == "9":
                print("Terminating program...")
                break
            if option == "10":
                self.__print_hash_stats__()

    def __establish_db_connections__(self, file):
        try:
            with open(file, "r") as file:
                data = json.loads(file.read())
            self.client = MongoClient(data["dbconnect"])
            self.db = self.client.blockchain
        except FileNotFoundError:
            print("File not found, terminating...")
            exit(-1)
        except errors.ConnectionFailure:
            print("Unable to connect to database, terminating...")
            exit(-2)
        return True

    def __print_hash_stats__(self):
        self.__update_blocks__()
        total_hashes = 0
        for i in self.blocks:
            total_hashes += int(i.get_nonce())
        estimated_hashes = 0
        for i in [i.get_difficulty() for i in self.blocks]:
            estimated_hashes += 16**int(i)
        print("The expected number of hashes to create this blockchain was: " + str(estimated_hashes))
        print("The actual number of hashes it took to create this blockchain was: " + str(total_hashes))

    def __query__(self):
        phrases = ("all blocks by a sender", "all blocks by a recipient", "all transactions > an amount", "all transactions < an amount", "all transactions = an amount")
        types = ("sender", "recip", "greater", "less", "equal")
        for i in range(len(phrases)):
            parameter = input("Search for " + phrases[i] + ": ")
            if not parameter == "":
                type = types[i]
                break
        if type == "sender":
            cursor = self.db["Blocks"].find({"sender": parameter})
            self.__display_cursor__(cursor)
        elif type == "recip":
            cursor = self.db["Blocks"].find({"recipient": parameter})
            self.__display_cursor__(cursor)
        elif type == "greater":
            cursor = self.db["Blocks"].find({"data": {"$gt": int(parameter)}})
            self.__display_cursor__(cursor)
        elif type == "less":
            cursor = self.db["Blocks"].find({"data": {"$lt": int(parameter)}})
            self.__display_cursor__(cursor)
        elif type == "equal":
            cursor = self.db["Blocks"].find({"data": int(parameter)})
            self.__display_cursor__(cursor)

    def __export_blockchain__(self):
        self.__update_blocks__()
        while True:
            filename = input("Enter a filename without extension: ")
            if self.__is_valid_filename__(filename):
                break
            print("Invalid filename, try again")

        dictionary_rep = {
            "blocks": [i.get_dict_representation() for i in self.blocks]
        }
        json_data = json.dumps(dictionary_rep)
        with open(filename + ".txt", "w") as file:
            file.write(json_data)
        print("File: " + filename + ".txt Saved")

    def __update_mongo__(self):
        self.db["Blocks"].remove({})
        for b in self.blocks:
            post = b.get_dict_representation()
            json_post = json.dumps(post)
            self.db["Blocks"].insert_one(post)

    def __display_cursor__(self, cursor):
        cursor = list(cursor)
        if len(cursor) > 0:
            self.blocks.clear()
            for doc in cursor:
                block = Block(doc["data"], doc["previous_hash"], doc["nonce"], doc["sender"], doc["recipient"],
                              doc["index"], doc["difficulty"])
                self.blocks.append(block)
        for i in range(len(self.blocks)):
            x = json.dumps(self.blocks[i].get_dict_representation())
            print(x)
        self.__update_blocks__()

    def __update_blocks__(self):
        cursor = list(self.db.Blocks.find())
        if len(cursor) > 0:
            self.blocks.clear()
            for doc in cursor:
                block = Block(doc["data"], doc["previous_hash"], doc["nonce"], doc["sender"], doc["recipient"],
                              doc["index"], doc["difficulty"])
                self.blocks.append(block)
            return True
        else:
            return False

    def __import_blockchain__(self):
        if not self.__update_blocks__():
            print("No blockchain found, creating empty blockchain")
            genblock = Block(0, "", 0, "", "", 0, 2)
            self.__add_block__(genblock)
        else:
            print("Blockchain found, importing...")

    def __add_block__(self, block):
        if len(self.blocks) > 0:
            block.previous_hash = self.blocks[-1].hash()
        block.find_nonce()
        self.blocks.append(block)

        # add block to mongo
        post = block.get_dict_representation()
        json_post = json.dumps(post)
        self.db["Blocks"].insert_one(post)

    def __add_transaction__(self):
        self.__update_blocks__()
        print("Creating a new transaction")
        data = input("Enter data: ")
        sender = input("Enter sender: ")
        recip = input("Enter recipient: ")
        diff = self.current_difficulty
        index = 0
        if len(self.blocks) > 0:
            index = int(self.blocks[-1].get_index()) + 1
        try:
            new_block = Block(int(data), "", 0, sender, recip, index, diff)
        except ValueError:
            print("Error: Data field must be an integer value")
            exit(-3)
        self.__add_block__(new_block)
        print("Block has been added to the chain")

    def __change_difficulty__(self):
        new_diff = -1
        while int(new_diff) < 0 or int(new_diff) > 6:
            new_diff = input("Enter a difficulty [0-6]: ")
            if int(new_diff) < 0 or int(new_diff) > 6:
                print("Value not in range, try again")
        self.current_difficulty = int(new_diff)

    def __fix_blockchain__(self):
        self.__update_blocks__()
        prev_hash = ""
        for i in range(len(self.blocks)):
            self.blocks[i].set_previous_hash(prev_hash)
            prev_hash = self.blocks[i].find_nonce()
        self.__update_mongo__()

    def __corrupt_blockchain__(self):
        self.__update_blocks__()
        while True:
            index = int(input("Enter a block to edit [0-" + str(len(self.blocks) - 1) + "]: "))
            if 0 <= index <= len(self.blocks) - 1:
                break
            print("Invalid index, try again")

        data = input("Enter data (empty to leave the same): ")
        sender = input("Enter sender (empty to leave the same): ")
        recip = input("Enter recipient (empty to leave the same): ")
        if data != "":
            try:
                self.blocks[index].set_data(int(data))
            except ValueError:
                print("Error: Data must be an integer value")
                exit(-3)
        if sender != "":
            self.blocks[index].set_sender(sender)
        if recip != "":
            self.blocks[index].set_recipient(recip)
        self.__update_mongo__()
        print("Block updated")

    def __verify_blockchain__(self):
        self.__update_blocks__()
        valid = True
        current_hash = self.blocks[0].hash()
        for i in range(0, len(self.blocks)):
            if i > 0 and self.blocks[i].get_previous_hash() != current_hash:
                valid = False
                print("Invalid blockchain, data modified in block: " + str(i - 1) + " (0 indexed)")
                break
            current_hash = self.blocks[i].hash()
        # no more chainhash, cannot validate last block
        if valid:
            print("Valid blockchain")
        # if valid:
        #     if self.chainhash == current_hash:
        #         print("Valid Blockchain")
        #     else:
        #         print("Invalid blockchain, data modified in block: " + str(len(self.blocks) - 1) + " (0 indexed)")

    def __display_blockchain__(self):
        self.__update_blocks__()
        for i in range(len(self.blocks)):
            x = json.dumps(self.blocks[i].get_dict_representation())
            print(" -------------------------- Block " + str(i) + " --------------------------")
            print(x)

    @staticmethod
    def __is_valid_filename__(filename):
        disallowed_chars = ["<", ">", ":", "\"", "/", "\\", "|", "?", "*"]
        net = [i for i in disallowed_chars if i in filename]
        if len(net) == 0 and filename != "":
            return True
        return False

    @staticmethod
    def __display_menu__():
        print("Menu:\n1 - Add a transaction\n2 - Verify the blockchain\n3 - View the blockchain\n4 - Corrupt a "
              "block\n5 - Fix corruption by recomputing hashes\n6 - Export blockchain\n7 - Search the blockchain\n8 - Change the difficulty "
              "\n9 - Close program\n10 - Show hash statistics")


b = Blockchain()
