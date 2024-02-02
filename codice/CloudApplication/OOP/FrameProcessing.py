import sys
import traceback, imutils, cv2, json
import numpy as np
from PIL import Image
from collections import deque
from pyzbar.pyzbar import decode


class FrameProcessing:

    def __init__(self, frames_dict: dict, temp_file_dir="static/temp_img/", direction=True, **kwargs):
        """
        :param frames_dict: dict of frames {frame_name: FILE_CONTENT}
        :param temp_file_dir: dir to use in order to store images
        :param direction: True (from left to right) increase otherwise decrease qty. False is the opposite
        """
        self.frames_dict = frames_dict
        self.frame_list = [self.frames_dict[key] for key in self.frames_dict]
        self.metadata_dict = kwargs
        self.temp_file_dir = temp_file_dir
        self.direction = direction
        self.msg = {}

        if direction:
            self.msg["SxDx"] = {"msg": "Qty. increased correctly", "qty": +1}
            self.msg["DxSx"] = {"msg": "Qty. decreased correctly", "qty": -1}
        else:
            self.msg["SxDx"] = {"msg": "Qty. decreased correctly", "qty": -1}
            self.msg["DxSx"] = {"msg": "Qty. increased correctly", "qty": +1}

    def detect_qr_code(self):
        """
        This method, for each frame, add content key inside dict with decoded product value and grey mask for direction
        detection.
        Call this method before detect_direction.
        A new frame list is created with frames with-in qrcode.
        """
        frame_list_updated = []
        for cont, frame in enumerate(self.frame_list):
            frame = Image.open(frame)
            frame = np.array(frame)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            barcodes = decode(gray)
            cv2.imwrite(f"static/temp_img/grey_{cont}.png", gray)
            cv2.imwrite(f"static/temp_img/frame_{cont}.png", frame)

            for barcode in barcodes:
                # extract the bounding box location of the barcode and draw the
                # bounding box surrounding the barcode on the image
                (x, y, w, h) = barcode.rect
                cv2.rectangle(frame, (x, y), (x + int(w / 2), y + int(h / 2)), (0, 128, 0), -1)
                barcodeData = barcode.data.decode("utf-8")
                frame_list_updated.append({"frame": frame, "content": json.loads(barcodeData)})

        self.frame_list.clear()
        self.frame_list = frame_list_updated.copy()

    def get_qr_info(self):
        """
        Returns qrcode related information for detected item
        """
        for item in self.frame_list:
            if isinstance(item, dict):
                return item.get("content").get("arcodart"), item.get("content").get("ardesart")

        raise Exception("Frame list doesn't have any QrCode to read infos from")

    def detect_direction(self, min_radius=5):
        """
        Given a set of frame and a set of related metadata we want to get the direction considering pic indexes.
        Evaluate the direction of the red colored item considering frames behaviour.


        :returns: True,  {"msg": "Qty. decreased correctly"/"Qty. increased correctly", "qty": -1/+1} / False, str(error)
        """
        try:
            """
            SX -> DX: Then Dx in < 0
            DX -> SX :Then Sx is > 0
            """
            max_len = len(self.frame_list)
            greenLower = (35, 115, 0)
            greenUpper = (64, 255, 255)
            pts = deque(maxlen=max_len)  # max number of previous frame analyzed in order to detect x,y evolution

            for cont, frame in enumerate(self.frame_list):
                # frame = frame_dict["frame"]
                # content_json = frame_dict["content"]
                frame = Image.open(frame)
                frame = np.array(frame)
                frame = imutils.resize(frame, width=600)
                blurred = cv2.GaussianBlur(frame, (11, 11), 0)
                mask = cv2.inRange(blurred, greenLower, greenUpper)
                cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cnts = imutils.grab_contours(cnts)
                cv2.drawContours(frame, cnts, -1, (0, 255, 0), 2)
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
                        # then update the list of tracked points
                        pts.appendleft(center)

            # FIRST-POINT INDEX
            first_index = 0
            # LAST-POINT INDEX
            last_index = len(pts) - 1
            # detect delta measure
            dX = pts[first_index][0] - pts[last_index][0]
            dY = pts[first_index][1] - pts[last_index][1]

            if dX < 0:
                direction = "SxDx"
            else:
                direction = "DxSx"

            return True, self.msg[direction]
        except Exception:
            return False, traceback.format_exc()
