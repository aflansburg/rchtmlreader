import re
import urllib.request
import urllib.error
import csv
from cli_augments import ConsoleColors as cColors


def uri_cleaner(uri):
    # uri_regex = r"^(.*product)\/cache.*(\/\w\/\w\/.*)"
    uri_regex = r"^(.*product)\/cache.*(\/\S\/\S\/.*)"
    uri_matches = re.findall(uri_regex, uri)
    u_match = ''
    for uri_match in uri_matches:
        u_match = ''.join(uri_match)

    cleaned_uri = u_match.replace('http://cdn.roughcountry.com', 'https://d11wx52d6i5kyf.cloudfront.net')
    return cleaned_uri


def replace_unicode_quotes(string):
    uni_quotes = ['\u2019']
    dob_quotes = ['\u0022', '\u201C', '\u201D']
    for ucp in uni_quotes:
        string = string.replace(ucp, "'")
    for dob in dob_quotes:
        string = string.replace(dob, '"')
    return string


def check_imagelinks(imglist):
    for img in imglist:
        try:
            if img != '':
                with urllib.request.urlopen(img) as response:
                    headers = list(response.getheaders())

                    if ('Content-Type', 'image/jpeg') not in headers:
                        print(cColors.FAIL + '\n*** Bad/broken image link found, removing url:\n' + img + '\n' +
                              cColors.ENDC)
                        imglist.pop(imglist.index(img))
        except urllib.error.HTTPError:
            print(cColors.FAIL + '\n*** Bad/broken image link found, removing url:\n' + img + '\n' + cColors.ENDC)
            imglist.pop(imglist.index(img))
    return imglist


def ship_rate(wt):
    weight = float(wt) + 1
    weight = float(weight)
    weight = int(round(weight))
    rates_file = 'data/int_ship_rates.csv'

    rates = {}

    with open(rates_file, newline='') as csvfile:
        rate_reader = csv.DictReader(csvfile, delimiter=',')
        for row in rate_reader:
            rates[row['weight']] = row['cost']

    return rates[str(weight)]
