from .utils import TranslatableText


class TranslatableFieldDescriptor:
    def __init__(self, field):
        self.field = field
        self.name = field.name
        self.id = field.id

    def __get__(self, obj, type_):
        return obj.get_translation(self.name) if obj else vars(type_).get(self.name)

    def __set__(self, obj, value):
        attrs = vars(obj)
        if isinstance(value, TranslatableText):
            attrs[self.name] = value
        else:
            translation = attrs[self.name] = obj.get_translation(self.name)
            vars(translation)[translation.get_lang() if '_end_init' in attrs else '_origin'] = str(value)

    def __delete__(self, obj):
        vars(self).pop(self.name, None)
        obj._meta._field_tof['by_name'].pop(
            obj._meta._field_tof['by_id'].pop(self.id, self).name,
            None
        )
