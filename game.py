import pygame as pg
from StateManager import StateManager as SM
from States import *

pg.init()

pg.display.set_caption("Sudoku")

size = width, height = 1200, 1000

SCREEN = pg.display.set_mode(size,depth=32)

sm = SM({
    "menu":MainMenuState(),
    "play":PlayState(),
    "pause":PauseState()
},start="menu")

clock = pg.time.Clock()
running=True
while running:
    #updating
    dt = clock.tick(60) #ms
    for event in pg.event.get():
        if event.type == pg.QUIT: running=False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running=False
    #drawing     
    SCREEN.fill(pg.color.Color("white"))
    sm(dt,SCREEN)
    pg.display.flip()
