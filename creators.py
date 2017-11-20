import csv
import datetime
import re
from helpers import ship_rate as canship
from cli_augments import ConsoleColors as cColors

now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")


def create_jobber(product, images):
    jobber_file_location = 'C:\\Users\\aflansburg\\Dropbox\\Business\\Rough Country\\generated_files\\jobber_lines\\'

    if product['SKU'] != '':
        jobber_filename = jobber_file_location + product['SKU'] + '_jobber.csv'
    else:
        jobber_filename = jobber_file_location + 'Item_' + now + '_jobber.csv'

    try:
        open(jobber_filename, "r+")
    except FileNotFoundError:
        print(cColors.WARNING + "\nJobber file doesn't exist. Creating...\n" + cColors.ENDC)
    except PermissionError:
        jobber_filename = jobber_file_location + product['SKU'] + '_' + now + '_jobber.csv'

    jobber_fields = ['MPN', 'Item Type', 'MAP', 'Discount %', 'Your Cost', 'Title',
                     'Strut/Shock Series', 'Start Year', 'End Year', 'Make',
                     'Model', 'Drive', 'Combined Fitment', 'Description', 'Kit products',
                     'Benefits', 'Technical Notes', 'Item Specifics', 'Weight (Lbs)',
                     'US Shipping', 'CAN Shipping', 'Image 1', 'Image 2', 'Image 3', 'Image 4',
                     'Image 5', 'Image 6', 'Image 7', 'Image 8', 'Image 9', 'Video Link', 'Superseded', 'Warranty',
                     'UPC Code', 'Flat Discount %']

    jobber_dict = {'MPN': product['SKU'], 'Title': product['Title'], 'Description': product['Description'],
                   'Benefits': product['Features'], 'Combined Fitment': product['Fitment'],
                   'Kit products': product['In The Box'], 'Technical Notes': product['Notes'], 'US Shipping': 0,
                   'MAP': product['Price'], 'Item Specifics': product['Specs'], 'Video Link': product['video_link'],
                   'Image 1': product['MainImg'], 'Warranty': 'Limited Lifetime', 'UPC Code': product['UPC']}

    if product['Weight'] != '' and type(product['Weight'] != str):
        jobber_dict['Weight (Lbs)'] = product['Weight']
        jobber_dict['CAN Shipping'] = canship(product['Weight'])

    if product['MainImg'] in images:
        images.pop(images.index(product['MainImg']))

    if len(images) > 0:
        for image in images:
            index = images.index(image) + 2
            key_string = 'Image ' + str(index)
            jobber_dict[key_string] = image

    with open(jobber_filename, 'w', newline='') as jobberCsvFile:
        jobber_writer = csv.DictWriter(jobberCsvFile, fieldnames=jobber_fields)

        fitments = product['Fitment'].split("; ")
        regex_starts = r"^\d{4}-\d{4}"
        for item in (item for item in fitments if not re.match(regex_starts, item)):
            fitments.pop(fitments.index(item))

        jobber_writer.writeheader()

        if len(fitments) > 1:
            for fitment in fitments:
                multi_dict = jobber_dict.copy()
                multi_fit = get_multifits(fitment)
                if multi_fit is not None:
                    multi_dict.update(multi_fit)
                    jobber_writer.writerow(multi_dict)
        else:
            jobber_writer.writerow(jobber_dict)

        jobberCsvFile.close()
        print(cColors.WARNING + "Jobber file created @ " + jobber_filename + '.' + cColors.ENDC)


def create_amazon(product, images):
    amz_file_file_location = 'C:\\Users\\aflansburg\\Dropbox\\Business\\Rough Country\\generated_files\\amzFiles\\'
    if product['SKU'] != '':
        amz_file_filename = amz_file_file_location + product['SKU'] + '_amzFile.csv'
    else:
        amz_file_filename = amz_file_file_location + 'Item_' + now + '_amzFile.csv'

    try:
        open(amz_file_filename, "r+")
    except FileNotFoundError:
        print(cColors.WARNING + "\nAmazon file doesn't exist. Creating....\n" + cColors.ENDC)
    except PermissionError:
        amz_file_filename = amz_file_file_location + itemSku + '_' + now + '_amzFile.csv'

    amz_file_fields = ['item_sku', 'item_name', 'part_number', 'standard_price', 'main_image_url', 'other_image_url1',
                       'other_image_url2', 'other_image_url3', 'product_description', 'bullet_point1',
                       'bullet_point2', 'bullet_point3', 'bullet_point4', 'bullet_point5']

    with open(amz_file_filename, 'w', newline='') as amzFileCsvFile:
        amz_file_writer = csv.DictWriter(amzFileCsvFile, fieldnames=amz_file_fields)

        amz_file_writer.writeheader()

        if len(images) == 0:
            amz_file_writer.writerow({'item_sku': product['SKU'], 'product_description': product['Description'],
                                      'item_name': product['Title'],
                                      'bullet_point1': 'Features: ' + product['Features'],
                                      'bullet_point2': 'Fits: ' + product['Fitment'],
                                      'bullet_point4': 'Kit products: ' + product['In The Box'],
                                      'part_number': product['SKU'], 'bullet_point3': 'Notes: ' + product['Notes'],
                                      'standard_price': product['Price'], 'bullet_point5': 'Specs: ' +
                                                                                           product['Specs'],
                                      'main_image_url': product['MainImg']})

        if len(images) == 1:
            amz_file_writer.writerow({'item_sku': product['SKU'], 'product_description': product['Description'],
                                      'item_name': product['Title'], 'bullet_point1': 'Features: ' +
                                                                                      product['Features'],
                                      'bullet_point2': 'Fits: ' + product['Fitment'],
                                      'bullet_point4': 'Kit products: ' + product['In The Box'],
                                      'part_number': product['SKU'], 'bullet_point3': 'Notes: ' + product['Notes'],
                                      'standard_price': product['Price'], 'bullet_point5': 'Specs: ' +
                                                                                           product['Specs'],
                                      'main_image_url': images[0]})
        if len(images) == 2:
            amz_file_writer.writerow({'item_sku': product['SKU'], 'product_description': product['Description'],
                                      'item_name': product['Title'], 'bullet_point1': 'Features: ' +
                                                                                      product['Features'],
                                      'bullet_point2': 'Fits: ' + product['Fitment'],
                                      'bullet_point4': 'Kit products: ' + product['In The Box'],
                                      'part_number': product['SKU'], 'bullet_point3': 'Notes: ' + product['Notes'],
                                      'standard_price': product['Price'], 'bullet_point5': 'Specs: ' +
                                                                                           product['Specs'],
                                      'main_image_url': images[0],
                                      'other_image_url1': images[1]})
        if len(images) == 3:
            amz_file_writer.writerow({'item_sku': product['SKU'], 'product_description': product['Description'],
                                      'item_name': product['Title'], 'bullet_point1': 'Features: ' +
                                                                                      product['Features'],
                                      'bullet_point2': 'Fits: ' + product['Fitment'],
                                      'bullet_point4': 'Kit products: ' + product['In The Box'],
                                      'part_number': product['SKU'], 'bullet_point3': 'Notes: ' + product['Notes'],
                                      'standard_price': product['Price'], 'bullet_point5': 'Specs: ' +
                                                                                           product['Specs'],
                                      'main_image_url': images[0],
                                      'other_image_url1': images[1], 'other_image_url2': images[2]})
        if len(images) >= 4:
            amz_file_writer.writerow({'item_sku': product['SKU'], 'product_description': product['Description'],
                                      'item_name': product['Title'], 'bullet_point1': 'Features: ' +
                                                                                      product['Features'],
                                      'bullet_point2': 'Fits: ' + product['Fitment'],
                                      'bullet_point4': 'Kit products: ' + product['In The Box'],
                                      'part_number': product['SKU'], 'bullet_point3': 'Notes: ' + product['Notes'],
                                      'standard_price': product['Price'], 'bullet_point5': 'Specs: ' +
                                                                                           product['Specs'],
                                      'main_image_url': images[0],
                                      'other_image_url1': images[1], 'other_image_url2': images[2],
                                      'other_image_url3': images[3]})

        amzFileCsvFile.close()


def get_multifits(fitment):
    # years
    regex_years = r"(\d{4})-(\d{4})"

    # drive type
    regex_drive = r"(\dWD)"

    # make
    regex_make = r"WD\s(\S+)\s"

    # model
    regex_model = r"WD\s\S+\s(.*)"

    years = re.finditer(regex_years, fitment)
    for year in years:
        start_year = year.group(1)
        end_year = year.group(2)

    drive_matches = re.findall(regex_drive, fitment)

    if drive_matches:
        if len(drive_matches) == 2:
            drive_type = drive_matches[1] + '/' + drive_matches[0]
        else:
            drive_type = drive_matches[0]

        make = re.finditer(regex_make, fitment)
        for match in make:
            v_make = match.group(1)

        model = re.finditer(regex_model, fitment)

        for m in model:
            v_model = m.group(1)

        fitment_details = {'Start Year': start_year, 'End Year': end_year, 'Make': v_make, 'Model': v_model,
                           'Drive': drive_type}
        return fitment_details