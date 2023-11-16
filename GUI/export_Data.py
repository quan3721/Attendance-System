import json

path_folder = '/home/pi/Desktop/Attendance_system/data_employee'
# Export data to a JSON file
def export_to_json(file_name,data):
    with open(file_name, 'w') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

def export_data(datetime_final_in_month,data,file_name,month_now_export,first_day_in_month=1):
    if month_now_export != 2:
        if datetime_final_in_month == 3:
            if (datetime_final_in_month - first_day_in_month == 2):
                file_name = file_name
                list_contain_file_name = file_name.split(' ')
                file_name = "_".join(list_contain_file_name)
                data = data
                export_to_json(f'{path_folder}/{file_name}.json',data=data)
            else:
                pass
    elif month_now_export == 2:
        if datetime_final_in_month == 28:
            if (datetime_final_in_month - first_day_in_month == 27):
                file_name = file_name
                list_contain_file_name = file_name.split(' ')
                file_name = "_".join(list_contain_file_name)
                data = data
                export_to_json(f'{path_folder}/{file_name}.json',data=data)
if __name__ == '__main__':
    export_data()