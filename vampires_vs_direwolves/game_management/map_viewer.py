# -*- coding: utf-8 -*-
from __future__ import annotations

import tkinter as tk
from time import sleep
from typing import List, Tuple

from common.logger import logger
from common.models import Singleton


class MapViewer(metaclass=Singleton):
    def __init__(self, height=500, width=500, show_map=True):
        self._show_map = show_map
        if not self._show_map:
            return
        self._game_map = None

        self._height = height
        self._width = width
        self._nb_updates = 0

        # Tk window
        self._window: tk.Tk = tk.Tk()
        self._title = None
        self._info_str: tk.StringVar = None  # todo
        self._info_label: tk.Label = None
        self._canvas: tk.Canvas = None

        self._active = True  # todo

    def load_map_viewer(self, game_map):
        if not self._show_map:
            return
        if self._game_map:  # map already loaded
            self._canvas.delete(tk.ALL)
            self._nb_updates = 0
            logger.info("Map viewer reloaded!")
            return
        self._game_map = game_map
        # Tk window
        try:
            self._title = self._window.title("Vampires versus Werewolves")
            self._info_str = tk.StringVar(self._window, value="Loading...")  # todo
            self._info_label = tk.Label(self._window, textvariable=self._info_str)
            self._info_label.pack()

            self._canvas = tk.Canvas(self._window, width=self._width, height=self._height, bg='gray')
            self._canvas.pack()
            logger.info("Map viewer loaded!")
        except RuntimeError as err:
            logger.error(f"Failed to load Tk window: {err}")
            logger.exception(err)
            self._active = False

    def start(self):
        if not self._show_map:
            return
        while not isinstance(self._window, tk.Tk):
            logger.warning("Map viewer not ready!")
            sleep(1)
        self._window.mainloop()

    def stop(self):
        if not self._show_map:
            return
        try:
            self._canvas.delete(tk.ALL)
        except tk.TclError as err:
            logger.error(f"Tkinter error: {err}")
            logger.exception(err)
        self._game_map = None

    def quit(self):
        if not self._show_map:
            return
        self._window.destroy()
        self._window.quit()
        self._game_map = None

    def update(self, ls_updates: List[Tuple[int, int, int, int, int]] = None):
        if not self._show_map:
            return
        logger.debug("Updating visualizer...")
        while not isinstance(self._canvas, tk.Canvas):
            sleep(1)
        if ls_updates is None:
            self._canvas.delete(tk.ALL)
            positions = self._game_map.positions
        else:
            positions = [(x, y) for x, y, _h, _v, _w in ls_updates]
        for x, y in positions:
            species, number = self._game_map.get_cell_species_and_number((x, y))
            self._canvas.create_rectangle(self._width / self._game_map.m * x,
                                          self._height / self._game_map.n * y,
                                          self._width / self._game_map.m * (x + 1),
                                          self._height / self._game_map.n * (y + 1),
                                          fill=species.to_color()
                                          )
            self._canvas.create_text(self._width / self._game_map.m * (x + 0.5),
                                     self._height / self._game_map.n * (y + 0.5),
                                     text=str(number),
                                     )
        self._info_str.set(f"Update #{self._nb_updates}")
        self._nb_updates += 1
        logger.debug("Visualizer updated!")

    def update_info(self, text: str):
        if not self._show_map:
            return
        self._info_str.set(value=text)
