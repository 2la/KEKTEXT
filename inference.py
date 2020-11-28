import torch
from torchvision import transforms
from PIL import Image, ImageDraw
from model import TextDetector
import numpy as np
import lanms
import math
import cv2

import pyocr


def get_rotate_mat(theta):
    return np.array([[math.cos(theta), -math.sin(theta)],
                     [math.sin(theta), math.cos(theta)]])


def resize_img(img):
    w, h = img.size
    resize_w = w
    resize_h = h
    resize_h = resize_h if resize_h % 32 == 0 else int(resize_h / 32) * 32
    resize_w = resize_w if resize_w % 32 == 0 else int(resize_w / 32) * 32
    img = img.resize((resize_w, resize_h), Image.BILINEAR)
    ratio_h = resize_h / h
    ratio_w = resize_w / w
    return img, ratio_h, ratio_w


def load_pil(img):
    t = transforms.Compose([transforms.ToTensor(),
                            transforms.Normalize(mean=(0.5, 0.5, 0.5),
                                                 std=(0.5, 0.5, 0.5))])
    return t(img).unsqueeze(0)


def is_valid_poly(res, score_shape, scale):
    cnt = 0
    for i in range(res.shape[1]):
        if res[0, i] < 0 or res[0, i] >= score_shape[1] * scale or \
                res[1, i] < 0 or res[1, i] >= score_shape[0] * scale:
            cnt += 1
    return True if cnt <= 1 else False


def restore_polys(valid_pos, valid_geo, score_shape, scale=4):
    polys = []
    index = []
    valid_pos *= scale
    d = valid_geo[:4, :]
    angle = valid_geo[4, :]

    for i in range(valid_pos.shape[0]):
        x = valid_pos[i, 0]
        y = valid_pos[i, 1]
        y_min = y - d[0, i]
        y_max = y + d[1, i]
        x_min = x - d[2, i]
        x_max = x + d[3, i]
        rotate_mat = get_rotate_mat(-angle[i])

        temp_x = np.array([[x_min, x_max, x_max, x_min]]) - x
        temp_y = np.array([[y_min, y_min, y_max, y_max]]) - y
        coordidates = np.concatenate((temp_x, temp_y), axis=0)
        res = np.dot(rotate_mat, coordidates)
        res[0, :] += x
        res[1, :] += y

        if is_valid_poly(res, score_shape, scale):
            index.append(i)
            polys.append([res[0, 0], res[1, 0], res[0, 1], res[1, 1], res[0, 2],
                          res[1, 2], res[0, 3], res[1, 3]])
    return np.array(polys), index


def get_boxes(score, geo, score_thresh=0.9, nms_thresh=0.2):
    score = score[0, :, :]
    xy_text = np.argwhere(score > score_thresh)
    if xy_text.size == 0:
        return None

    xy_text = xy_text[np.argsort(xy_text[:, 0])]
    valid_pos = xy_text[:, ::-1].copy()
    valid_geo = geo[:, xy_text[:, 0], xy_text[:, 1]]
    polys_restored, index = restore_polys(valid_pos, valid_geo, score.shape)
    if polys_restored.size == 0:
        return None

    boxes = np.zeros((polys_restored.shape[0], 9), dtype=np.float32)
    boxes[:, :8] = polys_restored
    boxes[:, 8] = score[xy_text[index, 0], xy_text[index, 1]]
    boxes = lanms.merge_quadrangle_n9(boxes.astype('float32'), nms_thresh)
    return boxes


def adjust_ratio(boxes, ratio_w, ratio_h):
    if boxes is None or boxes.size == 0:
        return None
    boxes[:, [0, 2, 4, 6]] /= ratio_w
    boxes[:, [1, 3, 5, 7]] /= ratio_h
    return np.around(boxes)


def detect(img, model, device):
    img, ratio_h, ratio_w = resize_img(img)
    with torch.no_grad():
        score, geo = model(load_pil(img).to(device))
    boxes = get_boxes(score.squeeze(0).cpu().numpy(),
                      geo.squeeze(0).cpu().numpy())
    return adjust_ratio(boxes, ratio_w, ratio_h)


def plot_boxes(img, boxes):
    if boxes is None:
        return img

    draw = ImageDraw.Draw(img)
    for box in boxes:
        draw.polygon(
            [box[0], box[1], box[2], box[3], box[4], box[5], box[6], box[7]],
            outline=(0, 255, 0))
    return img


if __name__ == '__main__':
    img_path = 'images/tekst1_stranica_2_s.jpg'

    T = pyocr.get_available_tools()[0]
    L = T.get_available_languages()[0]
    txt = T.image_to_string(
        Image.open(img_path),
        lang=L,
        builder=pyocr.builders.TextBuilder()
    )
    print(txt)
    # model_path = 'weights/east_vgg16.pth'
    # pretrained_path = 'weights/vgg16_bn-6c64b313.pth'
    # res_img = './res.bmp'
    # device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    # model = TextDetector(True, pretrained_path).to(device)
    # model.load_state_dict(torch.load(model_path))
    # model.eval()
    # img = Image.open(img_path).convert('RGB')
    # print(ptst.image_to_string(img, lang='en'))
    # to_draw = cv2.imread(img_path)
    # boxes = detect(img, model, device)
    # for box in boxes:
    #     xmin = int(min(box[i] for i in range(0, 8, 2)))
    #     ymin = int(min(box[i] for i in range(1, 8, 2)))
    #     xmax = int(max(box[i] for i in range(0, 8, 2)))
    #     ymax = int(max(box[i] for i in range(1, 8, 2)))
    #     text = to_draw[ymin: ymax, xmin: xmax, :]
    #     pil_text_image = Image.fromarray(text.astype('uint8'), 'RGB')
    #     print(ptst.image_to_string(img, lang='ru'))
    #     cv2.rectangle(to_draw, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
    #     cv2.imshow('Image', text)
    #     cv2.waitKey()
    # plot_img = plot_boxes(img, boxes)
    # plot_img.save(res_img)
