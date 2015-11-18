from salesforce import *
import re
from salesforce import _format_opportunity
from salesforce import _format_recurring_donation
from unittest.mock import MagicMock
from unittest.mock import create_autospec
from unittest.mock import patch
from six import wraps
from pytz import timezone

import pytest
import responses
import stripe
from werkzeug.datastructures import ImmutableMultiDict, MultiDict
from werkzeug.local import LocalProxy

#("Request: ImmutableMultiDict([('Opportunity.Amount', '100'), ('frequency', "
# "'until-cancelled'), ('Contact.LastName', 'C'), ('Contact.street', '823 "
# "Congress Ave Ste 1400'), ('stripeEmail', "
# "'dcraigmile+test6@texastribune.org'), ('Contact.FirstName', 'D'), "
# "('Contact.HomePhone', '5551212'), ('stripeToken', "
# "'tok_16u66IG8bHZDNB6TCq8l3s4p'), ('stripeTokenType', 'card'), "
# "('Contact.postalCode', '78701')])")


#"Request: ImmutableMultiDict([('frequency', 'one-time'), "
# "('Contact.MailingCity', 'abc'), ('Contact.MailingPostalCode', '78701'), "
# "('Contact.HomePhone', '5551212'), ('Contact.MailingStreet', '123'), "
# "('Opportunity.Amount', '100'), ('stripeToken', "
# "'tok_16vxMhG8bHZDNB6T0QmPd3M4'), ('Reason', 'journalism'), "
# "('Contact.LastName', 'C'), ('stripeEmail', 'dcraigmile@texastribune.org'), "
# "('Description', ''), ('stripeTokenType', 'card'), ('Contact.FirstName', "
# "'D'), ('Contact.MailingState', 'TX')])")


zone = timezone('US/Central')


class CustomerObject(object):
    pass

customer = CustomerObject()
customer.id='cus_78MqJSBejMN9gn'


class RequestObject(object):
    pass

class Customer(object):
    pass

customer = Customer()
customer.id = 'cus_78MqJSBejMN9gn'

#customer = {
#        'account_balance': 0,
#        'created': 1444417221,
#        'currency': None,
#        'default_source': 'card_16u66IG8bHZDNB6T5KL3YJjT',
#        'delinquent': False,
#        'description': None,
#        'discount': None,
#        'email': 'dcraigmile+test6@texastribune.org',
#        'id': 'cus_78MqJSBejMN9gn',
#        'livemode': False,
#        'metadata': {},
#        'object': 'customer',
#        'shipping': None,
#        'sources': {
#            'data': [
#                {
#                    'address_city': None,
#                    'address_country': None,
#                    'address_line1': None,
#                    'address_line1_check': None,
#                    'address_line2': None,
#                    'address_state': None,
#                    'address_zip': None,
#                    'address_zip_check': None,
#                    'brand': 'Visa',
#                    'country': 'US',
#                    'customer': 'cus_78MqJSBejMN9gn',
#                    'cvc_check': 'pass',
#                    'dynamic_last4': None,
#                    'exp_month': 1,
#                    'exp_year': 2016,
#                    'fingerprint': 'emevC9TQ2yGPdnyL',
#                    'funding': 'credit',
#                    'id': 'card_16u66IG8bHZDNB6T5KL3YJjT',
#                    'last4': '4242',
#                    'metadata': {},
#                    'name': 'dcraigmile+test6@texastribune.org',
#                    'object': 'card',
#                    'tokenization_method': None
#                    }
#                ],
#            'has_more': False,
#            'object': 'list',
#            'total_count': 1,
#            'url': '/v1/customers/cus_78MqJSBejMN9gn/sources'
#            },
#        'subscriptions': {
#            'data': [],
#            'has_more': False,
#            'object': 'list',
#            'total_count': 0,
#            'url': '/v1/customers/cus_78MqJSBejMN9gn/subscriptions'
#            }
#        }


#proxy = RequestObject()
#proxy.form = request

contact = {
        'AccountId': '0011700000BpR8PAAV',
        'attributes': {
            'url': '/services/data/v34.0/sobjects/Contact/0031700000BHQzBAAX',
            'type': 'Contact'
            },
        'Stripe_Customer_Id__c': 'cus_78MnnsgVuQb4r6',
        'Id': '0031700000BHQzBAAX'
        }


class Response(object):
    pass


class Request(object):
    pass


request = Request()

form = MultiDict()
form.add('Opportunity.Amount', '100')
form.add('frequency', " "'until-cancelled'),
form.add('Contact.LastName', 'C'),
form.add('Contact.MailingStreet', '823 Congress Ave Ste 1400'),
form.add('stripeEmail', 'dcraigmile+test6@texastribune.org'),
form.add('Contact.FirstName', 'D'),
form.add('Contact.HomePhone', '5551212'),
form.add('stripeToken', 'tok_16u66IG8bHZDNB6TCq8l3s4p'),
form.add('stripeTokenType', 'card'),
form.add('Contact.MailingPostalCode', '78701')
form.add('Reason', 'Because I love the Trib!')
form.add('InstallmentPeriod', 'yearly')
form.add('Installments', '3')
form.add('OpenEndedStatus', 'None')
request.form = form


def test_check_response():
    response = Response()
    response.status_code = 204
    with pytest.raises(Exception):
        check_response(response)

    response.status_code = 500
    with pytest.raises(Exception):
        check_response(response)

    response.status_code = 404
    with pytest.raises(Exception):
        check_response(response)

    response.status_code = 200
    response = check_response(response)
    assert response is True


today = datetime.now(tz=zone).strftime('%Y-%m-%d')


def test__format_opportunity():

    response = _format_opportunity(contact=contact, request=request,
            customer=customer)
    expected_response = {
            'AccountId': '0011700000BpR8PAAV',
            'Amount': '100',
            'CloseDate': today,
            'Encouraged_to_contribute_by__c': 'Because I love the Trib!',
            'LeadSource': 'Stripe',
            'Name': 'DC (dcraigmile+test6@texastribune.org)',
            'RecordTypeId': '01216000001IhI9',
            'StageName': 'Pledged',
            'Stripe_Customer_Id__c': 'cus_78MqJSBejMN9gn'
            }

    assert response == expected_response


def test__format_recurring_donation():

    response = _format_recurring_donation(contact=contact, request=request,
            customer=customer)
    expected_response = {
            'Encouraged_to_contribute_by__c': 'Because I love the Trib!',
            'npe03__Date_Established__c': today,
            'Lead_Source__c': 'Stripe',
            'npe03__Contact__c': '0031700000BHQzBAAX',
            'npe03__Installment_Period__c': 'yearly',
            'npe03__Open_Ended_Status__c': 'Open',
            'Stripe_Customer_Id__c': 'cus_78MqJSBejMN9gn',
            'npe03__Amount__c': '300',   # 3 * 100
            'Name': 'foo',
            'npe03__Installments__c': '3',
            'npe03__Open_Ended_Status__c': 'None',
            'Type__c': 'Giving Circle'
            }
    response['Name'] = 'foo'
    assert response == expected_response


def test__format_contact():
    sf = SalesforceConnection()

    response = sf._format_contact(request_form=request.form)

    expected_response = {'Description': 'added by Stripe/Checkout app',
            'Email': 'dcraigmile+test6@texastribune.org',
            'FirstName': 'D',
            'HomePhone': '5551212',
            'LastName': 'C',
            'LeadSource': 'Stripe',
            'MailingCity': 'Austin',
            'MailingPostalCode': '78701',
            'MailingState': 'TX',
            'MailingStreet': '823 Congress Ave Ste 1400',
            'Stripe_Customer_Id__c': None}

    assert response == expected_response


def test_upsert_empty_customer():
    with pytest.raises(Exception):
        upsert(customer=None, request=None)


def test_upsert_empty_request():
    with pytest.raises(Exception):
        upsert(customer=foo, request=None)


def request_callback(request):
#    payload = json.loads(request.body)
    if 'All_In_One_EMail__c' in request.path_url:
        resp_body = '{"done": true, "records": []}'
    else:
        resp_body='{"done": true, "records": ["foo"]}'

    return (200, {}, resp_body)


@responses.activate
def test__get_contact():
    url_re = re.compile(r'http://foo/services/data/v34.0/query.*')

    responses.add(responses.GET, url_re,
            body='{"done": true, "records": ["foo"]}')
    responses.add(responses.POST,
            'https://cs22.salesforce.com/services/oauth2/token',
            body='{"instance_url": "http://foo", "errors": [], "id":'
            '"a0917000002rZngAAE", "access_token": "bar", "success": true}',
            status=201)

    sf = SalesforceConnection()
    response = sf._get_contact('schnitzel')
    expected_response = 'foo'
    assert response == expected_response


@responses.activate
def test_create_contact():
    url_re = re.compile(r'http://foo/services/data/v34.0/query.*')
    responses.add(responses.GET, url_re,
            body='{"done": true, "records": ["foo"]}')
    responses.add(responses.POST,
            'https://cs22.salesforce.com/services/oauth2/token',
            body='{"instance_url": "http://foo", "errors": [], "id":'
            '"a0917000002rZngAAE", "access_token": "bar", "success": true}',
            status=201)
    responses.add(responses.POST,
            'http://foo/services/data/v34.0/sobjects/Contact',
            body='{"errors": [], "id": "0031700000F3kcwAAB", "success": true}',
            status=201,)

    sf = SalesforceConnection()
    response = sf.create_contact(request_form=request.form)
    expected_response = 'foo'
    assert response == expected_response


@responses.activate
def test_find_contact():
    url_re = re.compile(r'http://foo/services/data/v34.0/query.*')
    responses.add(responses.GET, url_re,
            body='{"done": true, "records": ["foo"]}')
    responses.add(responses.POST,
            'https://cs22.salesforce.com/services/oauth2/token',
            body='{"instance_url": "http://foo", "errors": [], "id":'
            '"a0917000002rZngAAE", "access_token": "bar", "success": true}',
            status=201)

    sf = SalesforceConnection()
    response = sf.find_contact(email='bogus')
    expected_response = ['foo']
    assert response == expected_response


@responses.activate
def test_get_or_create_contact_non_extant():

    # first testing for the case where the user doesn't exist and needs to be
    # created

    responses.add(responses.POST,
            'https://cs22.salesforce.com/services/oauth2/token',
            body='{"instance_url": "http://foo", "errors": [], "id":'
            '"a0917000002rZngAAE", "access_token": "bar", "success": true}',
            status=201)
    responses.add(responses.POST,
            'http://foo/services/data/v34.0/sobjects/Contact',
            body='{"errors": [], "id": "0031700000F3kcwAAB", "success": true}',
            status=201,)
    url_re = re.compile(r'http://foo/services/data/v34.0/query.*')
    responses.add_callback(
            responses.GET, url_re,
            callback=request_callback,
            )

    sf = SalesforceConnection()
    response = sf.get_or_create_contact(request_form=request.form)
    # they were created:
    expected_response = (True, 'foo')
    assert response == expected_response


@responses.activate
def test_get_or_create_contact_extant():

    # next we test with the user already extant:
    url_re = re.compile(r'http://foo/services/data/v34.0/query.*')
    responses.add(responses.GET, url_re,
            body='{"done": true, "records": ["foo"]}')
    responses.add(responses.POST,
            'https://cs22.salesforce.com/services/oauth2/token',
            body='{"instance_url": "http://foo", "errors": [], "id":'
            '"a0917000002rZngAAE", "access_token": "bar", "success": true}',
            status=201)

    sf = SalesforceConnection()
    response = sf.get_or_create_contact(request_form=request.form)
    # no need to create:
    expected_response = (False, 'foo')
    assert response == expected_response


@responses.activate
def test_get_or_create_contact_multiple():
    # TODO: check that we send an alert

    # next we test with the user already extant:
    url_re = re.compile(r'http://foo/services/data/v34.0/query.*')
    responses.add(responses.GET, url_re,
            body='{"done": true, "records": ["foo", "bar"]}')
    responses.add(responses.POST,
            'https://cs22.salesforce.com/services/oauth2/token',
            body='{"instance_url": "http://foo", "errors": [], "id":'
            '"a0917000002rZngAAE", "access_token": "bar", "success": true}',
            status=201)

    sf = SalesforceConnection()
    response = sf.get_or_create_contact(request_form=request.form)
    # no need to create:
    expected_response = (False, 'foo')
    assert response == expected_response


@responses.activate
def test_upsert_non_extant():

    responses.add(
            responses.POST,
            'https://cs22.salesforce.com/services/oauth2/token',
            body='{"instance_url": "http://foo", "errors": [], "id": "a0917000002rZngAAE", "access_token": "bar", "success": true}',
            status=201,
            )
    responses.add(
            responses.POST,
            'http://foo/services/data/v34.0/sobjects/Contact',
            body='{"errors": [], "id": "0031700000F3kcwAAB", "success": true}',
            status=201,
            )
    responses.add_callback(
            responses.GET,
            'http://foo/services/data/v34.0/query',
            callback=request_callback,
            )

    actual = upsert(customer=customer, request=request)
    assert actual is True
    assert len(responses.calls) == 4


list_resp_body = {
        'done': True,
        'records': [
            {'AccountId': '0011700000BpR8PAAV',
                'Id': '0031700000BHQzBAAX',
                'Stripe_Customer_Id__c': 'cus_7GHFg5Dk07Loox',
                'attributes': {'type': 'Contact',
                    'url': '/services/data/v34.0/sobjects/Contact/0031700000BHQzBAAX'}},
            {'AccountId': '0011700000BqjZSAAZ',
                'Id': '0031700000BM3J4AAL',
                'Stripe_Customer_Id__c': None,
                'attributes': {'type': 'Contact',
                    'url': '/services/data/v34.0/sobjects/Contact/0031700000BM3J4AAL'}}
                ],
        'totalSize': 9
        }


def request_upsert_extant_callback(request):
    if 'All_In_One_EMail__c' in request.path_url:
        resp_body = json.dumps(list_resp_body)
    else:
        resp_body = '{"done": true, "records": ["foo"]}'

    return (200, {}, resp_body)


@responses.activate
def test_upsert_extant():

    responses.add(
            responses.PATCH,
            'http://foo/services/data/v34.0/sobjects/Contact/0031700000BHQzBAAX',
            body='{"errors": [], "id": "a0917000002rZngAAE", "success": true}',
            status=204,
            )
    responses.add(
            responses.POST,
            'https://cs22.salesforce.com/services/oauth2/token',
            body='{"instance_url": "http://foo", "errors": [], "id": "a0917000002rZngAAE", "access_token": "bar", "success": true}',
            status=201,
            )
    responses.add(
            responses.POST,
            'http://foo/services/data/v34.0/sobjects/Contact',
            body='{"errors": [], "id": "0031700000F3kcwAAB", "success": true}',
            status=201,
            )
    responses.add_callback(
            responses.GET,
            'http://foo/services/data/v34.0/query',
            callback=request_upsert_extant_callback,
            )

    actual = upsert(customer=customer, request=request)
    assert actual is True
    assert len(responses.calls) == 3