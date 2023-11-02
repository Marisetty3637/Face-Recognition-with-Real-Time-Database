# we have ṭo generate the data for all those 128 data measurement, and have to store that in the file.
# that file is imported into our face recognition, and then it will display whether it has detected that face or not.

import os
import cv2 as cv
import face_recognition
import pickle
#importing libraries from database file to access
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json") # here we've just given the file name as it is in the same folder,
# else should provide path
firebase_admin.initialize_app(cred ,{
    'databaseURL' : "https://face-attendance-real-tim-f7534-default-rtdb.firebaseio.com/",
    'storageBucket': "face-attendance-real-tim-f7534.appspot.com"  #ading storage bucket link
})

#step 3: Encode Generator
# importing the student images
folderPath = 'Images'
Pathlist = os.listdir(folderPath)   # gets the list of all the files
imgList = []          # folder that contains all the list in the form of array, to pass to cv.imread()
studentsIds = []      # need to have student ids as well, which is name of images.

# getting the path of each image in the Image Directory
for path in Pathlist:
    imgList.append(cv.imread(os.path.join(folderPath, path)))
    studentsIds.append(os.path.splitext(path)[0])  # this seperates the png(extension) from path

    ## Step 7: Adding Images to Database
    # with this we will be creating a file Images and adding files into it.
    fileName = f'{folderPath}/{path}' # getting the filename
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)
print(studentsIds)

#Encode: Numerical representation of all the extracted features from the face.
# now these list items will be send into a function which generates the encodings
# we will be loop through all the images and encode every single image.
def findEncodings(imageList):

    encodeList = []

    for img in imageList:
        #change color from BGR to RGB
        img = cv.cvtColor(img , cv.COLOR_BGR2RGB)

        encode = face_recognition.face_encodings(img)[0]  # this is how we get the encodings of any image
        encodeList.append(encode)
    return encodeList

print("Encoding has started")
encodeListknown = findEncodings(imgList)
encodeListknownwithIds = [encodeListknown , studentsIds]
# print(encodeListknown)
print("Encoding Complete")

# Now we have to  save it in a pikle file so that we can us eit when we are using webcam
# make sure to save both encodings and ids of every image.
# way of pickling
file = open("Encodefile.p" , "wb")
pickle.dump(encodeListknownwithIds , file)
file.close()
print("File saved") # Dump Completed
