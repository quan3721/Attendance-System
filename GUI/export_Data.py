import firebase_admin
from firebase_admin import credentials, db
import json
from reset_date import *
# Initialize the Firebase app
cred = credentials.Certificate('../Database_Firebase/attendance-system-f3c35-firebase-adminsdk-s7c8b-2b1990099a.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://attendance-system-f3c35-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# Fetch data from the Realtime Database
def fetch_database_data(ref='/'):
    ref = db.reference(ref)
    data = ref.get()
    return data

# Export data to a JSON file
def export_to_json(ref, file_name):
    data = fetch_database_data(ref)
    with open(file_name, 'w') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

def export_data(ref_export,datetime_final_in_month,check_date_had,total_attendance,first_day_in_month=1):
    if (datetime_final_in_month - first_day_in_month >= 29) and (16 <= total_attendance <= 25):
        file_name = db.reference(f'{ref_export}/Name').get()
        list_contain_file_name = file_name.split(' ')
        file_name = "_".join(list_contain_file_name)
        export_to_json(ref_export,f'{file_name.json}')
    else:
        pass

if __name__ == '__main__':
    # Example usage
    # ref= 'Employee/23'
    # file_name = db.reference(f'{ref}/Name').get()
    # list_contain_file_name = file_name.split(' ')
    # file_name = "_".join(list_contain_file_name)
    # export_to_json(ref, f'{file_name}.json')
    export_data()

