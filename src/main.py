import cv2
import time

video_path = "videos/solo_test.mp4"

cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Fout: kan video niet openen.")
    exit()

total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

fps = 30

fps = cap.get(cv2.CAP_PROP_FPS)

if fps <= 0:
    fps = 30

print(f"Aantal frames: {total_frames}")
print(f"Gebruikte FPS: {fps}")
print(f"Geschatte lengte: {total_frames / fps:.2f} seconden")


frame_number = 0
paused = False

frame_time = 1 / fps
last_frame_time = time.perf_counter()
NUM_POINTS = 6

POINT_NAMES = [
    "Top Mid",
    "Left Mid",
    "Bottom Left",
    "Bottom Right",
    "Right Mid",
    "Center"
]
points = []
def load_frame(number):
    """
    Laadt een specifiek frame.
    Gebruikt voor A/D navigatie.
    """
    cap.set(cv2.CAP_PROP_POS_FRAMES, number)
    ret, frame = cap.read()

    if ret:
        return frame

    return None

frame = load_frame(frame_number)

def mouse_callback(event, x, y, flags, param):

    global points

    if event == cv2.EVENT_LBUTTONDOWN:

        if len(points) < NUM_POINTS:

            points.append((x, y))

            index = len(points) - 1

            print(f"{POINT_NAMES[index]}: ({x}, {y})")

cv2.namedWindow("FTC Vision Analytics")
cv2.setMouseCallback("FTC Vision Analytics", mouse_callback)

if frame is None:
    print("Kan eerste frame niet laden.")
    exit()


while True:

    display = frame.copy()

    for i, point in enumerate(points):

        cv2.circle(
            display,
            point,
            3,
            (0, 0, 255),
            -1
        )

        # Standaard: rechts boven het punt
        text_x = point[0] + 8
        text_y = point[1] - 8

        if POINT_NAMES[i] == "Bottom Right":
            text_x = point[0] - 100

        if POINT_NAMES[i] == "Right Mid":
            text_x = point[0] - 70

        cv2.putText(
            display,
            POINT_NAMES[i],
            (text_x, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 255),
            1
        )

    cv2.putText(
        display,
        f"Frame: {frame_number}/{total_frames}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.putText(
        display,
        f"FPS: {fps}",
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.imshow("FTC Vision Analytics", display)

    key = cv2.waitKey(1)


    if key == ord("q"):
        break


    elif key == ord(" "):
        paused = not paused
        last_frame_time = time.perf_counter()


    elif key == ord("d"):

        if frame_number < total_frames - 1:
            frame_number += 1
            frame = load_frame(frame_number)


    elif key == ord("a"):

        if frame_number > 0:
            frame_number -= 1
            frame = load_frame(frame_number)

    elif key == ord("r"):

        points.clear()

        print("Punten gewist.")

    if not paused:

        current_time = time.perf_counter()

        if current_time - last_frame_time >= frame_time:

            ret, frame = cap.read()

            if ret:
                frame_number += 1
                last_frame_time = current_time

            else:
                paused = True


cap.release()
cv2.destroyAllWindows()

print("Programma afgesloten.")