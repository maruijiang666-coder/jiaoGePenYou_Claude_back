from ninja import Schema


class ConfigPublicOut(Schema):
    contact_phone: str = ""
    service_time: str = ""
    app_version: str = ""
