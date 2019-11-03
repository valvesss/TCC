import time

from pprint import pprint
from server import Server

alice = Server('localhost', 6000, 20)
alice.start()
time.sleep(3)
for i in range(4):
    data = {'company_user': 'Alice', 'company_name': 'Fatec!', 'company_data': '{0}'.format(i)}
    alice.bc.new_tx(data)
    time.sleep(3)
alice.join()
pprint(alice.shared_tx)
