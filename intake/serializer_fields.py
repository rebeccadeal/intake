import datetime
from pytz import timezone
from rest_framework import serializers
from intake import models
from formation.field_types import YES, NO

THIS_YEAR = datetime.datetime.now().year
PACIFIC = timezone('US/Pacific')


class DictField(serializers.Field):
    """A read only field for serializing submission answers
    """
    def to_representation(self, obj):
        keys = getattr(self, 'keys', None)
        if keys:
            return {
                key: value
                for key, value in obj.items()
                if key in keys
                }
        return obj


class CityField(serializers.Field):
    def to_representation(self, obj):
        address = obj.get('address')
        if address:
            city = address.get('city')
            state = address.get('state')
            return ', '.join([n for n in (city, state) if n])


class AgeField(serializers.Field):
    def to_representation(self, obj):
        dob = obj.get('dob')
        if dob:
            year = dob.get('year')
            if year:
                return THIS_YEAR - int(year)


class DictKeyField(serializers.Field):
    def __init__(self, key, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key = key

    def to_representation(self, dictionary):
        return dictionary.get(self.key)


class YesNoAnswerField(DictKeyField):

    def to_representation(self, dictionary):
        value = super().to_representation(dictionary)
        if value == YES:
            return True
        elif value == NO:
            return False
        return value


class SubmissionAnswersField(DictField):
    keys = [
            'contact_preferences',
            'monthly_income',
            'us_citizen',
            'being_charged',
            'serving_sentence',
            'on_probation_parole',
            'currently_employed',
        ]


class EventTypeField(serializers.Field):
    event_name = None
    reducer = len

    def __init__(self, *args, **kwargs):
        base_kwargs = {
            'source': 'events'
        }
        base_kwargs.update(kwargs)
        super().__init__(*args, **base_kwargs)

    def filter(self, events):
        return list(filter(lambda e: e.name == self.event_name, events))

    def reduce(self, events):
        return self.reducer(events)

    def to_representation(self, events):
        return self.reduce(self.filter(events.all()))


class HasEventField(EventTypeField):

    def to_representation(self, events):
        return bool(super().to_representation(events))


class EventTimeField(EventTypeField):
    event_name = None

    def reduce(self, events):
        times = [e.time for e in events]
        if times:
            return max(times).astimezone(PACIFIC).isoformat()


class EventDataKeyField(EventTypeField):
    key = None

    def reduce(self, events):
        data = [e.data for e in events]
        values = [
            datum.get(self.key)
            for datum in data
            if datum and self.key in datum]
        return next(iter(values), None)


class Started(EventTimeField):
    event_name = models.ApplicationEvent.APPLICATION_STARTED


class Finished(EventTimeField):
    event_name = models.ApplicationEvent.APPLICATION_SUBMITTED


class HadErrors(HasEventField):
    event_name = models.ApplicationEvent.APPLICATION_ERRORS


class IPAddress(EventDataKeyField):
    event_name = models.ApplicationEvent.APPLICATION_STARTED
    key = 'ip'


class Referrer(EventDataKeyField):
    event_name = models.ApplicationEvent.APPLICATION_STARTED
    key = 'referrer'


def has_completed_county_page(events):
    for event in events:
        if event.name == models.ApplicationEvent.APPLICATION_PAGE_COMPLETE:
            if event.data.get('page_name') == 'CountyApplication':
                return True
    return False


def made_a_meaningful_attempt_to_apply(applicant):
    """Some started applications are empty submissions, in which it appears
    that someone is exploring the interface, rather than starting a meaningful
    application. This checks whether an applicant has indeed made a meaningful
    attempt to fill a form. There are two situations that would return True:
        1. The user successfully submitted the CountyApplication page.
        2. In the absence of 1, the user got errors indicating at least one
           attempt beyond submitting an empty form.
    """
    events = list(applicant.events.all())
    if has_completed_county_page(events):
        return True
    meaningful_errors = []
    for event in events:
        if event.name == models.ApplicationEvent.APPLICATION_ERRORS:
            filter_keys = ['counties', 'first_name']
            errors = event.data.get('errors', {})
            free_of_errors_indicating_frivolity = all(
                [key not in errors for key in filter_keys])
            meaningful_errors.append(free_of_errors_indicating_frivolity)
    return any(meaningful_errors)


def is_multicounty(applicant):
    submissions = applicant.form_submissions.all()
    rap_outside_sf = any([
        sub.answers.get('rap_outside_sf') == YES
        for sub in submissions
        ])
    if rap_outside_sf:
        return True
    for sub in submissions:
        if len(sub.organizations.all()) > 1:
            return True
    return False
