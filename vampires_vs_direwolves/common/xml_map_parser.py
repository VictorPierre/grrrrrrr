# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import os

from common.models import Species

MAP_DEFAULT_PATH = 'grrrrrrr/graphic_interface/testmap.xml'


class XMLMapParser:
    @staticmethod
    def _retrieve_path(path=MAP_DEFAULT_PATH):
        # print(os.getcwd())
        if os.path.isfile(path):
            return path
        n_path = os.path.join("..", path)
        if os.path.isfile(n_path):
            return n_path
        n_path = os.path.join("..", n_path)
        if os.path.isfile(n_path):
            return n_path
        n_path = os.path.join("..", n_path)
        if os.path.isfile(n_path):
            return n_path
        n_path = os.path.join("..", n_path)
        if os.path.isfile(n_path):
            return n_path
        return None

    def read_xml_map(self, path=""):
        path = path or self._retrieve_path(path) or self._retrieve_path()
        if path is None:
            return FileNotFoundError("None path")
        root = ET.parse(path).getroot()
        n = int(root.get("Rows"))
        m = int(root.get("Columns"))
        assert n > 1
        assert m > 1
        updates = []
        for node in root.getchildren():
            species = Species.from_xml_tag(node.tag)
            x, y, nb = int(node.get("X")), int(node.get("Y")), int(node.get("Count"))
            update = species.to_cell((x, y), nb)
            updates.append(update)
        return n, m, updates
