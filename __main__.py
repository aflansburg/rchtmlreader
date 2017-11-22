import sys
from cli_augments import arg_parser
from htmlreader import read_page

purgeFiles = False
newItem = False
weight = ''
upc = ''
video_link = None

# parse arguments
processedArgs = arg_parser(sys.argv)

if type(processedArgs) == str:
    url = processedArgs
    read_page(url, False)
elif type(processedArgs) == dict:
    read_page(processedArgs, False)
elif type(processedArgs) == list:
    for url_arg in processedArgs:
        read_page(url_arg, True)
else:
    print('\nNo valid URL was supplied. Program will now terminate.')
    exit(0)