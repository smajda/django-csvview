import tablib
from django.utils import timezone


DATE_FORMAT = '%m/%d/%Y'
DATETIME_FORMAT = "{0} %H:%M".format(DATE_FORMAT)

def format_local_datetime(dt, df=DATETIME_FORMAT):
    "Helper function to simplify converting a datetime to local tz and formatting"
    return dt.astimezone(timezone.get_current_timezone()).strftime(df)

def multi_getattr(obj, attr, default=None):
    """
    Get a named attribute from an object; multi_getattr(x, 'a.b.c.d') is
    equivalent to x.a.b.c.d. When a default argument is given, it is
    returned when any attribute in the chain doesn't exist; without
    it, an exception is raised when a missing attribute is encountered.

    Source: Noufal Ibrahim, MIT License
            http://code.activestate.com/recipes/577346-getattr-with-arbitrary-depth/

    Examples:

        obj  = [1,2,3]
        attr = "append.__doc__.capitalize.__doc__"
        multi_getattr(obj, attr) #Will return the docstring for the
                                 #capitalize method of the builtin string
                                 #object
    """
    attributes = attr.split('.')
    for i in attributes:
        try:
            obj = getattr(obj, i)
        except AttributeError:
            if default is not None:
                return default
            else:
                raise
    return obj


class MappedTablibDataset(object):
    """
    Build a tablib dataset from params.

    mapping: a dict/OrderedDict where:

        keys = CSV Header Values
        values = dot-separated attr string (i.e. "contact.address.zip")
                 or a callable that will have the object and label passed in.

    objects: a QuerySet or list of objects to iterate over for each row

    allow_newlines: if False, strip out any newline characters from
    each value before inserting into csv.
    """
    def __init__(self, *args, **kwargs):
        self.mapping = kwargs.get('mapping', {})
        self.objects = kwargs.get('objects', [])
        self.allow_newlines = kwargs.get('allow_newlines', True)

    @staticmethod
    def bool_to_yes_no(val):
        "If val is boolean return 'Yes' for True, 'No' for False. Else just return as-is."
        bool_map = {True: 'Yes', False: 'No'}
        return bool_map.get(val) if isinstance(val, bool) else val

    def format_val(self, val):
        # format any datetimes
        # TODO a) customize format, b) what about naive datetimes?
        val = format_local_datetime(val) if hasattr(val, 'astimezone') else val

        # strip newlines
        if not self.allow_newlines and hasattr(val, 'splitlines'):
            val = ", ".join(val.splitlines())

        val = val or ''  # if None set val to ''

        val = self.bool_to_yes_no(val)  # True and False should be "Yes" or "No"

        return val

    @property
    def dataset(self):
        "Build the dataset off of self.objects and self.mapping"
        dataset = tablib.Dataset(headers=self.mapping.keys())
        for obj in self.objects:
            row_data = []
            for label, name in self.mapping.iteritems():
                if callable(name):
                    val = name(obj, label)
                else:
                    attr = multi_getattr(obj, name, '')
                    val = attr() if callable(attr) else attr
                val = self.format_val(val)
                row_data.append(val)
            dataset.append(row_data)
        return dataset

    @property
    def csv(self):
        return self.dataset.csv
