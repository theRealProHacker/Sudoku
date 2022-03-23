from functools import cache
import pygame as pg
from pygame.font import SysFont
from StateManager import State
from random import choice
from collections import OrderedDict
from GameSudokuBoard import GameSudokuBoard as GSB
from Button import TextButton
from _utils import draw_text, BLACK, Surface
from itertools import islice

class PlayState(State):
    finished = False
    unlocked = True
    def on_init(self):
        self.board_kwargs = {
            "pos":pg.Vector2(pg.display.get_surface().get_rect().center)-(400,400),
            "color":(120,10,30),
            "text_color":(80,0,0),
            "size":800,
            "on_finished":self.on_finished
        }
        cx, cy = self.get_board_center()
        def menu_click(_):self.exit(to="menu")
        rect = pg.rect.Rect(0,0,300,100)
        rect.center = cx,cy-100
        self.menu_button = TextButton("Back to Menu", rect, menu_click)
        rect.y += 200
        self.restart_button = TextButton("Restart", rect, self.restart_game)
    def on_enter(self,frm: str,**kwargs):
        if frm == "menu":
            self.finished = False
            self.diff=kwargs.get("difficulty")
            self.board_kwargs["board"]=self.new_board()
            self.board=GSB(**self.board_kwargs)
        elif frm == "pause":
            self.unlocked = False
    def update(self,_):
        if self.finished:
            if any(x for x in pg.key.get_pressed() if x in [pg.K_RETURN,pg.K_SPACE]):
                self.restart_game()
            self.menu_button.update()
            self.restart_button.update()
        else:
            self.board.update()
            if pg.key.get_pressed()[pg.K_p]:
                if self.unlocked:
                    self.exit("pause")
            else:
                self.unlocked = True
    def draw(self,s:Surface):
        self.board.draw(s)
        if self.finished:
            x,y=self.board.draw_pos
            w=h=self.board.size
            trans_rect = pg.surface.Surface((w,h))
            trans_rect.set_alpha(80)
            trans_rect.fill((200,200,200))
            s.blit(trans_rect,(x,y))
            self.menu_button.draw(s)
            self.restart_button.draw(s)
    def on_finished(self):
        self.finished = True
    def restart_game(self):
        self.finished=False
        self.reset_board()
    @cache
    def get_sudoku(self,path:str)->list[str]:
        with open("data/"+path,"r") as f:
            lines=f.readlines()
        return [line.strip() for line in lines if not line.startswith("#") and line.strip()]
    diff_dict=OrderedDict(zip(
        ["Easy","Medium","Hard","Magical","Hardest","Diabolic","Impossible"],
        ["puzzles0_kaggle",
        "puzzles1_unbiased",
        "puzzles2_17_clue",
        "puzzles3_magictour_top1465",
        "puzzles4_forum_hardest_1905",
        "puzzles6_forum_hardest_1106",
        "puzzles7_serg_benchmark"]
    ))
    def new_board(self):
        return GSB.parse_literal(choice(self.get_sudoku(self.diff_dict[self.diff])))
    def reset_board(self):
        rename={
            "draw_pos":"pos",
            "_size":"size",
            "text_size":"text_size",
            "font":"font",
            "color":"color",
            "text_color":"text_color",
            "bg_color":"bg_color",
            "sel_color":"sel_color"
        }
        self.board_kwargs={k:v for _k,v in self.board.__dict__.items() if (k:=rename.get(_k))}
        self.board_kwargs["board"]=self.new_board()
        self.board_kwargs["on_finished"]=self.on_finished
        self.board=GSB(**self.board_kwargs)
    def get_board_center(self):
        return tuple(pos+self.board_kwargs["size"]/2 for pos in self.board_kwargs["pos"])

class MainMenuState(State):
    def __init__(self):        
        self.titleFont = SysFont(None,100)
        self.bigFont = SysFont(None,40)
    def on_init(self):
        self.buttons: list[TextButton] = []
        srect = pg.display.get_surface().get_rect()
        for i,v in enumerate(["Easy","Medium","Hard"]):
            rect = pg.rect.Rect(0,300+i*150,300,100)
            rect.centerx = srect.centerx
            self.buttons.append(TextButton(v,rect,self.button_click,font=self.bigFont,difficulty=v))

    def button_click(self,button):
        self.exit("play",difficulty=button.difficulty)

    def update(self,_):
        for button in self.buttons:
            button.update()
    
    def draw(self, screen: pg.surface.Surface):
        draw_text(screen,"Main Menu", self.titleFont, BLACK, center=(screen.get_rect().centerx,180))
        for button in self.buttons:
            button.draw(screen)

class PauseState(State):
    unlocked = False
    def on_init(self):
        cx = pg.display.get_surface().get_rect().centerx
        self.titleFont = SysFont(None,70)
        self.screen_rect = pg.Rect(0, 75, 600, 600)
        self.screen_rect.centerx = cx
        rect = pg.Rect(0,0, 300, 100)
        rect.centerx = cx
        rect.y += 275 # Resume button
        self.resume_button = TextButton("Resume", rect, self.resume)
        rect.y += 150 # Menu button
        self.menu_button = TextButton("Main Menu",rect, self.menu)
    def on_enter(self, frm: str, **kwargs):
        assert frm=="play", f"Can only pause from play state. Got: {frm}"
        self.unlocked = False
    def update(self, _):
        if pg.key.get_pressed()[pg.K_p]:
            if self.unlocked:
                return self.resume()
        else:
            self.unlocked = True
        if any(pg.mouse.get_pressed()) and not self.screen_rect.collidepoint(pg.mouse.get_pos()):
            return self.resume()
        self.menu_button.update()
        self.resume_button.update()
    def draw(self,s:Surface):
        """ Draw a golden overlay in the center of the screen
        on top of which there is the paused title, the resume button and the menu button """
        self.manager["play"].draw(s)
        backdrop = s.copy()
        backdrop.fill(pg.Color("black"))
        backdrop.set_alpha(30)
        s.blit(backdrop,(0,0))
        pg.draw.rect(s,pg.Color("white"),self.screen_rect)
        pg.draw.rect(s,pg.Color("black"),self.screen_rect,width = 1)
        draw_text(s, "Paused", self.titleFont, pg.Color("black"), center=(self.screen_rect.centerx,200))
        self.resume_button.draw(s)
        self.menu_button.draw(s)
    def resume(self):
        self.exit(to="play")
    def menu(self):
        self.exit(to="menu")

__all__ = [
    "PlayState",
    "MainMenuState",
    "PauseState"
]