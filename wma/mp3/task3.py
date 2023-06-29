import cv2 as cv
import numpy as np

cap = cv.VideoCapture('res/video_3_query.mp4')
img = cv.imread("res/photo_3_train.jpg", cv.IMREAD_GRAYSCALE)  # queryiamge

sift = cv.SIFT_create()

kp_image, desc_image = sift.detectAndCompute(img, None)
# Feature matching
FLANN_INDEX_KDTREE = 1
index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
search_params = dict(checks=50)

# we load the flann algorithm which we are going to use to find the matching features
flann = cv.FlannBasedMatcher(index_params, search_params)

while cap.isOpened():
    ret, frame = cap.read()

    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    grayframe = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)  # trainimage
    kp_grayframe, desc_grayframe = sift.detectAndCompute(grayframe, None)
    matches = flann.knnMatch(desc_image, desc_grayframe, k=2)
    good_points = []

    # compare them with the ones of the query image
    for m, n in matches:
        if m.distance < 0.71 * n.distance:
            good_points.append(m)

    # to get the homography, we need first to obtain the matrix and we do it with the function findHomography

    query_pts = np.float32([kp_image[m.queryIdx].pt for m in good_points]).reshape(-1, 1, 2)
    train_pts = np.float32([kp_grayframe[m.trainIdx].pt for m in good_points]).reshape(-1, 1, 2)
    matrix, mask = cv.findHomography(query_pts, train_pts, cv.RANSAC, 3.0)
    matches_mask = mask.ravel().tolist()

    # Perspective transform
    h, w = img.shape
    pts = np.float32([[0, 0], [0, h-1], [w-1, h-1], [w-1, 0]]).reshape(-1, 1, 2)
    dst = cv.perspectiveTransform(pts, matrix)

    homography = cv.polylines(frame, [np.int32(dst)], True, (0, 0, 255), 3)
    cv.imshow("Homography", homography)

    if cv.waitKey(1) == ord('q'):
        break

cap.release()
cv.destroyAllWindows()
