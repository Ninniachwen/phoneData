import requests
from bs4 import BeautifulSoup
import csv
import os
import time
import json

# Class gsmarena scrap the website phones models and its devices and save to csv file individually.
class Gsmarena():

    # Constructor to initialize common useful varibales throughout the program.
    # edited: read cwd path on any os
    def __init__(self):
        self.phones = []
        self.features = ["Brand", "Model Name", "Model Image"]
        self.temp1 = []
        self.phones_brands = []
        self.url = 'https://www.gsmarena.com/' # GSMArena website url
        self.new_folder_name = 'GSMArenaDataset' # Folder name on which files going to save.
        self.path = os.getcwd()
        self.absolute_path = os.path.join(self.path, self.new_folder_name)   # It create the absolute path of the GSMArenaDataset folder.
        self.temp_folder = os.path.join(self.absolute_path, 'temp')

    # This function crawl the html code of the requested URL.
    # edited: more specific error messages
    def read_or_crawl_html_page(self, sub_url, use_cash=True):
        soup = None
        if use_cash:    # try to read from cash
            soup = self.read_if_temp_exists(sub_url.replace('/', '_'))
        if soup == None:    # if read failed or if use_cash==False, crawl instead
            try:
                soup = self.crawl_html_page(sub_url)
            except Exception as e:
                print(f"Operation failed: {e}")
                return None
        return soup

    # This function crawl the html code of the requested URL.
    # edited: more specific error messages
    def crawl_html_page(self, sub_url):
        url = self.url + sub_url  # Url for html content parsing.
        header={"User-Agent":"#user agent of your system  "}
        print(f"querying for {sub_url}...")
        time.sleep(30)  #SO that your IP does not gets blocked by the website
        # Handing the connection error of the url.
        try:
            page = requests.get(url,timeout= 5, headers=header)
            soup = BeautifulSoup(page.text, 'html.parser')  # It parses the html data from requested url.

            if soup.find(text="Too Many Requests"):
                raise Exception("Too Many Requests: GSMArena has blocked requests from your IP address temporarily.")

            self.store_temp(soup.prettify(), sub_url.replace('/', '_'))

            return soup

        except ConnectionError as err:
            print(f"Connection Error: {err}")
            print("Please check your network connection.")
            raise

        except Exception as e:
            print(f"Error occurred: {e}")
            raise

    # store objects temporarily on disc
    # by ML
    def store_temp(self, item: str, filename: str) -> bool:
        self.create_folder(self.temp_folder)
        with open(os.path.join(self.temp_folder, filename), 'w', encoding='utf-8') as file:
            written = file.write(item)  # Write the HTML with formatting
        return written > 0   # flag whether write was successful
    
    # read temp soup from disc or read from web
    # by ML
    def read_if_temp_exists(self, name: str) -> BeautifulSoup|None:
        files_list = self.check_file_exists(self.temp_folder)   # file list or empty list
        if name in files_list:
            file_path = os.path.join(self.temp_folder, name)  # create abs file path to read from
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()  # Read the HTML from file
            return BeautifulSoup(html_content, 'html.parser')   # Recreate the soup object
        else:
            return None # no file matched the filename

    # This function crawl mobile phones brands and return the list of the brands.
    # edited by ML: cash soup on disc
    def crawl_phone_brands(self):
        phones_brands = []
        soup = self.read_or_crawl_html_page('makers.php3')
        if not soup:
            raise Exception("makers soup empty") 
        table = soup.find_all('table')[0]
        table_a = table.find_all('a')
        for a in table_a:
            temp = [a['href'].split('-')[0], a.find('span').text.split(' ')[0], a['href']]
            phones_brands.append(temp)
        return phones_brands

    # This function crawl mobile phones brands models links and return the list of the links.
    def crawl_phones_models(self, phone_brand_link):
        links = []
        nav_link = []
        soup = self.read_or_crawl_html_page(phone_brand_link)
        if not soup:
            raise Exception(f"brand soup empty: {phone_brand_link}") 
        nav_data = soup.find(class_='nav-pages')
        if not nav_data:
            nav_link.append(phone_brand_link)
        else:
            nav_link = nav_data.findAll('a')
            nav_link = [link['href'] for link in nav_link]
            nav_link.append(phone_brand_link)
            nav_link.insert(0, nav_link.pop())
        for link in nav_link:
            soup = self.read_or_crawl_html_page(link)
            data = soup.find(class_='section-body')
            if not data: continue   # if data is empty, skip this model
            for line1 in data.findAll('a'):
                links.append(line1['href'])

        return links

    # This function crawl mobile phones specification and return the list of the all devices list of single brand.
    def crawl_phones_models_specification(self, link, phone_brand):
        phone_data = {}
        soup = self.read_or_crawl_html_page(link)
        model_name = soup.find(class_='specs-phone-name-title').text
        model_img_html = soup.find(class_='specs-photo-main')
        model_img = model_img_html.find('img')['src']
        phone_data.update({"Brand": phone_brand})
        phone_data.update({"Model Name": model_name})
        phone_data.update({"Model Image": model_img})
        temp = []
        for data1 in range(len(soup.findAll('table'))):
            table = soup.findAll('table')[data1]
            for line in table.findAll('tr'):
                temp = []
                for l in line.findAll('td'):
                    text = l.getText()
                    text = text.strip()
                    text = text.lstrip()
                    text = text.rstrip()
                    text = text.replace("\n", "")
                    temp.append(text)
                    if temp[0] in phone_data.keys():
                        temp[0] = temp[0] + '_1'
                    if temp[0] not in self.features:
                        self.features.append(temp[0])
                if not temp:
                    continue
                else:
                    phone_data.update({temp[0]: temp[1]})
        return phone_data

    # This function create the folder 'GSMArenaDataset'.
    # by ML
    def create_folder(self, folder_path):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print("Creating ", folder_path, " Folder....")
            time.sleep(6)
            print("Folder Created.")
        else:
            print(folder_path , "directory already exists")
        

    # Returns a list of files in the specified folder, or an empty list if the folder doesn't exist.
    # edited by ML: prevent exception if folder doesn't exist
    def check_file_exists(self, absolute_path):
        if os.path.exists(absolute_path):
            return os.listdir(absolute_path)
        return []  # Return empty list if folder does not exist

    # This function save the devices specification to csv file.
    def save_specification_to_file(self):
        phone_brand = self.crawl_phone_brands()
        self.create_folder(self.new_folder_name)
        files_list = self.check_file_exists(self.absolute_path)
        for brand in phone_brand:
            phones_data = []
            if (brand[0].title() + '.csv') not in files_list:
                link = self.crawl_phones_models(brand[2])
                model_value = 1
                print("Working on", brand[0].title(), "brand.")
                for value in link:
                    datum = self.crawl_phones_models_specification(value, brand[0])
                    datum = { k:v.replace('\n', ' ').replace('\r', ' ') for k,v in datum.items() }
                    phones_data.append(datum)
                    print("Completed ", model_value, "/", len(link))
                    model_value+=1
                with open(os.path.join(self.absolute_path, brand[0].title() + ".csv"), "w")  as file:
                    dict_writer = csv.DictWriter(file, fieldnames=self.features)
                    dict_writer.writeheader()
                    str_phones_data = json.dumps(phones_data)
                    encoded = str_phones_data.encode('utf-8')
                    load_list = json.loads(encoded)
                    for dicti in load_list:
                        dict_writer.writerow({k:v.encode('utf-8') for k,v in dicti.items()})
                print("Data loaded in the file")
            else:
                print(brand[0].title() + '.csv file already in your directory.')


# This is the main function which create the object of Gsmarena class and call the save_specificiton_to_file function.
i = 1
while i == 1:
    if __name__ == "__main__":
        obj = Gsmarena()
        try:
            obj.save_specification_to_file()
        except KeyboardInterrupt:
            print("File has been stopped due to KeyBoard Interruption.")
