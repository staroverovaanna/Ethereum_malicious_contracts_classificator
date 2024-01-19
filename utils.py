from evmdasm import EvmBytecode
from scipy.sparse import csr_matrix
import pickle
filename = 'finalized_model.sav'
model = pickle.load(open(filename, 'rb'))


def decompile(_bytecode: str):
    """
    Декомпилирует байткод в опкод
    :param _bytecode: байткод контракта из нового блока
    :return: опкоды в виде str
    """
    print('Decompling to opcodes')
    disassembler = EvmBytecode(_bytecode)
    opcode = disassembler.disassemble().as_string
    print('Normalizing opcode')
    opcode_normalized = opcode.replace(' \n', '\n').replace(' ', ' 0x')

    return opcode_normalized.lower()


def inference(_opcode: str):
    """
    Инференс вашей модели
    :param _opcode:
    :return: класс смарт-контракта
    """
    import pickle
    filename = 'finalized_model.sav'
    model = pickle.load(open(filename, 'rb'))
    tr = 0.5
    ## обращаемся к заимпорченной модели
    X_transformed = model.named_steps['tfidf'].transform([_opcode])
    model_prediction_get = model.named_steps['model']
    y_proba = model_prediction_get.predict_proba(X_transformed)[0, 1]

    return int(y_proba > tr)
