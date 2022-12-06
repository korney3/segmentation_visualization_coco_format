from coco_dataset import CocoDataset
from visualizer import Visualizer


def main():
    coco_dataset = CocoDataset(annotation_path="./dataset/annotations/instances_val2017.json",
                               image_dir="./dataset/val2017")
    visualizer = Visualizer(coco_dataset=coco_dataset,
                            results_dir="./visualization",
                            max_font_size=24,
                            min_font_size=12)
    visualizer.get_visualization("random")


if __name__ == "__main__":
    main()
