import json


class CocoDataset:
    def __init__(self, annotation_path: str, image_dir: str):
        self.segmentations = {}
        self.images_info = {}
        self.super_categories = {}
        self.categories = {}
        self.annotation_path = annotation_path
        self.image_dir = image_dir
        self.coco = {}

        self.get_annotations()

        self.get_categories()
        self.get_images_info()
        self.get_segmentations_info()

    def get_annotations(self):
        json_file = open(self.annotation_path)
        self.coco = json.load(json_file)
        json_file.close()

    def get_categories(self):
        for category in self.coco['categories']:
            cat_id = category['id']
            super_category = category['supercategory']

            # Add category to the categories dict
            if cat_id not in self.categories:
                self.categories[cat_id] = category
            else:
                print("ERROR: Skipping duplicate category id: {}".format(category))

            # Add category to super_categories dict
            if super_category not in self.super_categories:
                self.super_categories[super_category] = {cat_id}  # Create a new set with the category id
            else:
                self.super_categories[super_category] |= {cat_id}  # Add category id to the set

    def get_images_info(self):
        for image_info in self.coco['images']:
            image_id = image_info['id']
            if image_id in self.images_info:
                print("ERROR: Skipping duplicate image id: {}".format(image))
            else:
                self.images_info[image_id] = image_info

    def get_segmentations_info(self):
        for segmentation in self.coco['annotations']:
            image_id = segmentation['image_id']
            if image_id not in self.segmentations:
                self.segmentations[image_id] = []
            self.segmentations[image_id].append(segmentation)
