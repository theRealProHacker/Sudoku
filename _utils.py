import pygame as pg

# typing
from typing import Any, Callable, Iterable, Optional
from pygame.surface import Surface
from pygame.font import Font, SysFont

BoardLike = list[list[Any]]
Board=list[list[int]]
Index2D=tuple[int,int]

Color = tuple[int,int,int]
KeyCodeIndex = list[tuple[int,int]]

# utils
BLACK = 0, 0, 0
WHITE = 255, 255, 255

def board_like(lmbda:Callable,n:int=9)->BoardLike:
    """Creates a board like structure. The lmbda is a callable that should take two arguments: x and y. n is the square size of the board.
    Use cases might for example be mappings of a board."""
    return [[lmbda(x,y) for y in range(n)] for x in range(n)]

def find(key:Callable,l:Iterable):
    """Finds the first matching occurrence in l"""
    for x in l:
        if key(x):return x

def range_square(n:int):
    for i in range(n):
        for j in range(n):
            yield (i,j)

def sub_indices(pos1:Index2D,pos2:Index2D):
    return pos1[0]-pos2[0], pos1[1]-pos2[1]

def get_from_set(s:set|Iterable):
    for x in s:return x

def scale_image(s:Surface,factor:float)->Surface:
    "Scale an image by a factor"
    if factor == 0:
        raise Exception("Invalid factor value: 0")
    elif factor == 1: 
        return s
    elif factor%2 == 0: 
        return scale_image(pg.transform.scale2x(s),factor//2)
    else: 
        return pg.transform.smoothscale(s,(factor*s.get_width(),factor*s.get_height()))
        
def scale_image_to_width(s:Surface, aim_width:int)->Surface:
    return scale_image(s,aim_width/s.get_width())

def draw_text(screen:pg.surface.Surface, string: str, font: pg.font.Font, color: Color, **kwargs):
    """ kwargs are passed to get_rect of the text.
    Example `center=(100,100)`"""
    text = font.render(string, True, color)
    rect = text.get_rect(**kwargs)
    screen.blit(text,rect)