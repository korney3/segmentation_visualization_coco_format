from coco_dataset import CocoDataset
from visualizer import Visualizer


def main():
    coco_dataset = CocoDataset("./dataset/annotations/instances_val2017.json", "./dataset/val2017")
    visualizer = Visualizer(coco_dataset, "./visualization", 24, 12)
    visualizer.get_visualization("random")

if __name__ == "__main__":
    main()