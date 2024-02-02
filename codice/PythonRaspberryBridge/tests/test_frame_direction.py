from collections import deque
import imutils
import cv2
import numpy as np


def find_direction_from_frame(frame_list, max_len=10, min_radius=5):
    """
    SX -> DX: Then Dx in < 0
    DX -> SX :Then Sx is > 0
    """
    greenLower = (35, 115, 0)
    greenUpper = (64, 255, 255)
    pts = deque(maxlen=max_len) # max number of previous frame analyzed in order to detect x,y evolution
    counter = 0
    (dX, dY) = (0, 0)

    for cont, frame in enumerate(frame_list):
        frame = imutils.resize(frame, width=600)
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        # hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        # construct a mask for the color "red", then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        mask = cv2.inRange(blurred, greenLower, greenUpper)
        # mask = cv2.erode(mask, None, iterations=2)
        # mask = cv2.dilate(mask, None, iterations=2)
        # cv2.imwrite(f"frame_testing/mask_direction_{cont}.png", mask)

        # find contours in the mask and initialize the current
        # (x, y) center of the qr-code
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        cv2.drawContours(frame, cnts, -1, (0, 255, 0), 2)
        cv2.imwrite(f"frame_testing/conts_{cont}.png", frame)
        center = None
        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            # only proceed if the radius meets a minimum size
            if radius > min_radius:
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                pts.appendleft(center)

    # FIRST-POINT INDEX
    first_index = 0
    # LAST-POINT INDEX
    last_index = len(pts)-1
    # detect delta measure
    dX = pts[first_index][0] - pts[last_index][0]
    dY = pts[first_index][1] - pts[last_index][1]

    if dX < 0: print("Da Sx a Dx")
    else: print("Da Dx a Sx")
    # loop over the set of tracked points
    # print(len(pts))
    # for i in np.arange(0, len(pts)):
        # if either of the tracked points are None, ignore
        # them
        # print(pts[i-1], pts[i])
        # if pts[i - 1] is None or pts[i] is None:
        #     continue
        # check to see if enough points have been accumulated in
        # the buffer
        # direction = None
        # print(counter, i, len(pts))
        # if counter >= 9 and i == 1 and pts[-9] is not None:
        # compute the difference between the x and y
        # coordinates and re-initialize the direction
        # text variables
        # dX = pts[i][0] - pts[i-1][0]
        # dY = pts[i][1] - pts[i-1][1]
        # dirX, dirY = "", ""
        # ensure there is significant movement in the
        # x-direction
        # if np.abs(dX) > 10:
        #    dirX = "East" if np.sign(dX) == 1 else "West"
        # ensure there is significant movement in the
        # y-direction
        # if np.abs(dY) > 10:
            # dirY = "North" if np.sign(dY) == 1 else "South"
        # handle when both directions are non-empty
        # if dirX != "" and dirY != "":
            # direction = "{}-{}".format(dirY, dirX)
        # otherwise, only one direction is non-empty
        # else:
            # direction = dirX if dirX != "" else dirY

        # print(direction if direction is not None else f"Dir. X:{dirX}-Dir. Y:{dirY}")
        # counter += 1


