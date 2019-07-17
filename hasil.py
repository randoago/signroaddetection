import cv2
import time
import numpy as np
import pytesseract
import pyttsx
import Image

##################
DELAY = 0.025
dapat = 0
currentFrame=0
##################
width  = 480.0
height = 336.0
margin = 0.0
##################


corners = np.array(
	[
		[[  		margin, margin 			]],
		[[ 			margin, height + margin  ]],
		[[ width + margin, height + margin  ]],
		[[ width + margin, margin 			]]
	]
)

#create an array for each direction, where array[0] indicates one of the lines and array[1] indicates the other, which if both > 0 will tell us the orientation
#print lines
left = [0, 0]
right = [0, 0]
up = [0, 0]
down = [0, 0]

##################
pts_dst = np.array( corners, np.float32 )
video = cv2.VideoCapture(0)
size = (480,336)
arah = ""


while True :
    ret, cap = video.read()
    start_time = time.time()
    #cap = cv2.imread("asli8204.jpg")
    ukuranbaru = cv2.resize(cap, size, interpolation = cv2.INTER_AREA)

    ubah = cv2.cvtColor( ukuranbaru, cv2.COLOR_BGR2HSV)

    #range warna hijau
    lower_green = np.array([30,50,50])
    upper_green = np.array([102,255,255])

    #masking warna hijau
    mask = cv2.inRange(ubah, lower_green, upper_green)
    res = cv2.bitwise_and(ukuranbaru,ukuranbaru, mask= mask)
    #cv2.imshow('oooo',res)

    gray = cv2.cvtColor( res, cv2.COLOR_BGR2GRAY)

    gray = cv2.bilateralFilter( gray, 1, 10, 120 )
    gray = cv2.medianBlur(gray, 3)

    edges  = cv2.Canny( gray, 100, 255 )


    kernel = cv2.getStructuringElement( cv2.MORPH_RECT, ( 7, 7 ) )

    closed = cv2.morphologyEx( edges, cv2.MORPH_CLOSE, kernel )


    contours, h = cv2.findContours( closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )




    for cont in contours:

        if cv2.contourArea( cont ) > 1000 :

            arc_len = cv2.arcLength( cont, True )

            approx = cv2.approxPolyDP( cont, 0.1 * arc_len, True )

            if ( len( approx ) == 4 ):
                dapat = 1
                pts_src = np.array( approx, np.float32 )

                h, status = cv2.findHomography( pts_src, pts_dst )
                out = cv2.warpPerspective( ukuranbaru, h, ( int( width + margin * 2 ), int( height + margin * 2 ) ) )


                cv2.drawContours( ukuranbaru, [approx], -1, ( 255, 0, 0 ), 2 )

            else : pass


    cv2.imshow( 'cap', ukuranbaru)

    if dapat :

        cv2.imshow( 'out', out )
        cv2.imwrite('asli' + str(currentFrame) + '.jpg',ukuranbaru)
        gmbr= cv2.resize(out, size, interpolation = cv2.INTER_AREA)
        gmbr= cv2.cvtColor(gmbr, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gmbr,(5,5),0)


        # find otsu's threshold value with OpenCV function
        ret, otsu = cv2.threshold(blur,80,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)


        kata = pytesseract.image_to_string(otsu)
        if kata == "" :
            print "Tidak ada rambu penunjuk arah"

        else :
            edges = cv2.Canny(otsu,40,200,apertureSize = 3)

            lines = cv2.HoughLines(edges,1,np.pi/180,20)

            for object in lines:
                theta = object[0][1]
                rho = object[0][0]
                print rho
                print theta
                garis = np.round(theta,2)
                #print object
                #cases for right/left arrows
                if (garis < 1.0):
                    up[1] +=1


                elif (garis >= 1.0):
                    if (rho <=  30):
                        right[1] +=1

                    elif (rho >= 110):
                        left[0] += 1
                    elif (rho <= 100):
                        left[1] +=1
                    elif (rho <= -57):
                        right[0] +=1


            if left[0] >= 1 or left[1] >= 1:
                arah = "belok kiri"

            elif right[0] >= 1 or right[1] >= 1:
                arah = "belok kanan"

            elif up[1] >= 1:
                arah = "Jalan terus"

            print kata
            print"posisi" + arah
            kata = pytesseract.image_to_string(otsu)
            engine = pyttsx.init()
            engine.say(kata)
            engine.say(arah)
            print " 'suara yang dikeluarkan"+kata+" "+arah +" -"
            print("--- %s waktu eksekusi ---" % (time.time() - start_time))

            engine.runAndWait()
        time.sleep( DELAY )

        dapat=0
        cv2.imwrite('out' + str(currentFrame) + '.jpg',out)

        #cv2.imwrite('asli' + str(currentFrame) + '.jpg',ukuranbaru)
        cv2.imshow('th', otsu)
        cv2.imwrite('th' + str(currentFrame) + '.jpg',otsu)
        currentFrame += 1

    if cv2.waitKey(27) & 0xFF == ord('q') :
            break

engine.runAndWait()
video_capture.release()
cv2.destroyAllWindows()
