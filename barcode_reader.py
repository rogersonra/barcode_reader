import os
from googleapiclient.discovery import build
from google.oauth2 import service_account
import winsound
import urllib.request
import json
import logging
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from socket import timeout
# from playsound import playsound

headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'Accept-Encoding': 'gzip,deflate'
}

go_api_key = '520800d09c6f2e451fea958adbd9d32a598784a4af57bc21d083b695b24c9ab9'

SERVICE_ACCOUNT_FILE = 'gs-keys.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

creds = None
creds = service_account.Credentials.from_service_account_file(
		SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Zandax Inventory
SPREADSHEET_ID = '1JT0ZBqYStzik2oo5Gi2NKs9g8WrKFOgQhkyQfjjoIkY'
# Zandax Inventory Test
# SPREADSHEET_ID = '16uwPRXcKPnW1oW1uteBs89XYbynr6hkg-3D7-kVHAdE'

service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

# Populate the locations list with the list of location on the locations sheet
result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
									range="locations!a2:a100").execute()
locations = result.get('values', [])
url = 'https://go-upc.com/api/v1/code/'
saved_location = None


# Get the input from the scanner
while True:
	print("Scan a barcode.  Ctl-c to end.")

	try:
		upc_input = input()
		
		# Check to see if a location was scanned
		location_scanned = False
		if upc_input in str(locations):
			saved_location = str(upc_input)
			frequency = 1400
			duration = 200
			winsound.Beep(frequency, duration)
			frequency = 1700
			winsound.Beep(frequency, duration)
			frequency = 2000
			winsound.Beep(frequency, duration)
			# playsound('/Warn_02.mp3')
		
		# If a location wasn't scanned but saved_location is still blank
		# issue an error.  A location must be scanned first
		elif saved_location == None:
			print("Warning! Scan a location before scanning a upc.\n")
			frequency = 1000
			duration = 700
			winsound.Beep(frequency, duration)
			# playsound('./Warn_01.mp3')
		
		# If a location was not scanned then continue and write the upc
		# to the spreadsheet
		else:
			# Lookup the title for the upc
			endpoint = url + upc_input
			req = Request(endpoint)
			req.add_header('Authorization', 'Bearer ' + go_api_key)

			# resp = requests.get('https://api.upcitemdb.com/prod/trial/lookup?upc=9780439023511', headers=headers)
			# resp = requests.get('https://api.upcitemdb.com/prod/trial/lookup?upc='+upc_input, headers=headers)
			# data = json.loads(resp.text)
			
			try:
				# content = urlopen(req).read()
				content = urlopen(req, timeout=10).read()
				data = json.loads(content.decode())

				upc_title = data["product"]["name"]
				# print(data["title"])
				# for item in data['items']:
				# 	upc_title = item['title']

				gs_input = [[saved_location,upc_input, upc_title]]

				# Append to the spreadsheet
				request = sheet.values().append(spreadsheetId=SPREADSHEET_ID, 
											range="Sheet1!a2", valueInputOption="USER_ENTERED", 
											insertDataOption="INSERT_ROWS", body={"values":gs_input}).execute()
				frequency = 2000
				duration = 200
				winsound.Beep(frequency, duration)

			except HTTPError as error:
				logging.error('HTTP Error: Data of %s not retrieved because %s\nURL: %s', upc_input, error, endpoint)
				frequency = 2500
				duration = 700
				winsound.Beep(frequency, duration)
			except URLError as error:
				frequency = 2500
				duration = 700
				winsound.Beep(frequency, duration)
				if isinstance(error.reason, timeout):
					logging.error('Timeout Error: Data of %s not retrieved because %s\nURL: %s', error, endpoint)
				else:
					logging.error('URL Error: Data of %s not retrieved because %s\nURL: %s', error, endpoint)
			else:
				logging.info('Access successful.')
	except:
		frequency = 1400
		duration = 200
		winsound.Beep(frequency, duration)
		frequency = 1100
		winsound.Beep(frequency, duration)
		frequency = 800
		winsound.Beep(frequency, duration)
		print("Ending program")
		break
