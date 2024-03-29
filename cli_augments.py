import validators
import csv
import os

base_dir = ''
ws_dir = ''
sc_dir = ''
j_dir = ''
amz_dir = ''
gen_dir = ''
csv_dir = ''
dir_slash = ''

if os.name == "posix":
    base_dir = '/Users/abram/Dropbox/Business/Rough Country/'
    ws_dir = 'WebstormProjects/template_builder/'
    sc_dir = 'generated_files/sc-line/'
    j_dir = 'generated_files/jobber_lines/'
    amz_dir = 'generated_files/amzFiles/'
    csv_dir = 'generated_files/csv/'
    gen_dir = 'generated_files/'
    dir_slash = '/'
elif os.name == "nt":
    base_dir = 'C:\\Users\\aflansburg\\Dropbox\\Business\\Rough Country\\'
    ws_dir = 'WebstormProjects\\template_builder\\'
    sc_dir = 'generated_files\\sc-line\\'
    j_dir = 'generated_files\\jobber_lines\\'
    amz_dir = 'generated_files\\amzFiles\\'
    csv_dir = 'generated_files\\csv\\'
    gen_dir = 'generated_files\\'
    dir_slash = '\\'


class ConsoleColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m',
    NORMAL = '\033[1;37m'


def clean_directories():
    gen_path = base_dir + gen_dir
    sub_dirs = [d for d in os.listdir(gen_path)]
    file_rm_count = 0
    try:
        for subdir in sub_dirs:

            full = gen_path + subdir
            if os.path.isdir(full):
                files = [name for name in os.listdir(gen_path + subdir)]
                for f in files:
                    if f != 'multi-file.csv' and f !='.DS_Store':
                        os.remove(gen_path + subdir + dir_slash + f)
                        file_rm_count += 1
    except PermissionError:
        print(ConsoleColors.FAIL + '\nFiles could not be purged due to file being open. Files will not be purged.\n' +
              ConsoleColors.ENDC)
    print(f'\n{file_rm_count} files were purged.')


def arg_parser(args):
    insert_video = False
    new_item = False
    url = None
    video_link = ''
    upc = ''
    multi_url_path = ''
    multi_urls = False
    get_vid_path = ''
    dealerDiscount = ''

    if args[1] not in ['-purge', '-p', '-n', '-new', '-v', '-video', '-m', '-multi', '-combine', '-c', '-getvids']:
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
                dealerDiscount = input('\nPlease enter the product\'s dealer discount: ' + ConsoleColors.ENDC)
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
            if str(arg).lower() in ['-combine', '-c']:
                scpath = r"C:\Users\aflansburg\Dropbox\Business\Rough Country\generated_files\sc-line"
                scfiles = os.listdir(scpath)
                # scfiles = [ff for ff in os.listdir(r"C:\Users\aflansburg\Dropbox\Business\Rough Country\generated_files\sc-line") if os.path.isfile(ff) and ff.endswith(".csv")]
                data = []
                for scfile in scfiles:
                    with open(scpath + "\\" + scfile, 'r') as f:
                        reader = csv.reader(f)
                        data.append(list(reader))
                headers = data[0][0]
                with open(scpath + "\\" + 'sc-combined.csv', 'a') as outfile:
                    writer = csv.writer(outfile, delimiter=',', lineterminator='\n')
                    writer.writerow(list(headers))
                    for d in data:
                        for i in d:
                            if d.index(i) != 0 and i != '':
                                writer.writerow(i)
                outfile.close()
                print(ConsoleColors.WARNING + '\nSC lines combined -> sc-combined.csv\n')
            if str(arg).lower() in ['-cjobber', '-cj']:
                jpath = r"C:\Users\aflansburg\Dropbox\Business\Rough Country\generated_files\jobber_lines"
                jfiles = os.listdir(jpath)
                data = []
                for jfile in jfiles:
                    with open(jpath + "\\" + jfile, 'r') as jf:
                        reader = csv.reader(jf)
                        data.append(list(reader))
                headers = data[0][0]
                with open(jpath + "\\" + 'jobber-combined.csv', 'a') as outfile:
                    writer = csv.writer(outfile, delimiter=',', lineterminator='\n')
                    writer.writerow(list(headers))
                    for d in data:
                        for i in d:
                            if d.index(i) != 0 and i != '':
                                writer.writerow(i)
                outfile.close()
                print(ConsoleColors.WARNING + '\nJobber lines combined -> jobber-combined.csv\n')
            if str(arg).lower() in ['camazon', '-ca']:
                apath = r"C:\Users\aflansburg\Dropbox\Business\Rough Country\generated_files\amzFiles"
                afiles = os.listdir(apath)
                data = []
                for afile in afiles:
                    with open(apath + "\\" + afile, 'r') as af:
                        reader = csv.reader(af)
                        data.append(list(reader))
                headers = data[0][0]
                with open(apath + "\\" + 'amz-combined.csv', 'a') as outfile:
                    writer = csv.writer(outfile, delimiter=',', lineterminator='\n')
                    writer.writerow(list(headers))
                    for d in data:
                        for i in d:
                            if d.index(i) != 0 and i != '':
                                writer.writerow(i)
                outfile.close()
                print(ConsoleColors.WARNING + '\nAmazon lines combined -> amz-combined.csv\n')
            if str(arg).lower() in ['-getvids']:
                get_vid_path = input(ConsoleColors.WARNING +
                                       '\nEnter the path to the csv containing the list of urls:\n' +
                                       ConsoleColors.ENDC)
                # Get youtube video link (if exists) here

    if url is not None:
        if new_item and insert_video:
            parsed_args = {'UPC': upc, 'Weight': weight, 'Video Link': video_link, 'URL': url}
            return parsed_args
        elif new_item:
            print(url)
            parsed_args = {'UPC': upc, 'Weight': weight, 'URL': url, 'Video Link': video_link, 'URL': url, 'Discount': dealerDiscount}
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

