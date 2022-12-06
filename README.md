
# COCO-format segmentation visualization

Repo contains scripts for visualizing segmentation datasets in COCO-format.
Based on custom COCO-dataset [tutorial](https://www.immersivelimit.com/tutorials/create-coco-annotations-from-scratch/#preview-coco-annotations)
## Installation

```
   conda create --name segmentation_visualization python=3.7
   conda activate segmentation_visualization
   pip install --upgrade Pillow
   pip install html2image
   git clone https://github.com/korney3/segmentation_visualization_coco_format
```


## Code

Пример использования находится в [main](main.py)


Объект класса [CocoDataset](coco_dataset.py) принимает на вход пути до файла с аннотациями и папке исходных изображений.
```
    Arguments:
        annotation_path (str): path to file with annotations
        image_dir (str): path to directory with images to annotate
```

Объект класса [Visualizer](visualizer.py) принимает на COCO-dataset, путь к папке, где будут лежать картинки с
аннотациями, и минимальный и максимальный размер шрифта, которым будут подписываются объекты в зависимости от размера
полигона

```
    Arguments:
        coco_dataset (CocoDataset): object of CocoDataset with loaded list of image and annotations info
        results_dir (str): directory to store annotated image
        max_font_size (int): size of label of largest object
        min_font_size (int): size of label of smallest object
```
