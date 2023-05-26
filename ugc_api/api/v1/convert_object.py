from datetime import datetime

from bson.objectid import ObjectId as BsonObjectId


class ObjectIdAsStr(BsonObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, (BsonObjectId, str)):
            # return str(v)
            raise TypeError('ObjectId required')
        return str(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string", example="")


class DatatimeAsStr(datetime):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, datetime):
            return v
        return datetime.isoformat(v)
