import numpy as np
import cv2
import time

inputvid = '/Users/stuartbman/Google Drive/us_emg_shared/recordings- 2021.05.13/- - Recording 13.05.21 active - 2021-05-13 14-24-20.mp4'

cap = cv2.VideoCapture(inputvid)

old_frame = None

start_t=200
Fs = cap.get(cv2.CAP_PROP_FPS)
cap.set(cv2.CAP_PROP_POS_FRAMES, int(Fs * start_t))

# kernel = np.ones((2,2),np.uint8)
# gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
# gray = gray[100:, 100:]
# gray = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)


# params for ShiTomasi corner detection
feature_params = dict(maxCorners=200,
                      qualityLevel=0.1,
                      minDistance=10,
                      blockSize=5)

# Parameters for lucas kanade optical flow
lk_params = dict(winSize=(15, 15),
                 maxLevel=2,
                 criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 1000, 0.03))

# Create some random colors
color = np.random.randint(0, 255, (200, 3))

# Take first frame and find corners in it
ret, old_frame = cap.read()
old_frame = old_frame[100:-100, 130:-200]
old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
p0 = cv2.goodFeaturesToTrack(old_gray, mask=None, **feature_params)


# Create a mask image for drawing purposes
mask = np.zeros_like(old_frame)


while (1):
    ret, frame = cap.read()
    try:
        frame = frame[100:-100, 130:-200]
    except:
        break
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # calculate optical flow
    p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)

    # Select good points
    good_new = p1[st == 1]
    good_old = p0[st == 1]

    # draw the tracks
    for i, (new, old) in enumerate(zip(good_new, good_old)):
        a, b = new.ravel()
        c, d = old.ravel()
        mask = cv2.line(mask, (a, b), (c, d), color[i].tolist(), 2)
        frame = cv2.circle(frame, (a, b), 5, color[i].tolist(), -1)
    img = cv2.add(frame, mask)

    cv2.imshow('frame', img)
    k = cv2.waitKey(3) & 0xff
    if k == 27:
        break

    # Now update the previous frame and previous points
    old_gray = frame_gray.copy()
    p0 = good_new.reshape(-1, 1, 2)

cv2.destroyAllWindows()
cap.release()
