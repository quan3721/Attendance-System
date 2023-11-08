# import firebase_admin
# from firebase_admin import credentials
# from firebase_admin import db
# cred = credentials.Certificate("../Database_Firebase/attendance-system-f3c35-firebase-adminsdk-s7c8b-2b1990099a.json")
# firebase_admin.initialize_app(cred,{
#     'databaseURL' : 'https://attendance-system-f3c35-default-rtdb.asia-southeast1.firebasedatabase.app/',
# })
######################################################################
def reset_data(ref,datetime_final_in_month,check_date_had,total_attendance,first_day_in_month=1):
    if (datetime_final_in_month - first_day_in_month >= 21) and (16 <= total_attendance <= 25) :

        data = {
            "23":  # is id Number of each person
                {
                    "Name": "Nguyen Dinh Hong Quan",
                    "Position": "IT",
                    "Starting year": 2023,
                    "Total attendance in Month": 0,
                    "Last attendance in": "",
                    "Last attendance out": "",
                    "List of Workday":
                        {
                        },
                    "Date of Birth": "30-07-2001",
                    "Address": "TD"
                },
            "31":  # is id Number of each person
                {
                    "Name": "Nguyen Gia Hung",
                    "Position": "Engineer",
                    "Starting year": 2022,
                    "Total attendance in Month": 0,
                    "Last attendance in": "",
                    "Last attendance out": "",
                    "List of Workday":
                        {
                        },
                    "Date of Birth": "30-07-2001",
                    "Address": "TD"
                }
        }
        for key, value in data.items():
            ref.child(key).set(value)

    elif (datetime_final_in_month - first_day_in_month >= 21) and check_date_had == "":
        pass

if __name__ == '__main__':
    reset_data()