from web3 import Web3
from multiprocessing import Process, Manager, Queue, Lock
import time

def get_new_trns(q_out: Queue):
    """
    q_out: Queue with new deploys
    Функция для прослушивания последних блоков в блокчейне, если новая транзакция - деплой, то записываем в очередь
    """
    i = 1
    print(i)
    MAX_CONN_RET = 4 # параметр сколько раз максимально хотим переподключаться к потоку
    wss = '' ## put your node address here
    w3 = Web3(Web3.WebsocketProvider(wss))
    status = w3.is_connected()
    print(f'Node Connection - {status}')
    print(f'Connection attempt - {i}')
    processed_hashes = set()

    while i <= MAX_CONN_RET:
        try:
            start_time = time.time()
            trns_block = w3.eth.get_block('latest', full_transactions=True).transactions
            for trns in trns_block:
                if trns['to'] is None and trns['input'].hex()[:10] == '0x60806040':  # смотрим что транзакция это деплой
                    if trns['hash'] not in processed_hashes:
                        ## если хэш транзакции еще не в списке (не отправлен в очередь на обработку) - добавим его
                        q_out.put(trns)
                        processed_hashes.add(trns['hash'])
                        print('put smth')
            end_time = time.time()
            if not q_out.empty():
                print(f"{end_time - start_time} per 1 batch")

        except ConnectionError as ce:
            print(f"Connection error: {ce}")
            i += 1
            print(f'Connection attempt - {i}')
            time.sleep(5)
            pass

        except Exception as e:
            print(f"An error occurred: {e}")
            i += 1
            print(f'Connection attempt - {i}')
            time.sleep(5)
            pass

    else:
        print(f"Max connection attempts reached")


def analyze_trns(q_in: Queue):
    """
    q_in: Queue with new deploys to analyze
    Функция для анализа деплоев, принтит результат деплоя а именно
    1) Адресс контракта
    2) Хеш транзакции
    3) Результат классификации

    :param q_in:
    :return:
    """
    from utils import decompile, inference

    print("started analyze_trns process")
    processed_hashes = set()

    while True:

        if q_in.empty():
            continue

        trns = q_in.get()
        trns_address = trns.get('from', 'N/A')
        trns_hash = trns.get('hash', 'N/A')
        bytecode = trns.get('input', 'N/A')
        print(trns_address)

        # Проверка на дубли - если выделенный хэш уже раньше был (он записан в сет), то подсвечиваем это:
        if trns_hash in processed_hashes:
            print(f"Duplicate transaction detected - Hash: {trns_hash}")
            continue

        # Получаем аналитику, если есть данные
        if bytecode != 'N/A':
            opcode = decompile(bytecode)
            y_class = inference(opcode)
            print(f"Address - {trns_address}, Hash - {trns_hash}, Is_malicious? {y_class}")

            # Записываем хэш трназакции в сет для дальнейшей проверки на дубликаты
            processed_hashes.add(trns_hash)
