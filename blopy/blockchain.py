import json
import logging
import datetime

from pprint import pprint
from hashlib import sha256

class Block:
    block_required_items = {'index': int,
                             'nonce': int,
                             'previous_hash': str,
                             'timestamp': str,
                             'transactions': list}

    def create_new(self,index,previous_hash,timestamp,transactions):
        block_raw = {'index': index,
                     'nonce': 0,
                     'previous_hash': previous_hash,
                     'timestamp': timestamp,
                     'transactions': transactions}

        return block_raw

    def compute_hash(self, block):
        block_string = self.dict_to_json(block)
        return sha256(block_string.encode()).hexdigest()

    def json_to_dict(self, json_block):
        try:
            data = json.loads(json_block)
        except Exception as error:
            logging.info('Block: error converting json to dict!')
        return data

    def dict_to_json(self, block):
        try:
            data = json.dumps(block, sort_keys=True)
        except Exception as error:
            logging.info('Block: error converting dict to json!')
        return data

    def validate_keys(self, block):
        if 'hash' in block:
            del block['hash']
        if not all (k in block for k in self.block_required_items.keys()):
            logging.error('Server Blockchain: Block #{} keys are not valid!'.format(block['index']))
            return False
        return True

    def validate_values(self, block):
        if 'hash' in block:
            del block['hash']
        keys = [k for k in block.keys()]
        for i in range(len(block)):
            if type(block[keys[i]]) != self.block_required_items[keys[i]]:
                logging.error('Server Blockchain: Block #{} values are not valid!'.format(block['index']))
                return False
        return True

class Blockchain:
    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []
        self.pow_difficulty = 2
        self.block = Block()

    def create_genesis_block(self, content=None):
        genesis_block = self.block.create_new(0, "Yo I'm Rupert (aka Genesis Blok) {0}".format(content), str(datetime.datetime.now()), [])
        genesis_block['hash'] = self.block.compute_hash(genesis_block)
        self.chain.append(genesis_block)
        logging.info('Server Blockchain: genesis block created.')

    @property
    def last_block(self):
        return self.chain[-1]

    def validate_block(self, block, proof):
        if (not self.block.validate_keys(block) or
            not self.block.validate_values(block) or
            not self.validate_previous_hash(block) or
            not self.validate_proof(block, proof)):
                return False

        logging.info('Server Blockchain: Block #{} is valid!'.format(block['index']))
        if not 'hash' in block:
            block['hash'] = proof
        return block

    def validate_proof(self, block, proof):
        block_hash = self.block.compute_hash(block)
        if (not (block_hash.startswith('0' * self.pow_difficulty) or
                block_hash != proof)):
            logging.error('Server Blockchain: Block #{} has no valid proof!'.format(block['index']))
            return False
        return True

    def validate_previous_hash(self, block):
        last_block = self.last_block
        if block['previous_hash'] != last_block['hash']:
            logging.error('Server Blockchain: Block #{} previous_hash is not valid!'.format(block['index']))
            return False
        return True

    def proof_of_work(self, block):
        computed_hash = self.block.compute_hash(block)
        while not computed_hash.startswith('0' * self.pow_difficulty):
            block['nonce'] += 1
            computed_hash = self.block.compute_hash(block)
        return computed_hash

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    def mine(self):
        if not self.unconfirmed_transactions:
            logging.info('Server Blockchain: There are no transactions to mine!')
            return False

        block = self.forge_block()
        proof = self.proof_of_work(block)
        validated_block = self.validate_block(block, proof)
        if not validated_block:
            return False
        self.add_block(validated_block)
        self.unconfirmed_transactions = []
        logging.info('Server Blockchain: Block #{} was inserted in the chain.'.format(block['index']))

    def add_block(self, block):
        self.chain.append(block)

    def forge_block(self):
        last_block = self.last_block
        return self.block.create_new(last_block['index'] + 1,
                                    last_block['hash'],
                                    str(datetime.datetime.now()),
                                    self.unconfirmed_transactions)

    def new_transaction(self, data):
        required_fields = ["company_name", "company_data"]

        for field in required_fields:
            if not data.get(field):
                logging.error('Server Blockchain: The transaction data is invalid.')
                return False

        data["timestamp"] = str(datetime.datetime.now())

        self.add_new_transaction(data)
        logging.info('Server Blockchain: a new transaction was validated')
