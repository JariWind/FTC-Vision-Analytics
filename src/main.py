import cv2
import time
import numpy as np

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

homography = None
points = []
click_point = None

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

field = cv2.imread("assets/field.png")

if field is None:
    print("Kan field.png niet laden.")
    exit()

FIELD_SIZE_CM = 366
field_height, field_width = field.shape[:2]
SCALE = field_width / FIELD_SIZE_CM

field_points = np.array([
    [183 * SCALE,   0 * SCALE],
    [0 * SCALE,   183 * SCALE],
    [0 * SCALE,   366 * SCALE],
    [366 * SCALE, 366 * SCALE],
    [366 * SCALE, 183 * SCALE],
    [183 * SCALE, 183 * SCALE]
], dtype=np.float32)

if field is None:
    print("Kan field.png niet laden.")
    exit()

def mouse_callback(event, x, y, flags, param):

    global points
    global click_point

    if event == cv2.EVENT_LBUTTONDOWN:

        if len(points) < NUM_POINTS:

            points.append((x, y))

            index = len(points) - 1

            print(f"{POINT_NAMES[index]}: ({x}, {y})")

        else:

            click_point = (x, y)

            print(f"Test klik: ({x}, {y})")

        if len(points) == NUM_POINTS:
            print("Alle punten geselecteerd.")

cv2.namedWindow("FTC Vision Analytics", cv2.WINDOW_AUTOSIZE)
cv2.namedWindow("Field View", cv2.WINDOW_NORMAL)

cv2.resizeWindow("Field View", 500, 500)

cv2.setMouseCallback("FTC Vision Analytics", mouse_callback)

if frame is None:
    print("Kan eerste frame niet laden.")
    exit()


while True:

    display = frame.copy()
    field_display = field.copy()

    if len(points) == NUM_POINTS and homography is None:

        image_points = np.array(points, dtype=np.float32)

        homography, status = cv2.findHomography(
            image_points,
            field_points
        )

        print("Homography:")
        print(homography)

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

    if homography is not None and click_point is not None:

        camera_point = np.array(
            [[[click_point[0], click_point[1]]]],
            dtype=np.float32
        )

        field_point = cv2.perspectiveTransform(
            camera_point,
            homography
        )

        x = int(field_point[0][0][0])
        y = int(field_point[0][0][1])

        cv2.circle(
            field_display,
            (x, y),
            25,
            (255, 0, 0),
            -1
        )

    if homography is not None:

        for point in points:

            camera_point = np.array([[[point[0], point[1]]]], dtype=np.float32)

            field_point = cv2.perspectiveTransform(
                camera_point,
                homography
            )

            x = int(field_point[0][0][0])
            y = int(field_point[0][0][1])

            cv2.circle(
                field_display,
                (x, y),
                15,
                (0, 0, 255),
                -1
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

    field_view = cv2.resize(
        field_display,
        (600, 600)
    )

    cv2.imshow("Field View", field_view)

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
        homography = None

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