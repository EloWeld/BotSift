from pymodm import MongoModel, fields

class TgUser(MongoModel):
    user_id: fields.IntegerField(primary_key=True)
    first_name: fields.CharField(blank=True)
    last_name: fields.CharField(blank=True)
    username: fields.CharField(blank=True)
    
