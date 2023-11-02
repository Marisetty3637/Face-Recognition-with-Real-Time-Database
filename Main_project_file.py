#we are going to write all the codes with real time database
import os
import pickle
import cv2 as cv
import face_recognition
import numpy as np
import cvzone
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

#step 7: retreiving images from database
bucket = storage.bucket()

# Now when the face is detected, we need to fetch the data from database and display it for a few secs on ghraphics
cam = cv.VideoCapture(0)

#setting property of video capture
#since our image background is 640*480
cam.set(3 , 640)   #prop 3: Width
cam.set(4, 480)     #prop 4: height

#importing graphics
imgBackground = cv.imread("Resources/background.png")  #(480*640) - height*width
#next step is to bring in the Modes i.e Active , student database , marked , already Marked

#importing the mode images into a list
folderModepath = "Resources/Modes"
modePathlist = os.listdir(folderModepath)  #gets the list of all the files
imgModeList = []  #folder that contains all the list in the form of array, to pass to cv.imread()

#getting the path of each image in the Mode Directory
for path in modePathlist:
    imgModeList.append(cv.imread(os.path.join(folderModepath , path)))

#print(len(imgModeList))


# step 2:Loading the encode File
print('Loading Encode File')
file = open('EncodeFile.p' , 'rb')  # perssion of reading : rb
encodeListknownwithIds = pickle.load(file)
file.close()
# separting the merged encodelistwithId
[encodeListknown , studentsIds] = encodeListknownwithIds
# print(studentsIds)
print('Encode File Loaded')


#step 7: setting mode for adding onto graphics
modeType = 0
counter = 0
id = -1 , # making sure that id is there
imgStudent = []

while True:
    success, img =cam.read()
    # scaling down the image to reduce the computations
    imgS = cv.resize(img , (0,0) , None , 0.25 , 0.25)
    imgS = cv.cvtColor(imgS , cv.COLOR_BGR2RGB)

    # we need two things i) Faces in the current frame , encodings in the current frame
    # since we dont want the encoding of the whole image, first we will provide the location of the face and then encode the face.
    faceCurFrame = face_recognition.face_locations(imgS)
    # earier we had encodings of new faces and Now we will Cmpare encodings of the old and latest recognized face
    encodeCurFrame = face_recognition.face_encodings(imgS , faceCurFrame)

    #overlaying image on background
    imgBackground[162 : 162+480 , 55:55+640] = img

    # overlaying Modes on background
    imgBackground[44: 44 + 633, 808:808 + 414] = imgModeList[modeType] #passing on the modetType

    ## step 4: Face recognition using encodings
    # Looping through all these encodings and check whether these match with the encodings o fth eknown faces or not
    for encodeFace , faceloc in zip(encodeCurFrame , faceCurFrame):  #without providing zip we have write two different loops
        matches = face_recognition.compare_faces(encodeListknown , encodeFace)
        faceDist = face_recognition.face_distance(encodeListknown,encodeFace)
        # face distance gives about how good the match is, lower the value, the better the match it is.
        # now we have to get the index of the least value i.e correct match
        #print("matches", matches)
        #print("FaceDistance ", faceDist)

        matchIndex = np.argmin(faceDist) #give sth eindex of least value.
        # now if that index is having "True" value we can say that the correct face is detected.

        if matches[matchIndex] :
            print("Known Face detected")
            print("Recognized Id: " , studentsIds[matchIndex])
            #print("matchIndex" , matchIndex)
            # now we will be drawing a rectangle around the face
            #for this we will use cvzone where we can have a fancy stuff
            y1 , x2 ,y2 , x1 = faceloc
            y1, x2, y2, x1 = y1*4 , x2*4 ,y2*4 , x1*4  # since we have reduced the size to 1/4th
            bbox = 55+x1, 162+y1 , x2-x1 , y2-y1
            imgBackground = cvzone.cornerRect( imgBackground , bbox , rt=0) #we can be get values of the bounding box from face locations

            #step 7
            id = studentsIds[matchIndex]

            # here if face is detecetd we need to download the data in very first iteration
            if counter == 0:
                counter = 1
                modeType = 1 #updating the modes

    if counter != 0:

        if counter ==1:  #belongs to first image
            # this is the part where we can download
            studentInfo = db.reference(f"Students/{id}").get()
            print(studentInfo)

            #step 8
            # get the Image from the storage
            blob = bucket.get_blob(f'Images/{id}.png')
            array = np.frombuffer(blob.download_as_string(),np.uint8)
            imgStudent = cv.imdecode(array , cv.COLOR_BGRA2BGR)

            #step 8.2
            #update data of attendfance
            ref = db.reference(f'Students/{id}')
            studentInfo["Total_Attendance"] += 1
            #updating in server
            ref.child("Total_Attendance").set(studentInfo["Total_Attendance"])



        # step 8.1
        #adding text to graphics by knowing the location
        cv.putText(imgBackground , str(studentInfo['Total_Attendance']),(861,125) ,
                   cv.FONT_HERSHEY_COMPLEX , 1 , (255 , 255 ,255) , 1)

        cv.putText(imgBackground, str(studentInfo['Major']), (1006, 550),
                   cv.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
        cv.putText(imgBackground, str(id), (1006, 493),
                   cv.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
        cv.putText(imgBackground, str(studentInfo['standing']), (910, 625),
                   cv.FONT_HERSHEY_COMPLEX, 0.6, (100,100,100), 1)
        cv.putText(imgBackground, str(studentInfo['year']), (1025, 625),
                   cv.FONT_HERSHEY_COMPLEX, 0.6, (100,100,100), 1)
        cv.putText(imgBackground, str(studentInfo['Starting Year']), (1125, 625),
                   cv.FONT_HERSHEY_COMPLEX, 0.6, (100,100,100), 1)

        #centering the Name on Graphics
        (w,h) , _ = cv.getTextSize(studentInfo['name'] , cv.FONT_HERSHEY_COMPLEX , 1, 1)
        offset = (414 - w )//2  # 414 is te width of the mode graphics

        cv.putText(imgBackground, str(studentInfo['name']), (808 + offset, 445),   # here since the name changes a lot we have to center the txt automarticaly
                     cv.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

        imgBackground[175:175+216 , 909:909+216] = imgStudent #adding the image to graphics , 216*216 : size of Image

        counter += 1



    #cv.imshow("webcam" , img)
    cv.imshow("Face Attendance",imgBackground )
    key = cv.waitKey(1)

    if (key == 27):
        cam.release()
        break
