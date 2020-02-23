# -*- coding: utf-8 -*-
from __future__ import annotations

import functools
import threading
import tkinter as tk
from abc import ABC, abstractmethod
from typing import List, Tuple

from common.logger import logger
from common.models import Singleton


class AbstractMapViewer(metaclass=Singleton):
    @abstractmethod
    def mainloop(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def load(self, game_map: 'AbstractGameMapWithVisualizer' = None):
        pass

    @abstractmethod
    def update(self, ls_updates: List[Tuple[int, int, int, int, int]] = None):
        pass

    @abstractmethod
    def update_info(self, text: str):
        pass


def if_is_visible_only(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self._is_visible:
            return
        return func(self, *args, **kwargs)

    return wrapper


class CustomTk(tk.Tk):
    def __init__(self, map_viewer):
        super().__init__()
        self._map_viewer = map_viewer

    def destroy(self):
        self._map_viewer._is_active = False
        super().destroy()


class MapViewer(AbstractMapViewer, metaclass=Singleton):
    def __init__(self, height=500, width=500):
        self._is_visible = False  # False means the map viewer is totally inactive
        self._is_active = None  # True when the window is ok, False on error or if it is not loaded
        self._to_be_refreshed = True  # True to force a refresh, False to update the screen
        self._game_map = None

        self._height = height
        self._width = width
        self._nb_updates = 0

        # Tk variables
        self._window: CustomTk = None
        self._title = None
        self._info_str: tk.StringVar = None
        self._info_label: tk.Label = None
        self._canvas: tk.Canvas = None

    @property
    def is_visible(self):
        return self._is_visible

    def set_visible(self, value: bool = True):
        self._is_visible = value

    def _init_map_viewer(self):
        if threading.current_thread().getName() != 'MainThread':
            logger.warning(f"Tkinter window not in main thread: {threading.current_thread().getName()}!")
        if not self._is_active or not self._window.is_active:
            self._window = CustomTk(self)

        # Tk window
        try:
            self._title = self._window.title("Vampires versus Werewolves")
            self._info_str = tk.StringVar(self._window, value="Loading...")  # todo
            self._info_label = tk.Label(self._window, textvariable=self._info_str)
            self._info_label.pack()

            self._canvas = tk.Canvas(self._window, width=self._width, height=self._height, bg='gray')
            self._canvas.pack()
            logger.info("Map viewer loaded!")
            self._is_active = True
        except RuntimeError as err:
            logger.error(f"Failed to load Tk window: {err}")
            logger.exception(err)
            self._is_active = False

    @if_is_visible_only
    def mainloop(self):
        self._init_map_viewer()
        self.update()
        self._window.lift()
        logger.info("Map viewer started!")
        self._window.mainloop()

    @if_is_visible_only
    def close(self):
        self._game_map = None
        self._nb_updates = 0

    @if_is_visible_only
    def stop(self):
        self.close()
        self._is_active = False
        try:
            logger.debug("Closing visualizer...")
            self._window.destroy()
            self._window.quit()
            logger.debug("Visualizer closed.")
        except tk.TclError as err:
            logger.error(f"Tkinter error: {err}")
            logger.exception(err)

    def _update(self, ls_updates: List[Tuple[int, int, int, int, int]] = None):
        logger.debug("Updating visualizer...")
        if ls_updates is None or self._to_be_refreshed:
            self._canvas.delete(tk.ALL)
            positions = self._game_map.positions
            self._to_be_refreshed = False
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

    @if_is_visible_only
    def load(self, game_map: 'AbstractGameMapWithVisualizer'):
        if self._is_active and self._game_map is not None:  # map already loaded
            self._update()
            logger.info("Map viewer reloaded!")
        else:
            self._game_map = game_map
            self._to_be_refreshed = True
            logger.info("Map viewer loaded!")

    @if_is_visible_only
    def update(self, ls_updates: List[Tuple[int, int, int, int, int]] = None):
        if not self._is_active or self._game_map is None:
            logger.warning("MapViewer not ready to receive updates!")
            self._to_be_refreshed = True
            return
        try:
            self._update(ls_updates)
        except RuntimeError as err:
            logger.warning(f"Map viewer exception: {err}. Map viewer is now deactivated.")
            logger.exception(err)
            self._is_active = False

    @if_is_visible_only
    def update_info(self, text: str):
        if not self._is_visible:
            return
        self._info_str.set(value=text)
