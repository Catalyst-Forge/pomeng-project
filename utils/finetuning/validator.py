import random
from marshmallow import Schema, fields, validate, ValidationError

BASE_MODELS = [
    'gpt-4o-2024-08-06',
    'gpt-4o-mini-2024-07-18', 
    'gpt-4-0613',
    'gpt-3.5-turbo-0125',
    'gpt-3.5-turbo-1106',
    'gpt-3.5-turbo-0613'
]

class FineTuningJobSchema(Schema):
    suffix = fields.Str(required=True, validate=[
        validate.Length(min=1, max=40),
        validate.Regexp(r'^[a-zA-Z0-9_-]+$', error='Suffix can only contain alphanumeric characters, underscores, and hyphens')
    ])
    model = fields.Str(required=True, validate=validate.OneOf(BASE_MODELS))
    seed = fields.Int(required=False, validate=validate.Range(min=0, max=2**32-1))
    batch_size = fields.Int(required=False, allow_none=True, validate=validate.Range(min=1))
    lr_multiplier = fields.Float(required=False, allow_none=True, validate=validate.Range(min=0, max=1))
    epochs = fields.Int(required=False, allow_none=True, validate=validate.Range(min=1))

    def load(self, data, *args, **kwargs):
        if not data.get('seed'):
            data['seed'] = random.randint(0, 2**32-1)
        return super().load(data, *args, **kwargs)