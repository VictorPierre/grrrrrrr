# -*- coding: utf-8 -*-
from __future__ import annotations

import enum
import functools
import threading
import tkinter as tk
from abc import ABC, abstractmethod
from time import sleep
from typing import List, Tuple, Dict

from common.logger import logger
from common.models import Singleton, Species
from game_management.game_monitoring import GameMonitor
from game_management.rule_checks import check_movements


class InfoCategory(enum.Enum):
    ROUND = 0,
    GAME = 1,
    PLAYER = 2,
    START = 3,
    WINNER = 4,
    BATTLE = 5,
    DETAILS = 6,


class InfoFrame(tk.Frame):
    def __init__(self, master=None, *args, **kwargs):
        super().__init__(master=master, *args, **kwargs)
        self._categories = {}
        for i, category in enumerate(InfoCategory):
            str_var = tk.StringVar(master=self, value="")
            label = tk.Label(master=self, textvariable=str_var)
            label.grid(row=i // 3, column=i % 3)
            self._categories[category] = (str_var, label)

    def update_info(self, text: str, category: InfoCategory):
        self._categories[category][0].set(value=text)

    def update_infos(self, infos: Dict[InfoCategory, str]):
        for category, info in infos.items():
            self.update_info(info, category)


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
    def update_info(self, text: str, category: InfoCategory):
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
        logger.debug("Destroying window...")
        super().destroy()
        logger.debug("Window destroyed. Quitting window...")
        super().quit()
        logger.debug("Window quited.")


class MapViewer(AbstractMapViewer, metaclass=Singleton):
    """

    Usage:

    >>> MapViewer().set_visible()  # must be in main thread
    >>> # Start a worker thread
    >>> MapViewer().mainloop()  # blocking until the window is closed
    >>> # Join the worker thread
    """

    def __init__(self, height=500, width=500):
        self._is_visible = False  # False means the map viewer is totally inactive
        self._is_active = None  # True when the window is ok, False on error or if it is not loaded
        self._to_be_refreshed = True  # True to force a refresh, False to update the screen
        self._game_map = None

        self._height = height
        self._width = width
        self._nb_updates = 0

        self._in_interaction_mode = False
        self._user_block_is_packed = False
        self._ready_to_send_moves = False
        self._next_moves = []

        self._game_monitor: GameMonitor = None

        # Tk variables
        self._window: CustomTk = None
        self._title = None
        self._info_frame: InfoFrame = None
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

            self._info_frame = InfoFrame(self._window)
            self._info_frame.update_infos({InfoCategory.ROUND: "Loading...", InfoCategory.GAME: "Game #0"})
            self._info_frame.pack()

            self._window.bind("<Key>", self._key_callback)

            self._canvas = tk.Canvas(self._window, width=self._width, height=self._height, bg='gray')
            self._canvas.pack()

            self._user_block = tk.Frame(self._window)
            _ints = "Select a departure, a destination and a number.\nReturn: send moves / Backspace: reset moves"
            self._ints_str = tk.StringVar(self._window, value=_ints)
            self._user_str = tk.StringVar(self._window, value="")

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
        # WARN: buggy if not called from main thread
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
            self._canvas.bind("<Button-1>", self._click_callback)
        self._info_frame.update_info(f"Update #{self._nb_updates}", InfoCategory.ROUND)
        self._nb_updates += 1
        logger.debug("Visualizer updated!")

    @if_is_visible_only
    def load(self, game_map: 'AbstractGameMapWithVisualizer'):
        if self._is_active and self._game_map is not None:  # map already loaded and viewer active
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
    def update_info(self, text: str, category: InfoCategory = InfoCategory.ROUND):
        if not self._is_visible:
            return
        self._info_frame.update_info(text, InfoCategory.ROUND)

    @if_is_visible_only
    def update_winner(self, winner):
        if winner is not Species.NONE:
            self._info_frame.update_info(f"{winner} won!", InfoCategory.WINNER)

    @if_is_visible_only
    def monitor(self, game_monitor: GameMonitor):
        self._game_monitor = game_monitor
        if self._is_active:
            self._info_frame.update_infos({InfoCategory.PLAYER: game_monitor.players,
                                           InfoCategory.START: game_monitor.starting_species,
                                           InfoCategory.DETAILS: f"Past results: {game_monitor.summary}",
                                           })

    def _cursor_position_to_map_position(self, cursor_position):
        x, y = cursor_position
        x_map = (self._game_map.m * x) // self._width
        y_map = (self._game_map.n * y) // self._height
        return x_map, y_map

    def _click_callback(self, event):
        if not self._in_interaction_mode:
            logger.warning("It's not your turn to play !")
            return
        cell_position = self._cursor_position_to_map_position((event.x, event.y))
        print(f"clicked at {cell_position}")
        if not self._next_moves or self._next_moves[-1][3] != -1:
            print("new move source")
            self._next_moves.append([*cell_position, 0, -1, -1])
        else:
            print("new move dest")
            self._next_moves[-1][3:] = cell_position
        print(f"moves: {self._next_moves}")
        self._user_str.set(f"Moves: {self._next_moves}")

    def _key_callback(self, event):
        if not self._in_interaction_mode:
            logger.warning("It's not your turn to play !")
            return
        print(f"key pressed: {event}")
        if event.keycode == 13:  # Return key
            print("enter: send moves")
            self._ready_to_send_moves = True
        elif event.keycode == 8:  # backspace
            print("backspace: reset moves")
            self._next_moves.clear()
        elif event.keysym in "0123456789":
            number = int(event.keysym)
            print(f"number {number}")
            if self._next_moves:
                self._next_moves[-1][2] = self._next_moves[-1][2] * 10 + number
            print(f"moves: {self._next_moves}")
        else:
            print("useless key")
        self._user_str.set(f"Moves: {self._next_moves}")

    def _pack_user_ints(self):
        self._ints_label = tk.Label(self._user_block, textvariable=self._ints_str)
        self._ints_label.grid(row=0)

        self._user_label = tk.Label(self._user_block, textvariable=self._user_str)
        self._user_label.grid(row=1)
        self._user_block.pack()
        self._user_block_is_packed = True

    def get_user_moves(self, species):
        lock = threading.Lock()
        lock.acquire()
        try:
            self._in_interaction_mode = True
            if not self._user_block_is_packed:
                self._pack_user_ints()
            self._ready_to_send_moves = False
            self._next_moves.clear()

            while not self._ready_to_send_moves:
                sleep(0.1)
            try:
                check_movements(self._next_moves, self._game_map, species)
            except AssertionError as err:
                err_msg = f"Bad prompt ({err}). Try again!"
                logger.warning(err_msg)
                self._user_str.set(err_msg)
                return self.get_user_moves(species)

            self._in_interaction_mode = False
            self._ready_to_send_moves = False
            self._user_str.set("")
        finally:
            lock.release()
        print(f"sending moves: {self._next_moves}")
        return self._next_moves.copy()
