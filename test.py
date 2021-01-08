from outlook_connector import MSOutlook
from settings import Config

import time, sys, schedule, csv, os.path, requests


class GetContactOutlook():

  def __init__(self):
    self.__ifpath_contacts = Config.PATH_CONTACTS
    self.__ifpath_contacts_new = Config.PATH_CONTACTS_NEW
    self.__path_files_csv = Config.PATH_CONTACTS_CSV
    self.__path_files_csv_new = Config.PATH_CONTACTS_CSV_NEW

    self.__url = Config.URI
    self.__key = Config.API_KEY
    self.__list_ids = Config.CONSTANT_CONTACT_LIST_IDS

    self.DEBUG = 0

  def getContacts(self):
    try:
      oOutlook = MSOutlook()
      # delayed check for Outlook on win32 box
      if not oOutlook.outlookFound:
        sys.exit(1)

      fields = ['FullName','Email1Address']

      if self.DEBUG:
        startTime = time.time()

      # you can either get all of the data fields
      # or just a specific set of fields which is much faster
      #oOutlook.loadContacts()
      oOutlook.loadContacts(fields)

      contacts = []
      for contact in oOutlook.records:
        contacts.append({
            "fullName": contact['FullName'],
            "email": contact['Email1Address']
        })
        return contacts
    except Exception as e:
      print(e)



  def getDifferenceLists(self, contacts):
    try:
      if not self.__ifpath_contacts:
        return self.__updateListContact(contacts)
      else:
        with open (self.__path_files_csv, newline ='') as csv_file:

          csvreader = csv.DictReader(csv_file)
          contact_list = [row for row in csvreader]
            # get the list of data type OrderedDict
            # from the already created CSV file

        clist = [dict(d) for d in contact_list]
        # get a flat dictionary list without being of type OrderedDict

        contact_difference = [item for item in contacts if item not in clist]
        # comprehension list for get difference between of two lists

        return self.__saveNewContact(contact_difference, contacts)
    except Exception as e:
      print(e)


  def __updateListContact(self, contacts):
    """Function that only runs once as long
    as the contacts.csv file is not created"""

    try:
      with open (self.__path_files_csv, 'w', newline ='') as new_file:

        header = ['fullName', 'email']
        writeFile = csv.DictWriter(new_file, fieldnames= header)
        writeFile.writeheader()

        for row in contacts:
          writeFile.writerow(row)

      if not self.__ifpath_contacts_new:
        return self.__sendtoConstantContact()
    except Exception as e:
      print(e)


  def __saveNewContact(self, contacts_dif, data_contacts):
    """Function that only runs once as long as
    the contacts.csv file is not created """

    try:
      with open (self.__path_files_csv_new, 'w', newline ='') as file:

        header = ['fullName', 'email']

        writeFile = csv.DictWriter(file, fieldnames= header)
        writeFile.writeheader()

        for row in contacts_dif:
          writeFile.writerow(row)

        self.__updateListContact(data_contacts)
        self.__sendtoConstantContact()
    except Exception as e:
      print(e)


  def __sendtoConstantContact(self):
    try:
      headers = {'Authorization': self.__key,
                  'content-type': 'multipart/form-data',
                  'Accept' : 'multipart/form-data'}

      if not self.__ifpath_contacts_new:
        files = {'file': ('contacts.csv', open(self.__path_files_csv, 'rb')),
                  'list_ids' : self.__list_ids}

        response = requests.post(self.__url, headers=headers, files= files)
        print(response)

      else:
        files = {'file_name': ('Newcontacts.csv', open(self.__path_files_csv_new, 'rb')),
                  'list_ids' : self.__list_ids}
        response = requests.post(self.__url, headers=headers, files= files)
    except Exception as e:
      print(e)




win_service = GetContactOutlook()
get_contact = win_service.getContacts()


schedule.every(10).seconds.do(win_service.getDifferenceLists, get_contact)

while 1:
  schedule.run_pending()
  time.sleep(1)