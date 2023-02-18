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

from PyQt6.QtCore import QThread
from PyQt6 import QtCore
from core.webengine import BrowserBuffer
from geopy.geocoders import Nominatim
from core.utils import message_to_emacs

class AppBuffer(BrowserBuffer):
    def __init__(self, buffer_id, url, arguments):
        BrowserBuffer.__init__(self, buffer_id, url, arguments, False)

        self.load_index_html(__file__)

        self.threads = []

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

    def add_new_place(self):
        self.send_input_message("Add new address: ", "add_new_place", "string")

    def handle_add_new_place(self, new_place):
        message_to_emacs("Fetch address list...")

        thread = FetchAddressThread(new_place)
        thread.fetch_address_finish.connect(self.fetch_address_list)
        thread.no_address_found.connect(self.no_address_found)

        self.threads.append(thread)
        thread.start()

    def fetch_address_list(self, location):
        self.send_input_message("Select address to add: ", "select_address", "list",
                                completion_list=list(map(lambda loc: "{}#{}#{}".format(loc.address, loc.longitude, loc.latitude), location)))

    def no_address_found(self, new_place):
        message_to_emacs("No address match {}".formt(new_place))

    def handle_select_address(self, address):
        address_info = address.split("#")
        message_to_emacs("Add new place: {}".format(address_info[0]))

        self.buffer_widget.eval_js_function("addNewPlace", address_info[0], address_info[1], address_info[2])

class FetchAddressThread(QThread):

    fetch_address_finish = QtCore.pyqtSignal(list)
    no_address_found = QtCore.pyqtSignal(str)

    def __init__(self, new_place):
        QThread.__init__(self)

        self.new_place = new_place

    def run(self):
        geolocator = Nominatim(user_agent="eaf-map")
        location = geolocator.geocode(self.new_place, exactly_one=False)

        if location:
            self.fetch_address_finish.emit(location)
        else:
            self.no_address_found.emit(self.new_place)
