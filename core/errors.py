class Error(Exception):
    pass

class DataError(Error):
    pass

class SerializeError(Error):
    pass

class ValidationError(Error):
    pass

class ConsensusError(Error):
    pass

class BlockRulesError(ConsensusError):
    pass
class TransactionRulesError(ConsensusError):
    pass
