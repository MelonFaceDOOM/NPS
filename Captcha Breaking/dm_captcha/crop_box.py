import cv2
import numpy as np

def crop_box(img_dir, debugging=False):

    KERNEL_LENGTH_DIVISOR = 15 # original value 20
    VERTICAL_EROSION_ITERATIONS = 3 # original value 3
    HORIZONTAL_EROSION_ITERATIONS = 3 # original value 3
    WEIGHTING_ALPHA = 0.5 # original value 0.5
    EXTRA_TOP_PIXELS = 2 # original value 2
    EXTRA_BOTTOM_PIXELS = 2 # original value 2
    EXTRA_LEFT_PIXELS = 2 # original value 2
    EXTRA_RIGHT_PIXELS = 2 # original value 2

    img_original = cv2.imread(img_dir, -1) # Original image to be cropped in final step
    img = cv2.imread(img_dir, 0) # Greyscale working image for manipulation
     
    # Thresholding the image.
    # This rounds all pixels up/down to black/white.
    (thresh, img_bin) = cv2.threshold(img, 128, 255,cv2.THRESH_BINARY_INV)

    # Defining a kernel length
    # too low of a kernel length will make the pixels that form lettes look like lines.
    # too high would disregard the box itself
    kernel_length = np.array(img).shape[1]//KERNEL_LENGTH_DIVISOR
     
    # A vertical kernel of (1 X kernel_length), which will detect all the vertical lines from the image.
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_length))
    # A horizontal kernel of (kernel_length X 1), which will help to detect all the horizontal line from the image.
    hori_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_length, 1))
    # A kernel of (3 X 3) ones.
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

    # Morphological operation to detect vertical lines from an image
    # This process strips away some of the thinner lines. Too many iterations will
    # also strip away the main box lines that we want
    img_temp1 = cv2.erode(img_bin, vertical_kernel,
    iterations=VERTICAL_EROSION_ITERATIONS)
    # This lengthens the lines. More iterations = more lengthening
    vertical_lines_img = cv2.dilate(img_temp1, vertical_kernel, iterations=3)

    # Morphological operation to detect horizontal lines from an image
    img_temp2 = cv2.erode(img_bin, hori_kernel, iterations=3)
    horizontal_lines_img = cv2.dilate(img_temp2, hori_kernel,
    iterations=HORIZONTAL_EROSION_ITERATIONS)

    # Weighting parameters, this will decide the quantity of an image to be added to make a new image.
    alpha = WEIGHTING_ALPHA
    beta = 1.0 - alpha
    # This function helps to add two image with specific weight parameter to get a third image as summation of two image.
    img_final_bin = cv2.addWeighted(vertical_lines_img, alpha, horizontal_lines_img, beta, 0.0)
    img_final_bin = cv2.erode(~img_final_bin, kernel, iterations=2)
    (thresh, img_final_bin) = cv2.threshold(img_final_bin, 128,255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    
    if debugging:
        cv2.imwrite("img_bin.jpg",img_bin)
        cv2.imwrite("vertical_lines.jpg",vertical_lines_img)
        cv2.imwrite("horizontal_lines.jpg",horizontal_lines_img)
        cv2.imwrite("img_final_bin.jpg",img_final_bin)
    
    # Find contours for image, which will detect all the boxes
    contours, hierarchy = cv2.findContours(img_final_bin, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    idx = 0
    img_w = img.shape[1]
    for c in contours:
        # Returns the location and width,height for every contour
        x, y, w, h = cv2.boundingRect(c)
        # w < img_w ensures that the whole image isn't returned
        if (w > 30 and h > 20 and w < img_w):
            idx += 1
            # the +2 and -2 prevent some clipping near the edge of the box
            new_img = img_original[y-EXTRA_TOP_PIXELS:y+h+EXTRA_BOTTOM_PIXELS,
                          x-EXTRA_LEFT_PIXELS:x+w+EXTRA_RIGHT_PIXELS]

    if idx == 1:
        return new_img
    elif idx > 1:
        raise ValueError("Error, multiple interior bounding boxes detected within captcha")
    elif idx == 0:
        raise ValueError("Error, no interior bounding box detected within captcha")