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

class TgGroup(MongoModel):
    chat_id = fields.IntegerField(primary_key=True)
    owner_id = fields.ReferenceField(TgUser)
    keywords = fields.ListField(fields.CharField(), blank=True)
    bad_keywords = fields.ListField(fields.CharField(), blank=True)
    ubs_names = fields.ListField(fields.CharField(), blank=True)
    blacklist_user_ids = fields.ListField(fields.IntegerField(), blank=True)
    forwarded_msgs = fields.ListField(fields.DictField(), blank=True)
    
    class Meta:
        write_concern = WriteConcern(j=True)
        connection_alias = 'pymodm-conn'
        collection_name = 'Groups'
        
class UserbotSession(MongoModel):
    id = fields.IntegerField(primary_key=True)
    owner_id = fields.ReferenceField(TgUser)
    name = fields.CharField()
    login = fields.CharField()
    password = fields.CharField(blank=True)
    