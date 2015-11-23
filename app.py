import os

import stripe
from flask import Flask, render_template, request

from salesforce import add_opportunity
from salesforce import add_recurring_donation
from salesforce import upsert
#from config import stripe_keys
from config import FLASK_SECRET_KEY
from forms import DonateForm
from validate_email import validate_email

from pprint import pprint

from sassutils.wsgi import SassMiddleware

app = Flask(__name__)

app.secret_key = FLASK_SECRET_KEY

app.wsgi_app = SassMiddleware(app.wsgi_app, {
        'app': ('static/sass', 'static/css', 'static/css')
        })

app.config.from_pyfile('config.py')
stripe.api_key = app.config['STRIPE_KEYS']['secret_key']


@app.route('/memberform')
def member_form():
    form = DonateForm()
    if request.args.get('amount'):
        amount = request.args.get('amount')
    else:
        amount=False
    installment_period = request.args.get('installmentPeriod')
    installments = 'None'
    openended_status = 'Open'
    return render_template('member-form.html', form=form, amount=amount, \
        installment_period=installment_period, installments=installments, \
        openended_status=openended_status, key=app.config['STRIPE_KEYS']['publishable_key'])


@app.route('/donateform')
def donate_renew_form():
    form = DonateForm()
    if request.args.get('amount'):
        amount = request.args.get('amount')
    else:
        amount=False
    openended_status = 'None'
    installments = 'None'
    installment_period = 'None'
    return render_template('donate-form.html', form=form, amount=amount, \
        installment_period=installment_period, installments=installments, \
        openended_status=openended_status, key=app.config['STRIPE_KEYS']['publishable_key'])


@app.route('/circleform')
def circle_form():
    form = DonateForm()
    amount = request.args.get('amount')
    openended_status = 'None'
    installments = request.args.get('installments')
    installment_period = request.args.get('installmentPeriod')
    return render_template('circle-form.html', form=form, amount=amount, \
        installment_period=installment_period, installments=installments, \
        openended_status=openended_status, key=app.config['STRIPE_KEYS']['publishable_key'])


@app.route('/error')
def error():
    message = "Something went wrong!"
    return render_template('error.html', message=message)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


@app.route('/charge', methods=['POST'])
def charge():

    form = DonateForm(request.form)
    pprint('Request: {}'.format(request))

    email_is_valid = validate_email(request.form['stripeEmail'])

    if email_is_valid:
        customer = stripe.Customer.create(
        email=request.form['stripeEmail'],
        card=request.form['stripeToken']
    )
    else:
        message = "Please enter a valid email address."
        return render_template('error.html', message=message)


    upsert(request=request, customer=customer)

    #charge = stripe.Charge.create(
    #   customer=customer.id,
    #   amount=int(request.form['Opportunity.Amount']) * 100,
    #   currency='usd',
    #   description='Change Me' # TODO
    #)
    # except stripe.error.CardError, e:
    # The card has been declined
    #print ('Charge: {}'.format(charge))
    if form.validate():
        if (request.form['installment_period'] == 'None'):
            print("----One time payment...")
            add_opportunity(request=request, customer=customer)
            return render_template('charge.html', amount=request.form['amount'])
        else:
            print("----Recurring payment...")
            add_recurring_donation(request=request, customer=customer)
            return render_template('charge.html', amount=request.form['amount'])
    else:
        message = "Sorry, there was an issue saving your form."
        return render_template('error.html', message=message)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
