import os
import re


def clean_directories():
    gen_path = 'C:\\Users\\aflansburg\\Dropbox\\Business\\Rough Country\\generated_files'
    sub_dirs = [d for d in os.listdir(gen_path)]

    csvfiles = [name for name in os.listdir(gen_path + '\\csv')]
    if len(csvfiles) >= 1:
        del_prompt = input('Do you wish to purge old files? [y/n]:  ')
        if del_prompt.lower() == 'y':
            for subdir in sub_dirs:
                files = [name for name in os.listdir(gen_path + '\\' + subdir)]
                for f in files:
                    os.remove(gen_path + '\\' + subdir + '\\' + f)


def uri_cleaner(uri):
    uri_regex = r"^(.*product)\/cache.*(\/\w\/\w\/.*)"
    uri_matches = re.findall(uri_regex, uri)
    u_match = ''
    for uri_match in uri_matches:
        u_match = ''.join(uri_match)

    cleaned_uri = u_match.replace('http://cdn.roughcountry.com', 'https://d11wx52d6i5kyf.cloudfront.net')
    return cleaned_uri


def replace_unicode_quotes(string):
    uni_quotes = ['\u2019', '\u0022', '\u8220',
                  '\u8221', '\u201C', '\u201D']
    for ucp in uni_quotes:
        string = string.replace(ucp, '"')
    return string
