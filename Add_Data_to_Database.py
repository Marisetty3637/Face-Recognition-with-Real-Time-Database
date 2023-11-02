# A real time database is created with the help of Firebase
# Add lib firebase_admin to
# Copied the code from the Firebase

#step 5: Setting Up Database
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json") # here we've just given the file name as it is in the same folder,
# else should provide path
firebase_admin.initialize_app(cred ,{
    'databaseURL' : "https://face-attendance-real-tim-f7534-default-rtdb.firebaseio.com/"
})

# to store inside the database need to create a parent directory i.e students,
# inside students -> Ids of all studnets,
# inside Ids -> Values of all required information

ref = db.reference("Students")  #creating a students path -> imported db

data =  {
    "321654" : {
        "name" : "Murtaza Hassan",
        "Major" : "Robotics",
        "Starting Year" : 2017,
        "Total_Attendance" : 6,
        "standing" : "G",
        "year" : 4,
        "Last_Attendance_time" :  "2023-10-23 00:54:34"   , # attendance is an imp parameter , cz we will take attendace only if he/she comes after 24hrs
    },
    "852741" : {
            "name" : "Emely Blunt",
            "Major" : "Economics",
            "Starting Year" : 2019,
            "Total_Attendance" : 17,
            "standing" : "B",
            "year" : 2,
            "Last_Attendance_time" :  "2023-10-23 00:54:34"   , # attendance is an imp parameter , cz we will take attendace only if he/she comes after 24hrs
        },
    "876541" : {
            "name" : "FlyingFeet",
            "Major" : "Aviation",
            "Starting Year" : 2019,
            "Total_Attendance" : 14,
            "standing" : "Ex",
            "year" : 4,
            "Last_Attendance_time" :  "2023-10-23 00:54:34"   , # attendance is an imp parameter , cz we will take attendace only if he/she comes after 24hrs
        },
    "963852" : {
            "name" : "Elon Musk",
            "Major" : "Physics",
            "Starting Year" : 2021,
            "Total_Attendance" : 6,
            "standing" : "G",
            "year" : 2,
            "Last_Attendance_time" :  "2023-10-23 00:54:34"   , # attendance is an imp parameter , cz we will take attendace only if he/she comes after 24hrs
        }

}

for key, value in data.items():
    ref.child(key).set(value) # to send data to a particular Directory, we use child

#  data is added into dataset , Now we have to add images into directory.
# instead we can do it from Encodings  file while encoding we can directly save images to file.
#check Encocde Generator File
