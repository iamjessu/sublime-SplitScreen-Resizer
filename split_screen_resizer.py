"""
SplitScreen-Resizer v2.0.0
by Jesus Leon
https://github.com/iamjessu/sublime-SplitScreen-Resizer

Contributors:
Artis Raugulis <artis@devart.lv>

A fork of:

    SplitScreen v1.0.0
    by Nick Fisher
    https://github.com/spadgos/sublime-SplitScreen

Combined with the plugin:

    Split Navigation
    by Linus Oleander
    https://github.com/oleander/sublime-split-navigation
"""
import sublime, sublime_plugin
import re


def addUp(lst):
    out = [0.0]
    for i in lst:
        out.append(out[-1] + i)

    return out

class PanelChangedCommand(sublime_plugin.EventListener):
    last_work_group = None
    settings = None
    def on_activated(self, view):
        #load settings
        if self.settings == None:
            self.settings = sublime.load_settings("splitscreen-resizer.sublime-settings")

        #if mouse focus disabled - exit ..
        if self.settings.get('disable_mouse_focus'):
            return 0

        #current active group
        current_active_group = view.window().active_group()

        #Working group not changed - doing nothing ...
        if self.last_work_group == current_active_group:
            return 0

        #update last work group
        self.last_work_group = current_active_group

        #by default we show left side ...
        args = {"side":"left", "ratio":self.settings.get('ratio_left'), "autofocus":False}
        #if right side active - update args to right side version
        if(current_active_group == 1):
            args = {"side":"left", "ratio":self.settings.get('ratio_right'), "autofocus":False}

        win = view.window()
        win.run_command("split_screen_resizer", args)


class SplitScreenResizerCommand(sublime_plugin.WindowCommand):
    def run(self, side, ratio, autofocus):
        win = self.window
        num = win.num_groups()
        act = win.active_group()

        if side == "left":
            ratio_val = ratio
            act = act - 1

        if side == "right":
            ratio_val = ratio
            act = act + 1

        # By keeping it as modulus operation we ensure that:
        #     - It continues focusing the next/previous column in case we're 
        #       working with more than 2 columns.
        #     - It acts as a loop, focusing the first/last column when the
        #       last/first is reached respectively.
        if autofocus:
            win.focus_group(act % num)


        """
        Keep original code in case we want to add vertical resizing.
        """
        parts = re.split("\\s*,\\s*", ratio)

        horiz = parts[0] or "1"
        vert = parts[1] or "1" if len(parts) > 1 else "1"

        vert = map(float, re.split(":", vert))
        horiz = map(float, re.split(":", horiz))
        vertTotal = sum(vert)
        horizTotal = sum(horiz)
        vert = map((lambda x: x / vertTotal), vert)
        horiz = map((lambda x: x / horizTotal), horiz)

        cols = addUp(horiz)
        rows = addUp(vert)

        cells = []
        for x, val1 in enumerate(horiz):
            for y, val2 in enumerate(vert):
                cells.append([x, y, x + 1, y + 1])

        self.window.run_command('set_layout', {
            "cols": cols,
            "rows": rows,
            "cells": cells
        })