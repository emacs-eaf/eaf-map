#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2018 Andy Stewart
#
# Author:     Andy Stewart <lazycat.manatee@gmail.com>
# Maintainer: Andy Stewart <lazycat.manatee@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import json
import urllib

import numpy as np
from core.utils import *
from core.webengine import BrowserBuffer
from PyQt6 import QtCore
from PyQt6.QtCore import QThread
from python_tsp.distances import great_circle_distance_matrix
from python_tsp.exact import solve_tsp_dynamic_programming


class AppBuffer(BrowserBuffer):
    def __init__(self, buffer_id, url, arguments):
        BrowserBuffer.__init__(self, buffer_id, url, arguments, False)

        self.load_index_html(__file__)

        self.threads = []

        self.vue_places = []

        self.map_path = ""

        self.marker_icon_path = os.path.join(os.path.dirname(__file__), "src", "images", "marker.png")

    def init_app(self):
        self.buffer_widget.eval_js_function("initMap", self.marker_icon_path)

    @PostGui()
    def handle_input_response(self, callback_tag, result_content):
        from inspect import signature

        handle_function_name = "handle_{}".format(callback_tag)
        if hasattr(self, handle_function_name):
            handle_function = getattr(self, handle_function_name)
            function_argument_number = len(signature(getattr(self, handle_function_name)).parameters)

            if function_argument_number == 1:
                handle_function(result_content)
            else:
                handle_function()

    @QtCore.pyqtSlot(list)
    def vue_update_places(self, vue_places):
        self.vue_places = vue_places

    def open_map(self):
        self.send_input_message("Open map: ", "open_map", "file")

    def reload_map(self):
        if os.path.exists(self.map_path):
            self.handle_open_map(self.map_path)
            message_to_emacs("Reload map successful.")
        else:
            self.open_map()

    def save_map(self):
        if self.map_path == "":
            self.send_input_message("Save map: ", "save_map", "file")
        else:
            self.handle_save_map(self.map_path)

    def add_place(self):
        self.send_input_message("Add address: ", "add_place", "string")

    def delete_place(self):
        if len(self.vue_places) == 0:
            message_to_emacs("No place can delete.")
        else:
            self.send_input_message("Delete address: ", "delete_place", "list",
                                    completion_list=list(map(lambda place_info: "#".join(place_info), self.vue_places)))

    def sort_places(self):
        if len(self.vue_places) == 0:
            message_to_emacs("No place need to sort")
        else:
            coords = []
            for place in self.vue_places:
                coords.append([float(place[1]), float(place[2])])

            sources = np.array(coords)
            distance_matrix = great_circle_distance_matrix(sources)

            new_place_indexs = solve_tsp_dynamic_programming(distance_matrix)[0]

            places = []
            for index in new_place_indexs:
                places.append(self.vue_places[index])

            self.buffer_widget.eval_js_function("updatePlaces", places)

    def handle_add_place(self, new_place):
        message_to_emacs("Fetch address list...")

        thread = FetchAddressThread(new_place)
        thread.fetch_address_finish.connect(self.fetch_address_list)
        thread.no_address_found.connect(self.no_address_found)

        self.threads.append(thread)
        thread.start()

    def handle_delete_place(self, delete_place):
        places = list(map(lambda place_info: "#".join(place_info), self.vue_places))
        places.remove(delete_place)

        places = list(map(lambda place_info: place_info.split("#"), places))
        self.buffer_widget.eval_js_function("updatePlaces", places)

    def handle_save_map(self, filepath):
        self.map_path = filepath

        with open(filepath, 'w') as file:
            file.write("\n".join(list(map(lambda place_info: "#".join(place_info), self.vue_places))))

        message_to_emacs("Save map to {}".format(filepath))

    def handle_open_map(self, filepath):
        if os.path.exists(filepath) and os.path.isfile(filepath):
            self.map_path = filepath
            with open(filepath, "r") as file:
                content = file.read()
                places = list(filter(lambda place: place != [''],
                                     list(map(lambda place_info: place_info.split("#"), content.split("\n")))
                                     ))
                self.buffer_widget.eval_js_function("updatePlaces", places)
        elif not os.path.isfile(filepath):
            message_to_emacs("Path {} is not file".format(filepath))
        else:
            message_to_emacs("Path {} not exist, please input valid emap path.".format(filepath))

    @PostGui()
    def fetch_address_list(self, locations):
        self.send_input_message("Select address to add: ", "select_address", "list",
                                completion_list=list(map(lambda loc: "{}#{}#{}".format(loc["display_name"], loc["lon"], loc["lat"]), locations)))

    @PostGui()
    def no_address_found(self, new_place):
        message_to_emacs("No address match {}".format(new_place))

    def handle_select_address(self, address):
        if len(self.vue_places) <= 1:
            self.add_address(address)
        else:
            self.select_address = address
            self.send_input_message("Insert place after number (1 - {}): ".format(len(self.vue_places)), "select_insert_order", "string")

    def handle_select_insert_order(self, order):
        if order == "":
            insert_order = -1
        else:
            insert_order = int(order)
        self.add_address(self.select_address, insert_order)

    def add_address(self, address, order=-1):
        address_info = address.split("#")
        message_to_emacs("Add new place: {}".format(address_info[0]))

        self.buffer_widget.eval_js_function("addNewPlace", address_info[0], address_info[1], address_info[2], order)

    @QtCore.pyqtSlot(str)
    def send_message_to_emacs(self, message):
        message_to_emacs(message)

class FetchAddressThread(QThread):

    fetch_address_finish = QtCore.pyqtSignal(list)
    no_address_found = QtCore.pyqtSignal(str)

    def __init__(self, new_place):
        QThread.__init__(self)

        self.new_place = new_place

    def fetch_locations(self):
        gaode_api_key_path = os.path.expanduser("~/.emacs.d/eaf/map/gaode_api_key.txt")
        gaode_api_key = ""
        if os.path.exists(gaode_api_key_path):
            with open(gaode_api_key_path) as f:
                gaode_api_key = f.read().strip()

        if gaode_api_key != "":
            import requests

            url = 'https://restapi.amap.com/v3/geocode/geo'
            params = { 'key': gaode_api_key, 'address': self.new_place}
            res = requests.get(url, params)
            content =  json.loads(res.text)

            if content["status"] == "1":
                geocodes = content["geocodes"]
                locations = list(map(lambda geocode: {
                    "display_name": geocode["formatted_address"],
                    "lon": geocode["location"].split(",")[0],
                    "lat": geocode["location"].split(",")[1]
                }, geocodes))
                return locations
            else:
                return []
        else:
            import pycurl
            from io import BytesIO

            url = 'https://nominatim.openstreetmap.org/search.php?q={}&format=jsonv2'.format(urllib.parse.quote(self.new_place))

            buffer = BytesIO()

            c = pycurl.Curl()
            c.setopt(c.URL, url)

            c.setopt(c.WRITEDATA, buffer)
            c.perform()
            c.close()

            body = buffer.getvalue()
            content = body.decode('utf-8')

            try:
                return json.loads(content)
            except:
                return []

    def run(self):
        try:
            locations = self.fetch_locations()

            if len(locations) == 0:
                self.no_address_found.emit(self.new_place)
            else:
                self.fetch_address_finish.emit(locations)
        except:
            import traceback
            traceback.print_exc()
            message_to_emacs("Fetch {} failed.".format(self.new_place))
