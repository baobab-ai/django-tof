import inspect

from django.db import models

from .descriptors import TranslatableFieldDescriptor


class TranslatableFieldMixin:
    descriptor_class = TranslatableFieldDescriptor

    def __init__(self, content_type, title, id, *args, **kwargs):
        self.content_type = content_type
        self.title = title
        self.id = id
        super().__init__(*args, **kwargs)

    @classmethod
    def from_field(cls, content_type, title, id, field):
        """Creating a copy of a field with a descriptor class.
        :param content_type: Object of ContentType Model. Owner of the Field.
        :param title: Name of field.
        :param id: Identification of TranslatableField object.
        :param field: Object of models.Field. Original field for copying.
        :return: TranslatableCharField or TranslatableTextField - copy of field with TranslatableFieldMixin.
        """
        init_args = inspect.signature(models.Field.__init__).parameters
        data = vars(field)

        extra_data = {arg.name: data[arg.name] for arg in init_args.values() if data.get(arg.name)}

        if isinstance(field, models.CharField):
            extra_data['max_length'] = data['max_length']

        return cls(content_type, title, id, **extra_data)

    def contribute_to_class(self, cls):
        setattr(cls, self.name, self.descriptor_class(self))
