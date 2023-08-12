from typing import Any

import obspython as obs
import pygetwindow as gw
import re


class WinampPlayer:
    def __init__(self):
        self.window_title = 'Winamp'
        self.text_source_name = 'Winamp: Now Playing'
        self.no_song_text = ''
        self.song_status_patterns = [
            r'\bBuild\b',
            r'\bStopped\b'
        ]

        self.player_window = None

    def description(self):
        return 'Capture Winamp Window Title and Update Text Source'

    def get_title(self):
        player_windows = gw.getWindowsWithTitle(self.window_title)
        for window in player_windows:
            title = window.title.strip()
            if self.is_valid_player_title(title):
                return self.collect_clean_title(title)
        return None

    def is_valid_player_title(self, title):
        return title.endswith(self.window_title) and len(title) > len(
            self.window_title) and self.is_previous_char_valid(title)

    def is_previous_char_valid(self, title):
        previous_char_index = len(title) - len(self.window_title) - 1
        previous_char = title[previous_char_index]
        return previous_char.isspace() or previous_char == '-'

    def collect_clean_title(self, title):
        previous_char_index = len(title) - len(self.window_title) - 1
        return title[:previous_char_index].rstrip('- ').strip()

    def update_text_source(self, title):
        text_source = obs.obs_get_source_by_name(self.text_source_name)
        if text_source is not None:
            settings = obs.obs_data_create()
            obs.obs_data_set_string(settings, 'text', title)
            obs.obs_source_update(text_source, settings)
            obs.obs_data_release(settings)
            obs.obs_source_release(text_source)

    def get_song_status(self, title):
        for pattern in self.song_status_patterns:
            if re.search(pattern, title):
                return True
        return False

    def tick(self):
        if not self.player_window:
            self.player_window = gw.getWindowsWithTitle(self.window_title)
            if not self.player_window:
                return

        winamp_title: Any | None = self.get_title()

        if winamp_title and self.get_song_status(winamp_title):
            winamp_title = self.no_song_text

        elif not winamp_title:
            winamp_title = self.no_song_text

        self.update_text_source(winamp_title)


# Create an instance of the WinampPlayer class
winampPlayer = WinampPlayer()


# Define the script description
def script_description():
    return winampPlayer.description()


# Define the script properties
def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_text(props, 'text_source_name', 'Text Source Name', obs.OBS_TEXT_DEFAULT)

    return props


# Define the script tick function
def script_tick(seconds):
    winampPlayer.tick()
