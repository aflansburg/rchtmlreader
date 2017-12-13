import validators
import csv
import os


class ConsoleColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def clean_directories():
    gen_path = 'C:\\Users\\aflansburg\\Dropbox\\Business\\Rough Country\\generated_files'
    sub_dirs = [d for d in os.listdir(gen_path)]
    file_rm_count = 0

    try:
        for subdir in sub_dirs:
            file_rm_count += 1
            files = [name for name in os.listdir(gen_path + '\\' + subdir)]
            for f in files:
                if f != 'multi-file.csv':
                    os.remove(gen_path + '\\' + subdir + '\\' + f)
        print(f'\n{file_rm_count} files were purged.')
    except PermissionError:
        print(ConsoleColors.FAIL + '\nFiles could not be purged due to file being open. Files will not be purged.\n' +
              ConsoleColors.ENDC)


def arg_parser(args):
    insert_video = False
    new_item = False
    url = None
    video_link = ''
    upc = ''
    multi_url_path = ''
    multi_urls = False

    if args[1] not in ['-purge', '-p', '-n', '-new', '-v', '-video', '-m', '-multi']:
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
                purge = input(ConsoleColors.FAIL + '\nAre you sure you want to purge all files [Y/N]?: ' +
                              ConsoleColors.ENDC)
                if purge.lower() == 'yes' or 'y' or 'ye' or 'si' or 'ja' or 'oui':
                    clean_directories()
                else:
                    print(ConsoleColors.WARNING + '\nDirectory purge canceled.\n' + ConsoleColors.ENDC)
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
            if str(arg).lower() in ['-m', '-multi', '-multiple', '-multiples']:
                multi_url_path = input(ConsoleColors.WARNING +
                                       '\nEnter the path to the csv containing the list of URLS:\n' +
                                       ConsoleColors.ENDC)
                multi_urls = True

    if url is not None:
        if new_item and insert_video:
            parsed_args = {'UPC': upc, 'Weight': weight, 'Video Link': video_link, 'URL': url}
            return parsed_args
        elif new_item:
            print(url)
            parsed_args = {'UPC': upc, 'Weight': weight, 'URL': url, 'Video Link': video_link, 'URL': url}
            return parsed_args
        elif insert_video:
            parsed_args = {'Video Link': video_link, 'URL': url}
            return parsed_args
        else:
            return url
    elif multi_urls:
        url_list = []
        with open(multi_url_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                url_list.append(row[0])
        return url_list
    else:
        return False

