from functools import cached_property
import pygame as pg
from pygame import Rect
from _utils import BLACK, WHITE, sub_indices, Callable, Index2D, Surface, Any, Color, Optional
import inspect

def mt_func(b):pass

class GeneralButton:
    just_done: dict[str,Any] = {x:False for x in ["click","hover","alt_click"]}
    def __init__(self, draw: Callable=None, area_func: Callable=None, on_click: Callable = None, on_hover: Callable = None, on_alt_click: Callable = None, **kwargs):
        """
        @params:  

        draw: Callable (b,s:Surface)

        Gets the button and the surface to draw on and draws the button. 

        area_func: Callable (b,pos:(int,int))->bool

        Gets the button and a point. Returns whether the point is in the button area

        on_click: Callable (b)

        Gets the button. Decides what happens when the button is clicked. 

        on_hover: Callable (b)

        Gets the button. Decides what happens when the button is hovered.

        on_alt_click: Callable (b) [optional]

        Gets the button. Decides what happens when the button is right clicked.

        **kwargs: Any

        These arguments will be passed to the buttons __dict__ for later access.  
        """
        self.__dict__.update(kwargs)
        self.draw = draw or self._draw
        self.area_func = area_func or self._area_func
        self.on_click = on_click or mt_func
        self.on_hover = on_hover or mt_func
        self.on_alt_click = on_alt_click or mt_func

    def __call__(self, s:Surface):
        self.update()
        self.draw(s)

    def _call(self,func):
        if len(inspect.signature(func).parameters)==1:
            func(self)
        else:
            func()

    def update(self):
        mouse_pos = pg.mouse.get_pos()
        if self.area_func(mouse_pos):
            jd_copy = dict(self.just_done)
            self.just_done["hover"]=True
            mbttns = pg.mouse.get_pressed()
            if mbttns[0]: # normal click
                self.just_done["click"]=True
                if not jd_copy["click"]:
                    return self._call(self.on_click)
            else:
                self.just_done["click"]=False
            if mbttns[1]: # alt click
                self.just_done["alt_click"]=True
            elif not mbttns[1]:
                self.just_done["alt_click"]=False
                if jd_copy["alt_click"]:
                    return self._call(self.alt_click)
            if not jd_copy["hover"]: # neither click
                return self._call(self.on_hover)
        else:
            self.just_done["hover"] = False
    
    def _draw(self,s:Surface): pass

    def _area_func(self,pos:Index2D):return True


class StaticButton(GeneralButton):
    """ A static Button that just takes an image and a position to draw. 
    Else it inherits the methods of the GeneralButton"""
    @staticmethod
    def rect_area_func(rect):
        return Rect(rect).collidepoint
    @staticmethod
    def circle_area_func(circle:tuple):
        assert len(circle) ==3
        mx,my,r=circle
        def circle_collide(pos:Index2D):
            dx,dy = sub_indices((mx,my),pos)
            return (dx**2+dy**2)<= r ** 2
        return circle_collide         

    def __init__(self,s:Surface, pos: Index2D|Rect, **kwargs):
        self.s = s
        self.pos = pos
        kwargs["draw"] = self._draw
        super().__init__(**kwargs)

    def _draw(self,s:Surface):
        s.blit(self.s,self.pos)


class TextButton(GeneralButton):
    """ A simple text button """
    non_defaults: set[str] = {
        "text","rect"
    }
    defaults: set[str] = {
        "font","border","border_color","border_radius","bg_color","text_color","hover_style"
    }
    @cached_property 
    def font(self)->pg.font.Font: # we do a cached property to make sure the font is only loaded if the TextButton is used and the font defaults to half of the buttons height
        return pg.font.SysFont(None,self.rect.height//2)
    border: int = 1
    border_color: Color = BLACK
    border_radius: int = 0
    bg_color: Color = WHITE
    text_color: Color = BLACK
    hover_style: dict[str,Any] = {}
    text_alignment: str = "center"
    text_offset: Index2D = (0,0)

    def __init__(self, text: str, rect: Rect, on_click: Callable[["TextButton"],Any], on_hover: Optional[Callable[["TextButton"],Any]] = None, on_alt_click: Optional[Callable[["TextButton"],Any]] = None, **kwargs):
        """Needs a text, a rect (including the position) and an on_click callback function. 
        The rest is optional """
        self.text = str(text)
        self.rect = Rect(rect)
        self.on_click = on_click
        self.on_hover = on_hover or mt_func
        self.on_alt_click = on_alt_click or mt_func
        self.__dict__.update(kwargs)
        self.area_func = self.rect.collidepoint

    def style_dict(self)->dict[str,Any]:
        style = {k:self.__getattribute__(k) for k in self.non_defaults|self.defaults}
        if self.just_done["hover"]:
            style.update(self.hover_style)
        return style

    def draw(self,s: Surface):
        #print(f"Button drawn: {self.text} at {self.rect.topleft}")
        style: dict[str,Any] = self.style_dict()
        pg.draw.rect(s, style["bg_color"], self.rect, border_radius = style["border_radius"])
        pg.draw.rect(s, style["border_color"], self.rect, style["border"], style["border_radius"])
        text_render = self.font.render(self.text, True, style["text_color"])
        text_rect = text_render.get_rect(center = self.rect.center)
        s.blit(text_render,text_rect)
    
def main(): 
    pg.init()
    def button_on_click(button:TextButton):
        print("Hello World")
    button_style = {
        "bg_color": pg.Color("red"),
        "border_radius": 15,
        "border_color": BLACK,
        "hover_style": {
            "bg_color": pg.Color("darkred")
        }
    }
    tButton = TextButton("Hello",Rect(100,100,400,150),button_on_click, **button_style)
    screen = pg.display.set_mode((900,600))
    while True: 
        for e in pg.event.get():
            if e.type == pg.QUIT:
                return
            elif e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                return
        screen.fill(WHITE)
        tButton(screen)
        pg.display.flip()

if __name__ == "__main__":
    try: 
        main()
    finally:
        pg.quit()