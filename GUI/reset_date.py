# import firebase_admin
# from firebase_admin import credentials
# from firebase_admin import db
# cred = credentials.Certificate("../Database_Firebase/attendance-system-f3c35-firebase-adminsdk-s7c8b-2b1990099a.json")
# firebase_admin.initialize_app(cred,{
#     'databaseURL' : 'https://attendance-system-f3c35-default-rtdb.asia-southeast1.firebasedatabase.app/',
# })
######################################################################
def reset_data(ref_rs,datetime_final_in_month,month_now,first_day_in_month=1):
    if month_now != 2:
        if datetime_final_in_month == 30:
            if (datetime_final_in_month - first_day_in_month == 29):
                ref_rs.child('Last attendance in').set("")
                ref_rs.child('Last attendance out').set("")
                ref_rs.child('Total attendance in Month').set(0)
                ref_rs.child('List of Workday').set("")
    else:
        if datetime_final_in_month == 28:
            if (datetime_final_in_month - first_day_in_month == 27):
                ref_rs.child('Last attendance in').set("")
                ref_rs.child('Last attendance out').set("")
                ref_rs.child('Total attendance in Month').set(0)
                ref_rs.child('List of Workday').set("")
if __name__ == '__main__':
    reset_data()