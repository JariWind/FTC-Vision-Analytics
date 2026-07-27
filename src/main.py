import cv2

# Locatie van je testvideo
video_path = "videos/solo_test.mp4"

# Open de video
cap = cv2.VideoCapture(video_path)

# Controleer of de video geopend is
if not cap.isOpened():
    print("Fout: kan video niet openen.")
    exit()

print("Video gestart. Druk op 'q' om te stoppen.")

while True:
    # Lees een frame
    ret, frame = cap.read()

    # Als er geen frame meer is: stop
    if not ret:
        print("Einde van de video.")
        break

    # Laat het frame zien
    cv2.imshow("FTC Vision Analytics", frame)

    # Wacht 25 milliseconden en kijk of q wordt ingedrukt
    key = cv2.waitKey(25) & 0xFF

    if key == ord("q"):
        break

# Ruim alles netjes op
cap.release()
cv2.destroyAllWindows()

print("Programma afgesloten.")