import cv2
camera = cv2.VideoCapture("video_pot2.mp4")
while True:
    ret,image=camera.read()



    if ret == True:
       # image = cv2.imread('4.jpg')
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        canny = cv2.Canny(gray, 0, 255, 0)

        # Find contours
        cnts = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]

        # Iterate thorugh contours and draw rectangles around contours
        for c in cnts:
            x,y,w,h = cv2.boundingRect(c)
            cv2.rectangle(image, (x, y), (x + w, y + h), (36,255,12), 2)

        cv2.imshow('canny', canny)
        cv2.imshow('image', image)

        keypress = cv2.waitKey(1) & 0xFF

        if (keypress == ord("q")):
            break

camera.release()

cv2.destroyAllWindows()