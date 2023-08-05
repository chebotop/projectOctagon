import cv2
import numpy as np
import os
import glob

'''Меняем размер изображения, сохраняя пропорции'''
def resize_image(image, width=None, height=None, inter=cv2.INTER_AREA):
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image

    if width is not None and height is None:
        r = width / float(w)
        dim = (width, int(h * r))
        resized = cv2.resize(image, dim, interpolation=inter)
        return resized

    if height is not None and width is None:
        r = height / float(h)
        dim = (int(w * r), height)
        resized = cv2.resize(image, dim, interpolation=inter)
        return resized

    r = height / float(h)
    dim = (int(w * r), height)
    resized = cv2.resize(image, dim, interpolation=inter)

    if resized.shape[1] < width:
        padding = width - resized.shape[1]
        left_padding = padding // 2
        right_padding = padding - left_padding
        white_left = np.full((resized.shape[0], left_padding, 3), 255, dtype="uint8")
        white_right = np.full((resized.shape[0], right_padding, 3), 255, dtype="uint8")
        resized = cv2.hconcat([white_left, resized, white_right])

    return resized



def resize_all_images_in_folder(folder=os.getcwd(), width=640, height=360, inter=cv2.INTER_AREA):
    for filename in glob.glob(os.path.join(folder, '*.jpg')):
        img = cv2.imread(filename)
        if img is not None:
            img = resize_image(img, width, height, inter)
            cv2.imwrite(filename, img)


resize_all_images_in_folder(folder=os.getcwd(), width=640, height=360, inter=cv2.INTER_AREA)
