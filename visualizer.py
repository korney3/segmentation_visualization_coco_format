import base64
import os
import random
import re
from io import BytesIO
from math import trunc

import numpy as np
from PIL import Image as PILImage
from html2image import Html2Image

from coco_dataset import CocoDataset
from html_processor import HtmlWriter


class Visualizer:
    def __init__(self, coco_dataset: CocoDataset, results_dir="./visualization", max_font_size=12, min_font_size=6):
        self.coco_dataset = coco_dataset
        self.colors = ['blue', 'purple', 'red', 'green', 'orange', 'salmon', 'pink', 'gold',
                       'orchid', 'slateblue', 'limegreen', 'seagreen', 'darkgreen', 'olive',
                       'teal', 'aquamarine', 'steelblue', 'powderblue', 'dodgerblue', 'navy',
                       'magenta', 'sienna', 'maroon']
        os.makedirs(results_dir, exist_ok=True)
        self.results_dir = results_dir
        self.hti = Html2Image(output_path=self.results_dir)
        self.max_font_size = max_font_size
        self.min_font_size = min_font_size

        self.html_writer = HtmlWriter()

    def get_visualization(self, image_id: str):
        image_id, image_info = self.log_image_info(image_id)

        image, img_str = self.get_pil_image_and_html_image(image_info)

        adjusted_height, adjusted_ratio, adjusted_width, image_height = self.adjust_image_size(image)

        bbox_polygons, labels, poly_colors, polygons, rle_regions = self.get_polygons_info_for_html(adjusted_ratio,
                                                                                                    image_height,
                                                                                                    image_id)

        self.html_writer.get_open_html_tags(adjusted_height, adjusted_width, img_str)

        self.html_writer.add_single_object_polygons_to_html(poly_colors, polygons)

        self.html_writer.add_crowds_to_html(poly_colors, rle_regions)

        bbox_squares = self.html_writer.add_bboxes_to_html(bbox_polygons, poly_colors)
        font_size_adjustment = self.get_font_size_adjustment(bbox_squares)

        self.html_writer.add_labels_to_html(bbox_squares, font_size_adjustment, labels, poly_colors)

        self.html_writer.get_close_html_tags()

        self.save_html_as_image(self.html_writer.html, image_id)

        return os.path.join(self.results_dir, f'{image_id}.png')

    def process_run_length_encoding_of_crowd_for_html(self, adjusted_ratio, image_height, rle_regions, segm):
        # Gotta decode the RLE
        px = 0
        x, y = 0, 0
        rle_list = []
        for j, counts in enumerate(segm['segmentation']['counts']):
            if j % 2 == 0:
                # Empty pixels
                px += counts
            else:
                # Need to draw on these pixels, since we are drawing in vector form,
                # we need to draw horizontal lines on the image
                x_start = trunc(trunc(px / image_height) * adjusted_ratio)
                y_start = trunc(px % image_height * adjusted_ratio)
                px += counts
                x_end = trunc(trunc(px / image_height) * adjusted_ratio)
                y_end = trunc(px % image_height * adjusted_ratio)
                if x_end == x_start:
                    # This is only on one line
                    rle_list.append({'x': x_start, 'y': y_start, 'width': 1, 'height': (y_end - y_start)})
                if x_end > x_start:
                    # This spans more than one line
                    # Insert top line first
                    rle_list.append(
                        {'x': x_start, 'y': y_start, 'width': 1, 'height': (image_height - y_start)})

                    # Insert middle lines if needed
                    lines_spanned = x_end - x_start + 1  # total number of lines spanned
                    full_lines_to_insert = lines_spanned - 2
                    if full_lines_to_insert > 0:
                        full_lines_to_insert = trunc(full_lines_to_insert * adjusted_ratio)
                        rle_list.append(
                            {'x': (x_start + 1), 'y': 0, 'width': full_lines_to_insert, 'height': image_height})

                    # Insert bottom line
                    rle_list.append({'x': x_end, 'y': 0, 'width': 1, 'height': y_end})
        if len(rle_list) > 0:
            rle_regions[segm['id']] = rle_list
        return rle_regions

    def get_polygons_for_html(self, adjusted_ratio, polygons_list, segm):
        for segmentation_points in segm['segmentation']:
            segmentation_points = np.multiply(segmentation_points, adjusted_ratio).astype(int)
            polygons_list.append(str(segmentation_points).lstrip('[').rstrip(']'))
        return polygons_list

    def get_bbox_info_for_html(self, adjusted_ratio, bbox_polygons, segm):
        bbox = segm['bbox']
        bbox_points = [bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1],
                       bbox[0] + bbox[2], bbox[1] + bbox[3], bbox[0], bbox[1] + bbox[3],
                       bbox[0], bbox[1]]
        bbox_points = np.multiply(bbox_points, adjusted_ratio).astype(int)
        bbox_polygons[segm['id']] = str(bbox_points).lstrip('[').rstrip(']')
        return bbox_polygons, bbox_points

    def get_labels_info_for_html(self, bbox_points, labels, segm):
        labels[segm['id']] = (
            self.coco_dataset.categories[segm['category_id']]['name'], (bbox_points[0], bbox_points[1] - 4))
        return labels

    def get_polygons_info_for_html(self, adjusted_ratio, image_height, image_id):
        polygons = {}
        bbox_polygons = {}
        rle_regions = {}
        poly_colors = {}
        labels = {}
        print('  segmentations ({}):'.format(len(self.coco_dataset.segmentations[image_id])))
        for i, segm in enumerate(self.coco_dataset.segmentations[image_id]):
            polygons_list = []
            if segm['iscrowd'] != 0:
                rle_regions = self.process_run_length_encoding_of_crowd_for_html(adjusted_ratio, image_height,
                                                                                 rle_regions,
                                                                                 segm)
            else:
                polygons_list = self.get_polygons_for_html(adjusted_ratio, polygons_list, segm)

            polygons[segm['id']] = polygons_list

            poly_colors = self.set_object_color(i, poly_colors, segm)

            bbox_polygons, bbox_points = self.get_bbox_info_for_html(adjusted_ratio, bbox_polygons, segm)

            labels = self.get_labels_info_for_html(bbox_points, labels, segm)

            # Print details
            print('    {}:{}:{}'.format(segm['id'], poly_colors[segm['id']],
                                        self.coco_dataset.categories[segm['category_id']]))
        return bbox_polygons, labels, poly_colors, polygons, rle_regions

    def log_image_info(self, image_id):
        print('Image:')
        print('======')
        if image_id == 'random':
            image_id = random.choice(list(self.coco_dataset.images_info.keys()))
        image_info = self.coco_dataset.images_info[image_id]
        for key, val in image_info.items():
            print(f'  {key}: {val}')
        return image_id, image_info

    def adjust_image_size(self, image):
        max_width = 900
        image_width, image_height = image.size
        adjusted_width = min(image_width, max_width)
        adjusted_ratio = adjusted_width / image_width
        adjusted_height = adjusted_ratio * image_height
        return adjusted_height, adjusted_ratio, adjusted_width, image_height

    def get_font_size_adjustment(self, bbox_squares):
        max_bbox_square = max(bbox_squares.values())
        min_bbox_square = min(bbox_squares.values())
        if min_bbox_square==max_bbox_square:
            font_size_adjusment = lambda x_arg: x_arg
        else:
            font_size_adjusment = lambda x_arg: ((self.max_font_size - self.min_font_size) * x_arg + (
                    self.min_font_size * max_bbox_square - self.max_font_size * min_bbox_square)) / (
                                                        max_bbox_square - min_bbox_square)
        return font_size_adjusment



    def set_object_color(self, i, poly_colors, segm):
        if i < len(self.colors):
            poly_colors[segm['id']] = self.colors[i]
        else:
            poly_colors[segm['id']] = self.colors[i % len(self.colors)]
        return poly_colors

    def get_pil_image_and_html_image(self, image):
        # Open the image
        image_path = os.path.join(self.coco_dataset.image_dir, image['file_name'])
        image = PILImage.open(image_path)
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = "data:image/png;base64, " + base64.b64encode(buffered.getvalue()).decode()
        return image, img_str

    def save_html_as_image(self, html, image_id):
        self.hti.screenshot(html_str=html, save_as=f'{image_id}.png')
