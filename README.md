
# COCO-format segmentation visualization

![](images/test.jpg)

Repo contains scripts to split image into pieces with predefined size and merge obtained pieces into initial image.

## Installation

```
   conda create --name sliding_window python=3.8
   conda activate sliding_window
   pip install opencv_contrib_python
   git clone https://github.com/korney3/image_sliding_window_cutter
```


## Code


### Download dataset

[COCO validation set](https://cocodataset.org/#download)

Пример использования находится в [main](main.py)


Скрипт [split](split.py) принимает на вход картинку,
    размер (h, w) окна в пикселях или процентах,
    смещение по x и y, и нарезает
    изображения sliding window подходом.
```
    Arguments:
        image_path (str): path to image to split
        window_size (Tuple[int, int] or Tuple[float, float]): width 
                                    and height of sliding window 
                                    in pixels of percent
        use_percent (bool) = False: if window size is given is percent
        x_shift (int) = 0: shift of start of cutting x-coordinate
        y_shift (int) = 0: shift of start of cutting y-coordinate
        result_dir (str) = "./split_image": directory to store image's pieces
    Returns:
        Path to cut image
```
Скрипт [merge](merge.py) принимает на вход папку
    с нарезанными картинками и из них собирает
    оригинальную.
```
    Arguments:
        image_dir (str): path to directory with splitted images
    Returns:
        Numpy array with merged image
```
