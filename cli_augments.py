import helpers
import validators


class ConsoleColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# implemented but not used


def arg_parser(args):
    insert_video = False
    new_item = False
    url = None
    video_link = ''
    upc = ''

    if args[1] not in ['-purge', '-p', '-n', '-new', '-v', '-video']:
        try:
            if validators.url(args[1]):
                url = str(args[1])
                print("\nUrl validated...")
            else:
                print('\nNo valid URL supplied.')
        except IndexError:
            print('\nNo URL supplied')

    if len(args) < 2:
        print(ConsoleColors.OKGREEN + '\nNo command line arguments were found. Continuing...' + ConsoleColors.ENDC)
    else:
        for arg in args:
            if str(arg).lower() in ['-purge', '-p']:
                purge = input(ConsoleColors.WARNING + '\nAre you sure you want to purge all files [Y/N]?: ' +
                              ConsoleColors.ENDC)
                if purge.lower() == 'yes' or 'y' or 'ye' or 'si' or 'ja' or 'oui':
                    helpers.clean_directories()
            if str(arg).lower() in ['-n', '-new'] and url is not None:
                new_item = True
                print(ConsoleColors.WARNING + '\nNew product creation request.\n')
                upc = input(ConsoleColors.WARNING + 'Please enter the product\'s UPC: ' + ConsoleColors.ENDC)
                weight = input('\nPlease enter the product\'s weight in Lbs: ' + ConsoleColors.ENDC)
            if str(arg).lower() in ['-v', '-video'] and url is not None:
                v_link_index = args.index(arg) + 1
                if args[v_link_index]:
                    insert_video = True
                    video_link = args[v_link_index]
                print('\nVideo Link Processed!')

    if url is not None:
        if new_item and insert_video:
            parsed_args = {'UPC': upc, 'Weight': weight, 'Video Link': video_link, 'URL': url}
            return parsed_args
        elif new_item:
            print(url)
            parsed_args = {'UPC': upc, 'Weight': weight, 'URL': url}
            return parsed_args
        elif insert_video:
            parsed_args = {'Video Link': video_link, 'URL': url}
            return parsed_args
        else:
            return url
    else:
        return False

