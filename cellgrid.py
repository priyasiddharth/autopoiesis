"""
Copyright 2020 Siddharth Priya

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

"""
This is a GUI viewer for Autopoiesis. It uses code grid construction logic from
https://stackoverflow.com/questions/30023763/how-to-make-an-interactive-2d-grid-in-a-window-in-python

"""
import math
import time
from tkinter import *

import helper
import world_model as world
import world_presenter as presenter
import world_viewer as viewer


class Cell():
    FILLED_COLOR_BG = "green"
    EMPTY_COLOR_BG = "white"
    FILLED_COLOR_BORDER = "green"
    EMPTY_COLOR_BORDER = "black"

    LINK_FREE = 'red'
    LINK_SINGLE = 'yellow'
    LINK_DOUBLE = 'orange'
    SUBSTRATE = 'green'
    CATALYST = 'pink'

    def __init__(self, master, x, y, size):
        """ Constructor of the object called by Cell(...) """
        self.master = master
        self.abs = x
        self.ord = y
        self.size = size
        self.fill = False

    def _switch(self):
        """ Switch if the cell is filled or not. """
        self.fill = not self.fill

    def draw(self):
        """ order to the cell to draw its representation on the canvas """
        if self.master != None:
            fill = Cell.FILLED_COLOR_BG
            outline = Cell.FILLED_COLOR_BORDER

            if not self.fill:
                fill = Cell.EMPTY_COLOR_BG
                outline = Cell.EMPTY_COLOR_BORDER

            xmin = self.abs * self.size
            xmax = xmin + self.size
            ymin = self.ord * self.size
            ymax = ymin + self.size

            self.master.create_rectangle(xmin, ymin, xmax, ymax, fill=fill, outline=outline)

    def drawCell(self, element: world.T):
        """ order to the cell to draw its representation on the canvas """
        if self.master != None:
            fill = Cell.FILLED_COLOR_BG
            outline = Cell.FILLED_COLOR_BORDER

            if not self.fill:
                fill = Cell.EMPTY_COLOR_BG
                outline = Cell.EMPTY_COLOR_BORDER

            xmin = self.abs * self.size
            xmax = xmin + self.size
            ymin = self.ord * self.size
            ymax = ymin + self.size
            xmid = int((xmin + xmax) / 2)
            ymid = int((ymin + ymax) / 2)

            ch = ''
            if isinstance(element, world.Hole):
                ch = 'H'
            elif isinstance(element, world.Substrate):
                fill = Cell.SUBSTRATE
                ch = 'S'
            elif isinstance(element, world.Link):
                fill = Cell.LINK_FREE
                if element.isFree():
                    ch = 'L'
                elif element.isSinglyBonded():
                    fill = Cell.LINK_SINGLE
                    ch = 'b'
                else:
                    fill = Cell.LINK_DOUBLE
                    ch = 'B'
            elif isinstance(element, world.Catalyst):
                fill = Cell.CATALYST
                ch = 'K'
            self.master.create_rectangle(xmin, ymin, xmax, ymax, fill=fill, outline=outline)
            self.master.create_text(xmid, ymid, text=ch)

class CellGrid(Canvas):
    def __init__(self, master, rowNumber, columnNumber, cellSize, *args, **kwargs):
        Canvas.__init__(self, master, width=cellSize * columnNumber, height=cellSize * rowNumber, *args, **kwargs)

        self.cellSize = cellSize

        self.grid = []
        for row in range(rowNumber):

            line = []
            for column in range(columnNumber):
                line.append(Cell(self, column, row, cellSize))

            self.grid.append(line)


        self.draw()

    def draw(self):
        for row in self.grid:
            for cell in row:
                cell.draw()

    def _eventCoords(self, event):
        row = int(event.y / self.cellSize)
        column = int(event.x / self.cellSize)
        return row, column

    def updateCells(self, sim_grid: [world.Point, world.T]):
        size = int(math.sqrt(len(sim_grid)))
        for j in range(size):
            for i in range(size):
                e = sim_grid[world.Point(i, j)]
                cell = self.grid[j][i]
                cell.drawCell(e)


class CellGridViewer(viewer.WorldViewer):

    def __init__(self):
        super().__init__()
        self._app = Tk()
        self.size = 10
        self._cellgrid = CellGrid(self._app, self.size, self.size, self.size * self.size)
        self._cellgrid.pack()

    def updateView(self, grid: [world.Point, world.T], iteration: int):
        self._cellgrid.updateCells(grid)
        self._app.update_idletasks()


class CellGridPresenter(presenter.WorldPresenter):

    def __init__(self, viewer: viewer.WorldViewer, ctx: world.WorldContext):
        super().__init__(viewer, ctx)

    def _doSingleStep(self):
        r = super()._doSingleStep()
        time.sleep(1)
        return r


def main():
    # The initial parameters are in the json file
    path = 'config.json'
    view = CellGridViewer()
    ctx = world.WorldFactory().createWorld(helper.Config.loadConfigFromFile(path))
    presenter = CellGridPresenter(view, ctx)
    presenter.doSimulate()


if __name__ == "__main__":
    main()
