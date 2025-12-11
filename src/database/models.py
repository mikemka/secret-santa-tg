from tortoise.models import Model
from tortoise import fields


class User(Model):
    id = fields.IntField(pk=True)
    tg_id = fields.BigIntField(index=True, unique=True)
    tg_username = fields.CharField(max_length=255, null=True)
    tg_first_name = fields.CharField(max_length=255)
    tg_last_name = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    name = fields.CharField(max_length=255, null=True)
    surname = fields.CharField(max_length=255, null=True)
    additional_info = fields.CharField(max_length=255, null=True)

    confirmed = fields.BooleanField(default=False)

    secret_user_id = fields.IntField(null=True)
    
    status = fields.CharField(max_length=63, null=True)

    def __str__(self):
        return f'{self.tg_first_name} {self.tg_last_name if self.tg_last_name else ''}'.strip()


class Message(Model):
    from_user = fields.ForeignKeyField('models.User', null=True, on_delete=fields.SET_NULL, related_name='message_from_user')
    to_user = fields.ForeignKeyField('models.User', null=True, on_delete=fields.SET_NULL, related_name='message_to_user')
    text = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.from_user} -> {self.to_user}: {self.text}'
