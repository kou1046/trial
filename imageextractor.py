from __future__ import annotations
import os
from typing import Callable
import cv2
import tkinter as tk
import matplotlib.pyplot as plt
import matplotlib.axes as mpl_axes
from matplotlib.image import AxesImage
import numpy as np

from mycommon import mywidget

class ImageExtractor(tk.Tk):
    def __init__(self, image:np.ndarray, **kw):
        super().__init__(**kw)
        self.origin_img:np.ndarray = image
        height, width, _ = image.shape
        self.viewer:mywidget.ImageCanvas = mywidget.ImageCanvas(self, width=width, height=height)
        self.viewer.update_img(image)
        self.viewer.bind('<1>', lambda e:self._send_two_cor(e, self._extract_img))
        self.viewer.pack()
        self.result:np.ndarray|None = None
    def _send_two_cor(self, e:tk.Event, send_func:Callable[[tuple[int, int]], None],
                      *, __clicked_cor:list[None|int]=[None]):
        if __clicked_cor[0] is None:
            __clicked_cor[0] = (e.x, e.y)
        else:
            second_clicked_cor = (e.x, e.y)
            if __clicked_cor[0] == second_clicked_cor: return
            send_func(__clicked_cor[0], second_clicked_cor)
            __clicked_cor[0] = None
    def _extract_img(self, cor_1:tuple[int, int], cor_2:tuple[int, int]):
        xmin, ymin = cor_1; xmax, ymax = cor_2
        if xmin > xmax: xmin, xmax = xmax, xmin
        if ymin > ymax: ymin, ymax = ymax, ymin
        img_copy = self.origin_img.copy()
        visualized_img = cv2.rectangle(img_copy, cor_1, cor_2, (0, 0, 0), 3)
        self.viewer.update_img(visualized_img)
        extracted_img = self.origin_img[ymin:ymax, xmin:xmax]
        if self.result is None:
            tk.Button(self, text='完了', command=self.destroy).pack()
        self.result = extracted_img

def shift_extracted_img(img:np.ndarray, extracted_img:np.ndarray, ax:mpl_axes.Axes, row_step:int=1, col_step:int=1) -> list[AxesImage]:
    height, width, _ = img.shape
    fg_height, fg_width, _ = extracted_img.shape
    return_values:list[AxesImage] = []
    for i in range((width-fg_width)//row_step): #横
        row_progress = i*row_step
        for j in range((height-fg_height)//col_step):
            col_progress = j*col_step
            bg_img = img.copy()
            bg_img[col_progress:col_progress+fg_height, row_progress:row_progress+fg_width] = extracted_img
            cv2.imshow('img', bg_img)
            cv2.waitKey(1)
    
file_path = os.path.join(__file__, '..', 'dropkick.jpg')
img = cv2.imread(file_path)
extractor = ImageExtractor(img); extractor.mainloop()
extracted_img = extractor.result

h, w, _ = extracted_img.shape

result = cv2.matchTemplate(img, extracted_img, method=cv2.TM_CCORR_NORMED)
plt.imshow(result)
plt.show()
