from flask import Flask, jsonify, request, render_template
import zeep

app = Flask(__name__)

# SOAP clients
country_info_client = zeep.Client(wsdl='http://webservices.oorsprong.org/websamples.countryinfo/CountryInfoService.wso?WSDL')
convert_currency_client = zeep.Client(wsdl='https://fx.currencysystem.com/webservices/CurrencyServer5.asmx?wsdl')


def convert_currency(license_key, from_currency, to_currency, amount, rounding=True, format="", return_rate="curncsrvReturnRateNumber", time="", type=""):
    try:
        result = convert_currency_client.service.Convert(
            licenseKey=license_key,
            fromCurrency=from_currency,
            toCurrency=to_currency,
            amount=amount,
            rounding=rounding,
            format=format,
            returnRate=return_rate,
            time=time,
            type=type
        )
        return result
    except Exception as e:
        return f"Error in conversion: {str(e)}"


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/country_info', methods=['POST'])
def country_info():
    try:

        country_name = request.form.get('country_name')
        country_iso = request.form.get('country_iso')
        capital = request.form.get('capital')
        flag = request.form.get('flag')
        amount_currency = request.form.get('amount_currency')
        currency_iso_code = request.form.get('currency_iso_code')
        amount_in_usd = None

        if amount_currency and currency_iso_code:

            conversion_result = convert_currency(
                license_key="",
                from_currency=currency_iso_code, 
                to_currency='USD', 
                amount=float(amount_currency)
            )

            if isinstance(conversion_result, str):
                return render_template('home.html', error=conversion_result)

            amount_in_usd = conversion_result
            return render_template('home.html', 
                                   country_iso=country_iso, 
                                   capital=capital, 
                                   flag=flag, 
                                   country_name=country_name,
                                   currency_iso_code=currency_iso_code,
                                   amount_currency=amount_currency,
                                   amount_in_usd=amount_in_usd)

        else:
            country_iso_code = country_info_client.service.CountryISOCode(sCountryName=country_name)
            capital_city = country_info_client.service.CapitalCity(sCountryISOCode=country_iso_code)
            country_flag_url = country_info_client.service.CountryFlag(sCountryISOCode=country_iso_code)
            country_currency = country_info_client.service.CountryCurrency(sCountryISOCode=country_iso_code)
            currency_iso_code = country_currency.sISOCode

            return render_template('home.html', 
                                   country_iso=country_iso_code, 
                                   capital=capital_city, 
                                   flag=country_flag_url, 
                                   country_name=country_name,
                                   currency_iso_code=currency_iso_code)

    except Exception as e:
        return render_template('home.html', error=str(e))


if __name__ == '__main__':
    app.run(debug=True)
