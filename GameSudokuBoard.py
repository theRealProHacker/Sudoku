from SudokuBoard import SudokuBoard
import pygame as pg
from _utils import WHITE, BLACK, board_like , range_square, get_from_set, sub_indices, scale_image_to_width, Callable, Iterable, Surface, KeyCodeIndex, Color, Index2D, Board, Font, Optional
#https://stackoverflow.com/questions/6339057/draw-a-transparent-rectangles-and-polygons-in-pygame

class GameSudokuBoard(SudokuBoard):
    def __init__(self, board:Optional[Board]=None, pos:Optional[Index2D]=None, size:Optional[int]=None, text_size:Optional[int]=None, font:Optional[Font]=None, color:Optional[Color]=None, text_color:Optional[Color]=None, bg_color:Optional[Color]=None, sel_color:Optional[Color]=None, on_finished:Optional[Callable]=None):
        "on_finished: function to call when finished"
        super().__init__(board)
        self.draw_pos = max(pos[0],3),max(pos[1],3) or (3,3)
        self.size = size or self.default_size
        self.text_size = text_size or 50
        self.font = font or pg.font.Font(None, self.text_size)
        self.color = color or BLACK
        self.text_color = text_color or BLACK
        self.bg_color = bg_color or WHITE
        self.sel_color = sel_color or (160,160,160)
        self.on_finished = on_finished or (lambda self: print("On finished not defined"))
        self.numbers: list[Surface] = [self.font.render(str(i+1),True,self.text_color) for i in range(9)]
        self.note_numbers=[scale_image_to_width(s,self.size/60) for s in self.numbers]
        self.selected_field: Optional[Index2D]=None
        self.selected_num = 0
        self.preset:list[Index2D] = [(x,y) for x,column in enumerate(self.board) for y,num in enumerate(column) if num]
        self.notes:list[list[set[int]]] = board_like(lmbda=lambda x,y:set())
    def put_number(self,number: int, pos: Index2D): 
        super().put_number(number,pos)
        self.set_notes(set(),pos)
    def set_notes(self,notes: set[int],pos: Index2D):
        x,y = pos
        self.notes[x][y] = notes
    def get_notes(self,pos: Index2D):
        x,y = pos
        return self.notes[x][y]
    def get_field_rect(self,pos:Index2D)->pg.rect.Rect:
        x,y = pos
        posx,posy=self.draw_pos
        sboxsize=self.size//9
        return pg.rect.Rect(posx+x*sboxsize,posy+y*sboxsize,sboxsize,sboxsize)
    def _set_size(self,size:int):
        if not size%9==0:
            self._size = round(size/9)*9
            #print (f"Size ({size}) has to be divisible by 9. Was rounded to the closest number divisable by 9 ({self.size})")
        else: 
            self._size=size
    def _del_size(self): self._size=self.default_size
    default_size = 270
    size=property(lambda self:self._size,_set_size,_del_size,"Size of the board.")
    key_codes:KeyCodeIndex = [(i,pg.key.key_code(str(i))) for i in range(0,10)]
    just_pressed_keys={k:False for k in range(512)}
    def update(self):
        if self.checkFinished():
            self.on_finished()
        pressed_keys=pg.key.get_pressed()
        if self.assure_single_key(pressed_keys,pg.K_m):
            self.cheat()
        if not (self.selected_field is None or self.selected_field in self.preset):
            if pressed_keys[pg.K_DELETE]:
                self.put_number(0,self.selected_field)
            else:
                if pg.key.get_mods() & pg.KMOD_CTRL: #control input
                    def key_click():
                        if num:
                            self.get_notes(self.selected_field).symmetric_difference_update({num})
                        else:
                            self.get_notes(self.selected_field).clear()
                else: # normal input
                    def key_click():
                        self.put_number(num,self.selected_field)
                        self.selected_num = num
                for num,key in self.key_codes:
                    if self.assure_single_key(pressed_keys,key):
                        key_click()
        else: 
            for num,key in self.key_codes:
                if self.assure_single_key(pressed_keys,key):
                    self.selected_num=num
        mb=pg.mouse.get_pressed()
        if mb[0]:
            self.mouse_click(pg.mouse.get_pos())
        elif any(mb):
            self.alternate_mouse_click(pg.mouse.get_pos())
    def draw(self,surface:Surface):
        """Draws the board to the given surface"""
        posx,posy=self.draw_pos
        sboxsize=self.size//9
        mboxsize=self.size//3
        #draw background color
        pg.draw.rect(surface,self.bg_color, (posx,posy,self.size,self.size))
        #draw selected field color
        if self.selected_field is not None:
            pg.draw.rect(surface,self.sel_color, self.get_field_rect(self.selected_field))
        #draw sudoku fields and number
        for x,y,num in self.iterate_board(withEmpty=True):
            rect=self.get_field_rect((x,y))
            draw_x,draw_y,width,height=rect
            if num:
                if num == self.selected_num:
                    # draw a gray background for all boxes of same number as selected
                    trans_rect = pg.surface.Surface((width,height))
                    trans_rect.set_alpha(120)
                    trans_rect.fill(self.sel_color)
                    surface.blit(trans_rect,(draw_x,draw_y))
                text=self.numbers[num-1]
                text_rect=text.get_rect(center=(draw_x+sboxsize/2,draw_y+sboxsize/2))
                surface.blit(text,text_rect)
            else: #draw notes
                for note in self.get_notes((x,y)):
                    inote=note-1
                    text=self.note_numbers[inote]
                    center_pos=(draw_x+inote%3*sboxsize/3+sboxsize/6,draw_y+sboxsize/27+inote//3*sboxsize/3+sboxsize/6)
                    text_rect=text.get_rect(center=center_pos)
                    surface.blit(text,text_rect)
            pg.draw.rect(surface,self.color,rect,1)
        # draw the bigger boxes
        for x,y in range_square(3):
            pg.draw.rect(surface,self.color,(posx-1+x*mboxsize,posy-1+y*mboxsize,mboxsize+2,mboxsize+2),3)
        #frame the whole board
        pg.draw.rect(surface,self.color,(posx-3,posy-3,self.size+6,self.size+6),2)
    def get_index_from_pos(self,pos:Index2D)->Optional[Index2D]:
        abs_pos = sub_indices(pos,self.draw_pos)
        if all(x>=0 and x<self.size for x in abs_pos): # both coordinates have to be in the sudoku board
            posx,posy = abs_pos
            x=int(posx/(self.size/9))
            y=int(posy/(self.size/9))
            return x,y
    def assure_single_key(self,pressed_keys,key:int)->bool:
        if pressed_keys[key]:
            if not self.just_pressed_keys[key]:
                self.just_pressed_keys[key] = True
                return True
        else:
            self.just_pressed_keys[key] = False
    def mouse_click(self,pos:Index2D):
        posi = self.get_index_from_pos(pos)
        self.selected_field = posi
        if self.selected_field is not None:
            self.selected_num = self.get_number(self.selected_field)
    def alternate_mouse_click(self,pos:Index2D):
        posi = self.get_index_from_pos(pos)
        if posi:
            self.fill_safe_notes(posi)
            self.fill_notes(posi)
    def long_mouse_click(self,pos:Index2D):
        posi = self.get_index_from_pos(pos)
        if posi: 
            self.fill_safe_notes(posi)
    def fill_notes(self,pos:Index2D):
        """ Fills the trivial notes of a box """
        x,y = pos
        notes=set(range(1,10))
        collumn=set(self.board[x])
        row = set(self.rows()[y])
        box = set(list(self.boxes())[self.box_from_index(pos)])
        self.set_notes(notes.difference(collumn.union(row.union(box))),pos)
    def fill_safe_notes(self,pos:Index2D):
        """ Fills boxes with single naked hints"""
        notes = self.get_notes(pos)
        fill_safe=len(notes)==1 and not self.get_number(pos)
        if fill_safe:
            self.put_number(get_from_set(notes),pos)
        return fill_safe
    def cheat(self):
        for x,y,num in self.iterate_board(withEmpty=True):
            if not num:
                self.fill_notes((x,y))
        for pos in range_square(9):
            self.fill_safe_notes(pos)
