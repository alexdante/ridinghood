#!/usr/bin/env python


# This file is part of Ridinghood.
#
# Ridinghood is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ridinghood is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ridinghood.  If not, see <http://www.gnu.org/licenses/>.


import subprocess
import select
import time
import re
import gi
gi.require_version("WebKit", "3.0")
from gi.repository import WebKit, Gtk, GObject


class TestWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_default_size(512, 512)

        self.socket = Gtk.Socket();
        self.add(self.socket)
        self.show_all()

        self.proc = None
        self.connect("destroy", self.destroy_event)
        self.create_universe()

    def create_universe(self, url="http://pirateradiotheater.org"):
        args_list = ["python", "browser.py", url]
        self.proc = subprocess.Popen(args_list, stdout=subprocess.PIPE)

        start = time.time()
        plug_id = None
        plug_pattern = r'^PLUG ID: (?P<plug_id>\d+)$'
        while True:
            ready = select.select([self.proc.stdout], [], [])[0]
            if ready:
                line = ready[0].readline()
                match = re.match(plug_pattern, line)
                if match:
                    plug_id = int(match.groupdict()['plug_id'])
                    break
            time.sleep(0.01)
            if time.time() - start > 1:
                break
            
        if plug_id:
            self.socket.add_id(plug_id)

        else:
            print "ERROR: No browser plug found."
                
    def destroy_event(self, *args, **kargs):
        Gtk.main_quit(args, kargs)
        if self.proc:
            self.proc.kill()
        

if __name__ == "__main__":
    Gtk.init()
    TestWindow()
    Gtk.main()
