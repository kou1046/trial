from __future__ import annotations
import os
import sys
from typing import Callable, Generator
import cv2
import tkinter as tk
import matplotlib.pyplot as plt
import matplotlib.axes as mpl_axes
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable, get_cmap
import matplotlib.figure as mpl_fig
from matplotlib.animation import FuncAnimation
import numpy as np

sys.path.append(os.path.join(__file__, '..', '..'))

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

def animateMatchTemplate(img:np.ndarray, extracted_img:np.ndarray, row_step:int=1, col_step:int=1,
                         cmap='jet', method:int=cv2.TM_CCOEFF_NORMED) -> FuncAnimation:
    
    FrameType = tuple[int, int, np.ndarray, np.ndarray]
    def update(frame:FrameType) -> None:
        for ax in axes[1:]: ax.cla()
        i, j, match, img  = frame
        fig.suptitle(f'i={i}, j={j}')
        axes[1].imshow(img)
        axes[2].imshow(match, extent=[0, result_w, 0, result_h], vmin=min_value, vmax=max_value, cmap=cmap)
        
    def send_frames() -> Generator[tuple[int, int, np.ndarray], None, None]:
        for i in range((height-fg_height)//col_step):
            col_progress = i*col_step
            for j in range((width-fg_width)//row_step): #横
                row_progress = j*row_step
                bg_img = img.copy()
                bg_img[col_progress:col_progress+fg_height, row_progress:row_progress+fg_width] = extracted_img
                result_anim[:col_progress+1, :row_progress+1] = result[:col_progress+1, :row_progress+1]
                yield col_progress, row_progress, result_anim, bg_img

    fig, axes = plt.subplots(3, 1)
    cmap = get_cmap(cmap)
    height, width, _ = img.shape
    fg_height, fg_width, _ = extracted_img.shape
    result = cv2.matchTemplate(img, extracted_img, method=method) #結果は先に計算
    result_h, result_w = result.shape
    min_value, max_value, _, max_idx = cv2.minMaxLoc(result)
    result_anim = np.zeros((result.shape))
    left_top_x, left_top_y = max_idx
    axes[0].imshow(cv2.rectangle(img.copy(), (left_top_x, left_top_y), (left_top_x+fg_width, left_top_y+fg_height), (0, 0, 255), 3))
    axes[0].set(xticks=[], yticks=[])
    axes[2].set(xlim=[0, result_w], ylim=[0, result_h])
    anim = FuncAnimation(fig, update, send_frames, interval=1)
    fig.colorbar(ScalarMappable(cmap=cmap, norm=Normalize(vmin=min_value, vmax=max_value)), orientation='horizontal')
    return anim
            
if __name__ == '__main__':
    file_path = os.path.join(__file__, '..', 'dropkick.jpg')
    img = cv2.imread(file_path)
    extractor = ImageExtractor(img); extractor.mainloop()
    extracted_img = extractor.result
    anim = animateMatchTemplate(img, extracted_img, row_step=15, col_step=15)
    plt.show()




