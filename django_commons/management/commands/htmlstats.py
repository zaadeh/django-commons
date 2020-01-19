# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import collections
import json

try:
    from html.parser import HTMLParser
except ImportError:
    # Python 2
    from HTMLParser import HTMLParser

from django.core.management import BaseCommand, CommandError
from django.core.management.base import LabelCommand
from django.db import DEFAULT_DB_ALIAS
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType


class NotRunningInTTYException(Exception):
    pass


class HTMLMetrics(object):
    """
    Defines the various metrics that can be collected from an HTML document.
    """

    def __init__(self):
        self.tags = collections.defaultdict(int)
        self.ntags = 0
        self.attrs = collections.defaultdict(int)
        self.nattrs = 0
        self.tag_attrs = collections.defaultdict(lambda: collections.defaultdict(int))
        self.data_len = 0
        self.comments = 0
        self.doctypes = []
        self.processing_instructions = 0
        self.unrecognized_declarations = 0

    def report(self):
        stats = collections.OrderedDict()
        stats['tags'] = collections.OrderedDict(
            sorted(self.tags.items(), key=lambda item: item[0])
        )
        stats['ntags'] = self.ntags
        stats['attrs'] = collections.OrderedDict(
            sorted(self.attrs.items(), key=lambda item: item[0])
        )
        stats['nattrs'] = self.nattrs
        stats['tag_attrs'] = collections.OrderedDict(
            sorted(self.tag_attrs.items(), key=lambda item: item[0])
        )
        stats['data_len'] = self.data_len
        stats['comments'] = self.comments
        stats['doctypes'] = self.doctypes
        stats['processing_instructions'] = self.processing_instructions
        stats['unrecognized_declarations'] = self.unrecognized_declarations

        res = json.dumps(stats, indent=4)
        return res


class HTMLMetricsAggregator(HTMLMetrics):
    """
    Aggregate the results of many HTMLMetrics classes into one.

    This class can build upon HTMLMetrics class to add metric aggregation
    logic.
    """

    def ingest(self, metrics):
        """
        Ingest a given instance of HTMLMetrics.

        Add the given metrics parameter to the aggregated result.
        """
        assert isinstance(metrics, HTMLMetrics), "invalid parameter"

        for tag, count in metrics.tags.items():
            self.tags[tag] += count
        self.ntags += metrics.ntags
        for attr, count in metrics.attrs.items():
            self.attrs[attr] += count
        self.nattrs += metrics.nattrs
        for tag, attr in metrics.tag_attrs.items():
            for attr_key, attr_count in attr.items():
                self.tag_attrs[tag][attr_key] += attr_count
        self.data_len += metrics.data_len
        self.comments += metrics.comments
        self.doctypes.extend(metrics.doctypes)
        self.processing_instructions += metrics.processing_instructions
        self.unrecognized_declarations += metrics.unrecognized_declarations


class HTMLProcessor(HTMLParser, HTMLMetrics):
    """
    Collect statistics about the parsed HTML document.

    Python's builtin `html.parser` might not be the fastest HTML parser (look
    for `lxml` for speed), but it is fairly tolerant of faulty HTML markup.
    """

    def __init__(self, *args, **kwargs):
        #  super(HTMLProcessor, self).__init__(*args, **kwargs)
        HTMLParser.__init__(self, *args, **kwargs)
        HTMLMetrics.__init__(self)

    def handle_starttag(self, tag, attrs):
        self.tags[tag] += 1
        self.ntags += 1
        for attr in attrs:
            self.attrs[attr[0]] += 1
            self.nattrs += 1
            # TODO: add a count of distinct attr[1] values as a child
            self.tag_attrs[tag][attr[0]] += 1

    def handle_data(self, data):
        self.data_len += len(data)

    def handle_comment(self, data):
        self.comments += 1

    def handle_decl(self, decl):
        self.doctypes.append(decl)

    def handle_pi(self, data):
        self.processing_instructions += 1

    def unknown_decl(self, dara):
        self.unrecognized_declarations += 1


class Command(LabelCommand):
    """
    Parse HTML content in a data model field and display a statistical report.

    The main purpose for this commands is to give insight into what HTML
    content has been posted by users into the web application. It can help
    the decisions regarding what set of HTML tags or attributes to allow on
    the application and whether there has been attempts to inject malicious
    content into it and where to look for them.
    """

    help = (
        "Parse the HTML content stored in a model field, showing a statistical report"
    )
    missing_args_message = "Enter at least one fully-qualified model field name."
    requires_migrations_checks = True

    start_time = None

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.metrics_aggregator = HTMLMetricsAggregator()

    def execute(self, *args, **options):
        self.start_time = timezone.localtime()
        self.options = options
        retval = super(Command, self).execute(*args, **options)
        if options['verbosity'] > 1:
            self.stdout.write(
                self.style.WARNING(
                    "started at {}, took {}".format(
                        self.start_time, timezone.localtime() - self.start_time
                    )
                )
            )
        return retval

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '--database',
            action='store',
            dest='database',
            default=DEFAULT_DB_ALIAS,
            help='Specifies the database to use. Default is "default".',
        )
        parser.add_argument(
            '--single',
            action='store_true',
            dest='single',
            default=False,
            help='Whether an HTML statistics report should be displayed for every single record',
        )
        parser.add_argument(
            '--no-aggregate',
            action='store_true',
            dest='no_aggregate',
            default=False,
            help='Whether an aggregated HTML statistics should be displayed',
        )

    def parse_html(self, html):
        assert html is not None, "None HTML input"
        assert isinstance(html, (str, unicode, bytes)), "Invalid HTML input type"

        html_processor = HTMLProcessor()
        try:
            html_processor.feed(html)
            html_processor.close()
        except HTMLParser.HTMLParseError as e:
            raise CommandError("'{}': {}".format(type(e), e))

        return html_processor

    def process_row(self, row, column_name):
        try:
            column = getattr(row, column_name)
        except AttributeError:
            raise CommandError(
                "column '{}' on model does not exist".format(column_name)
            )

        if column is None:
            self.stdout.write(self.style.WARNING("column is null"))
            column = ''

        if not isinstance(column, (str, unicode, bytes)):
            raise CommandError(
                "column '{}' must have a textual type".format(column_name)
            )

        html_processor = self.parse_html(column)
        return html_processor

    def process_rows(self, model_class, column_name):
        try:
            rows = model_class.objects.all().order_by('pk')
            for row in rows:
                if self.options['verbosity'] > 0:
                    self.stdout.write("Processing row #{}".format(row.pk))
                html_processor = self.process_row(row, column_name)
                if self.options['verbosity'] > 1:
                    self.stdout.write(self.style.SUCCESS('Successfully processed'))

                if self.options['single']:
                    self.stdout.write("HTML stats:")
                    self.stdout.write(html_processor.report())

                self.metrics_aggregator.ingest(html_processor)

        except model_class.DoesNotExist:
            self.stdout.write(self.style.ERROR("No row found"))

        # TODO: add django-filter style queryset filtering and ordering
        #  except model_class.MultipleObjectsReturned as e:
        #  raise CommandError(e)

    def handle_label(self, label, *args, **options):
        self.stdout.write("Processing '{}'".format(label))

        try:
            app_name, model_name, column_name = label.split('.', 3)
        except ValueError:
            raise CommandError(
                "label argument must be in the form of 'app.model.column'"
            )

        self.stdout.write(
            "Parsing the HTML in model '{}.{}'".format(model_name, column_name)
        )

        try:
            ct = ContentType.objects.get(app_label=app_name, model=model_name)
            self.stdout.write("Fetching from model: '{}'".format(ct.name))
            model_class = ct.model_class()
        except (ContentType.DoesNotExist, ContentType.MultipleObjectsReturned):
            raise CommandError(
                "failed to fetch the model for '{}.{}'".format(app_name, model_name)
            )

        self.process_rows(model_class, column_name)

        if not options['no_aggregate']:
            self.stdout.write("Aggregate HTML stats:")
            self.stdout.write(self.metrics_aggregator.report())
