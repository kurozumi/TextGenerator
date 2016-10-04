from peewee import *

database = SqliteDatabase('chain.db', **{})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class ChainFreqs(BaseModel):
    freq = IntegerField()
    prefix1 = TextField()
    prefix2 = TextField()
    suffix = TextField()

    class Meta:
        db_table = 'chain_freqs'

class SqliteSequence(BaseModel):
    name = UnknownField(null=True)  # 
    seq = UnknownField(null=True)  # 

    class Meta:
        db_table = 'sqlite_sequence'

