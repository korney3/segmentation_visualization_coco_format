import re
from math import trunc

import numpy as np


class HtmlWriter:
    def __init__(self):
        self.html = ""

    def get_open_html_tags(self, adjusted_height, adjusted_width, img_str):
        self.html = '<div class="container" style="position:relative;">'
        self.html += '<img src="{}" style="position:relative;top:0px;left:0px;width:{}px;">'.format(img_str,
                                                                                                    adjusted_width)
        self.html += '<div class="svgclass"><svg width="{}" height="{}">'.format(adjusted_width, adjusted_height)

    def add_labels_to_html(self, bbox_squares, font_size_adjusment, labels, poly_colors):
        for seg_id, label in labels.items():
            color = poly_colors[seg_id]
            square = bbox_squares[seg_id]
            font_size = font_size_adjusment(square)
            self.html += f'<text x="{label[1][0]}" y="{label[1][1]}" style="fill:{color}; font-size: {font_size}pt;">{label[0]}</text>'

    def get_bbox_square(self, seg_id, bbox_string):
        bbox_list = re.findall(r'\d+', bbox_string.strip())
        coordinates = [int(i) for i in bbox_list]
        width = coordinates[2] - coordinates[0]
        height = coordinates[5] - coordinates[1]
        return width * height

    def add_bboxes_to_html(self, bbox_polygons, poly_colors):
        bbox_squares = {}
        for seg_id, points in bbox_polygons.items():
            fill_color = poly_colors[seg_id]
            stroke_color = poly_colors[seg_id]
            self.html += '<polygon points="{}" style="fill:{}; stroke:{}; stroke-width:1; fill-opacity:0" />'.format(
                points, fill_color, stroke_color)
            bbox_squares[seg_id] = self.get_bbox_square(seg_id, points)
        return bbox_squares

    def add_crowds_to_html(self, poly_colors, rle_regions):
        for seg_id, rect_list in rle_regions.items():
            fill_color = poly_colors[seg_id]
            stroke_color = poly_colors[seg_id]
            for rect_def in rect_list:
                x, y = rect_def['x'], rect_def['y']
                w, h = rect_def['width'], rect_def['height']
                self.html += '<rect x="{}" y="{}" width="{}" height="{}" style="fill:{}; stroke:{}; stroke-width:1; fill-opacity:0.5; stroke-opacity:0.5" />'.format(
                    x, y, w, h, fill_color, stroke_color)

    def add_single_object_polygons_to_html(self, poly_colors, polygons):
        for seg_id, points_list in polygons.items():
            fill_color = poly_colors[seg_id]
            stroke_color = poly_colors[seg_id]
            for points in points_list:
                self.html += '<polygon points="{}" style="fill:{}; stroke:{}; stroke-width:1; fill-opacity:0.5" />'.format(
                    points, fill_color, stroke_color)

    def get_close_html_tags(self):
        self.html += '</svg></div>'
        self.html += '</div>'
        self.html += '<style>'
        self.html += '.svgclass { position:absolute; top:0px; left:0px;}'
        self.html += '</style>'
