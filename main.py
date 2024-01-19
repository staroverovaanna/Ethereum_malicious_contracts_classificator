import pickle
from evmdasm import EvmBytecode
from scipy.sparse import csr_matrix
import time
from web3 import Web3
from multiprocessing import Process, Manager, Queue, Lock

from utils import decompile, inference
from pipeline import get_new_trns, analyze_trns

import warnings
warnings.filterwarnings('ignore')

tr = 0.5
filename = 'finalized_model.sav'
model = pickle.load(open(filename, 'rb'))

NODE_ADDRESS = '' ## put here your node address

if __name__ == '__main__':


    new_deploys_trns_queue = Queue()
    # processed_hashes = set()
    new_deploys_tracker = Process(name='Mempool Scanner',
                              target=get_new_trns,
                              args=(new_deploys_trns_queue, ),
                              daemon=True)

    deploy_analyzer = Process(name='Mempool analyzer',
                              target=analyze_trns,
                              args=(new_deploys_trns_queue, ),
                              daemon=True)

    new_deploys_tracker.start()
    deploy_analyzer.start()
    new_deploys_tracker.join()
    deploy_analyzer.join()
