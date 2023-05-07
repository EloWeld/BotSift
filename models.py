from pymodm import MongoModel, fields
from pymongo.write_concern import WriteConcern

from config import MONGODB_CONNECTION_URI

class TgUser(MongoModel):
    user_id = fields.IntegerField(primary_key=True)
    first_name = fields.CharField(blank=True)
    last_name = fields.CharField(blank=True)
    username = fields.CharField(blank=True)
    
    class Meta:
        write_concern = WriteConcern(j=True)
        connection_alias = 'pymodm-conn'
        collection_name = 'Users'
