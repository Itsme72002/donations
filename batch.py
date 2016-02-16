from datetime import datetime, timedelta
import json

import celery
from emails import send_email
from pytz import timezone
import requests
import stripe

from salesforce import SalesforceConnection
from config import STRIPE_KEYS
from config import ACCOUNTING_MAIL_RECIPIENT
from config import TIMEZONE

zone = timezone(TIMEZONE)

stripe.api_key = STRIPE_KEYS['secret_key']


class Log(object):
    """
    This encapulates sending to the console/stdout and email all in one.

    """
    def __init__(self):
        self.log = list()

    def it(self, string):
        """
        Add something to the log.
        """
        print(string)
        self.log.append(string)

    def send(self):
        """
        Send the assembled log out as an email.
        """
        body = '\n'.join(self.log)
        recipient = ACCOUNTING_MAIL_RECIPIENT
        subject = 'Batch run'
        send_email(body=body, recipient=recipient, subject=subject)


def amount_to_charge(entry):
    """
    Determine the amount to charge. This depends on whether the payer agreed
    to pay fees or not. If they did then we add that to the amount charged.
    Stripe charges 2.9% + $0.30.

    Stripe wants the amount to charge in cents. So we multiply by 100 and
    return that.
    """
    amount = int(entry['Amount'])
    if entry['Stripe_Agreed_to_pay_fees__c']:
        fees = amount * .029 + .30
    else:
        fees = 0
    total = amount + fees
    total_in_cents = total * 100

    return int(total_in_cents)


def process_charges(query, log):

    sf = SalesforceConnection()

    response = sf.query(query)
    # TODO: check response code

    log.it('Found {} opportunities available to process.'.format(
        len(response)))

    for item in response:
        amount = amount_to_charge(item)
        try:
            log.it('---- Charging ${} to {} ({})'.format(amount / 100,
                item['Stripe_Customer_ID__c'],
                item['Name']))
            charge = stripe.Charge.create(
                    customer=item['Stripe_Customer_ID__c'],
                    amount=amount,
                    currency='usd',
                    description=item['Description'],
                    )
        except stripe.error.CardError as e:
            # look for decline code:
            decline_code = ''
            try:
                decline_code = e.json_body['error']['decline_code']
            except:
                print('Unable to extract decline code')
            log.it("The card has been declined: {} ({})".format(e,
                decline_code))
            continue
        except stripe.error.InvalidRequestError as e:
            log.it('Problem: {}'.format(e))
            continue
        except Exception as e:
            log.it('Problem: {}'.format(e))
            continue
        if charge.status != 'succeeded':
            log.it('Charge failed. Check Stripe logs.')
            continue
        update = {
                'Stripe_Transaction_Id__c': charge.id,
                'Stripe_Card__c': charge.source.id,
                'StageName': 'Closed Won',
                }
        path = item['attributes']['url']
        url = '{}{}'.format(sf.instance_url, path)
        resp = requests.patch(url, headers=sf.headers, data=json.dumps(update))
        # TODO: check 'errors' and 'success' too
        if resp.status_code == 204:
            log.it('ok')
        else:
            log.it('problem')
            raise Exception('problem')


@celery.task()
def charge_cards():

    log = Log()

    log.it('---Starting batch job...')

    three_days_ago = (datetime.now(tz=zone) - timedelta(
        days=3)).strftime('%Y-%m-%d')
    today = datetime.now(tz=zone).strftime('%Y-%m-%d')

    # regular (non Circle) pledges:
    log.it('---Processing regular charges...')

    query = """
        SELECT Amount, Name, Stripe_Customer_Id__c, Description,
            Stripe_Agreed_to_pay_fees__c
        FROM Opportunity
        WHERE CloseDate <= {}
        AND CloseDate >= {}
        AND StageName = 'Pledged'
        AND Stripe_Customer_Id__c != ''
        AND Type != 'Giving Circle'
        """.format(today, three_days_ago)

    process_charges(query, log)

    #
    # Circle transactions are different from the others. The Close Dates for a
    # given Circle donation are all identical. That's so that the gift can be
    # recognized all at once on the donor wall. So we use another field to
    # determine when the card is actually charged: Expected_Giving_Date__c.
    # So we process charges separately for Circles.
    #

    log.it('---Processing Circle charges...')

    query = """
        SELECT Amount, Name, Stripe_Customer_Id__c, Description,
            Stripe_Agreed_to_pay_fees__c
        FROM Opportunity
        WHERE Expected_Giving_Date__c <= {}
        AND Expected_Giving_Date__c >= {}
        AND StageName = 'Pledged'
        AND Stripe_Customer_Id__c != ''
        AND Type = 'Giving Circle'
        """.format(today, three_days_ago)

    process_charges(query, log)
    log.send()


if __name__ == '__main__':
    charge_cards()
