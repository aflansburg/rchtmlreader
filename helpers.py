import os
import re
import urllib.request
import urllib.error


def clean_directories():
    gen_path = 'C:\\Users\\aflansburg\\Dropbox\\Business\\Rough Country\\generated_files'
    sub_dirs = [d for d in os.listdir(gen_path)]

    # csvfiles = [name for name in os.listdir(gen_path + '\\csv')]
    # if len(csvfiles) >= 1:
    try:
        for subdir in sub_dirs:
            files = [name for name in os.listdir(gen_path + '\\' + subdir)]
            for f in files:
                os.remove(gen_path + '\\' + subdir + '\\' + f)
    except PermissionError:
        print('Files could not be purged - one must be open. Continuing.')
    # else:
    #     print('There were no files to purge!')


def uri_cleaner(uri):
    uri_regex = r"^(.*product)\/cache.*(\/\w\/\w\/.*)"
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
            with urllib.request.urlopen(img) as response:
                headers = list(response.getheaders())

                if ('Content-Type', 'image/jpeg') not in headers:
                    print('*** Bad/broken image link found, removing url:\n' + 'img')
                    imglist.pop(imglist.index(img))
        except urllib.error.HTTPError:
            print('*** Bad/broken image link found, removing url:\n' + 'img')
            imglist.pop(imglist.index(img))
    return imglist

