from django.http import HttpResponse
from django.utils import timezone

from .utils import MappedTablibDataset


def csv_response(csv, filename=None):
    """
    Pass in csv content and a filename (don't include the '.csv').
    Returns an HttpResponse with the correct mimetype and Content-Disposition.
    """
    if not filename:
        filename = "csv-{0}".format(timezone.now().strftime('%Y-%m-%d'))
    response = HttpResponse(csv, mimetype="text/csv")
    response['Content-Disposition'] = "attachment; filename={0}.csv".format(filename)
    return response


class CSVViewMixin(object):
    csv_mapping = {}  # subclasses must define
    allow_newlines = True  # Set to False to strip newlines from cell values

    def get_csv_filename(self):
        "Defaults to '[Model Name]-csv-[Date]'. Override to modify."
        filename = "csv-{0}".format(timezone.now().strftime('%Y-%m-%d'))
        if self.model:
            filename = "{0}-{1}".format(self.model.__name__, filename)
        return filename

    def render_to_response(self, context, **response_kwargs):
        "Build a tablib dataset and return csv_response"
        dataset = MappedTablibDataset(
            mapping=self.csv_mapping,
            objects=self.get_queryset(),  # TODO pagination?
            allow_newlines=self.allow_newlines,
            )
        filename = self.get_csv_filename()
        return csv_response(dataset.csv, filename=filename)
