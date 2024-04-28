from threading import Thread
from scipy.spatial import distance
from imutils import face_utils
import imutils
import dlib
import cv2

import serial
import threading
import time
import tkinter as tk
import pygame

from check_gps import retrieve_gps_location
from input_number import UserInputWindow


pygame.init()
pygame.mixer.init()

# Initialize serial port
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
gps_location = retrieve_gps_location()

def reinitiliaze():
    pygame.init()
    pygame.mixer.init()
    
def send_command(command):
    ser.write((command + '\r\n').encode())
    time.sleep(1)
    response = ser.read(ser.inWaiting()).decode()
    return response
    
def play_sound(is_threaded=True, is_new=False):
	file_path_annoying_sound = "/usr/share/sounds/alsa/buzzer.mp3"
	file_path_selos_sound = "/usr/share/sounds/alsa/selos.mp3"
	if is_threaded == True:
		try:
			pygame.mixer.music.load(file_path_selos_sound)
			pygame.mixer.music.play()
			while pygame.mixer.music.get_busy():
				pygame.time.Clock().tick(10)
		except Exception as e:
			print("Error:", e)
		finally:
			pygame.mixer.quit()
			pygame.quit()
   
	elif is_threaded == False:
			try:
				pygame.mixer.music.load(file_path_annoying_sound)
				pygame.mixer.music.play()
				while pygame.mixer.music.get_busy():
					pygame.time.Clock().tick(10)
			except Exception as e:
				print("Error:", e)
			finally:
				pygame.mixer.quit()
				pygame.quit()
	
	else:
		print("NO SOUND HERE")
			
    
def send_sms(number="+639763568298", message="", sound_only=False):
    def send_sms_thread():
        send_command('AT+CMGF=1')  # Set SMS text mode
        send_command('AT+CMGS="{}"'.format(number))  # Set the phone number
        time.sleep(1)
        send_command(message + chr(26))  # Send the message and terminate with Ctrl+Z
        reinitiliaze()
        play_sound(is_threaded=True)
        
        print(number)
        print(message)
        print("SENT...")
        
        
    def send_sound():
        play_sound(is_threaded=False)

    if sound_only:
    # Create and start the thread for sending SMS
        sms_thread = threading.Thread(target=send_sound)
        
    else:
        sms_thread = threading.Thread(target=send_sms_thread)
    sms_thread.start()
    

def eye_aspect_ratio(eye):
	A = distance.euclidean(eye[1], eye[5])
	B = distance.euclidean(eye[2], eye[4])
	C = distance.euclidean(eye[0], eye[3])
	ear = (A + B) / (2.0 * C)
	return ear

user_input_window = UserInputWindow()
full_number = user_input_window.get_user_input()

thresh = 0.25
frame_check = 7
frame_check_mid = 11
frame_check_high = 14
detect = dlib.get_frontal_face_detector()
predict = dlib.shape_predictor("models/shape_predictor_68_face_landmarks.dat")# Dat file is the crux of the code

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]
cap=cv2.VideoCapture(0)
flag=0
count=0
running = True

def close_application():
    global running
    running = False

def process_frame():
    global running, flag, cap
    while running:
        ret, frame=cap.read()
        frame = imutils.resize(frame, width=450)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        subjects = detect(gray, 0)
        for subject in subjects:
            shape = predict(gray, subject)
            shape = face_utils.shape_to_np(shape)#converting to NumPy Array
            leftEye = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]
            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)
            ear = (leftEAR + rightEAR) / 2.0
            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
            if ear < thresh:
                flag += 1
                print (flag)
                if flag >= frame_check_high:
                    cv2.putText(frame, f"HIGHLY DROWSY: THRESHOLD {flag}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.putText(frame, f"ASPECT RATIO: {ear:.5f}", (10,200),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    send_sms(number=full_number, message=f"PERSON HIGHLY DROWSY! SENDING MESSAGE TO EMERGENCY CONTACT LatLong here: {gps_location}")
                elif flag >= frame_check:
                    cv2.putText(frame, f"LIGHTLY DROWSY: THRESHOLD {flag}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.putText(frame, f"ASPECT RATIO: {ear:.5f}", (10,200),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    send_sms(sound_only=True)
                else:
                    cv2.putText(frame, f"THRESHOLD {flag}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.putText(frame, f"ASPECT RATIO: {ear:.5f}", (10,200),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                cv2.putText(frame, f"THRESHOLD {flag}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(frame, f"ASPECT RATIO: {ear:.5f}", (10,200),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                flag = 0
        cv2.imshow("Frame", frame)
    
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
    cv2.destroyAllWindows()
    cap.release()
    
thread = Thread(target=process_frame)
thread.start()

root = tk.Tk()
root.title("Drowsiness Detection Control")

stop_button = tk.Button(root, text="Stop", command=close_application, height=2, width=10)
stop_button.pack(pady=20)  # Add some vertical padding

# Run the Tkinter event loop
root.mainloop()

# When the Tkinter window is closed, stop the OpenCV loop
running = False
thread.join()