from random import randint
from copy import copy
from _utils import board_like, Board, Index2D, Iterable, Optional

class SudokuBoard:
    def __init__(self,board:Optional[Board]=None):
        if board is None:board = self.empty_board()
        assert len(board)==9
        for column in board:assert len(column)==9
        self.board:Board = copy(board)
    def get_number(self,position:Index2D)->int:
        x,y = position
        return self.board[x][y]
    def put_number(self,number:int,position:Index2D)->Board:
        x,y = position
        self.board[x][y]=number
        return self.board
    def release_number(self,position:Index2D)->Board:
        x,y = position
        self.board[x][y]=0
        return self.board
    def field_occupied(self,position:Index2D)->bool:
        x,y = position
        return not self.board[x][y] == 0
    def findNumber(self,number:int)->Iterable[Index2D]: 
        for x,y,num in self.iterate_board(withEmpty=not number): # if 0->with empty
            if num==number:yield (x,y)
    def iterate_board(self,board=None,*,withEmpty:bool=False)->Iterable[tuple[int,int,int]]:
        """withEmpty (key-word-only): If True iterates over the whole board, otherwise skips all empty fields"""
        board=board or self.board
        for x,column in enumerate(board):
            for y,num in enumerate(column):
                if withEmpty or num:yield (x,y,num)
    def print_literal(self,board=None)->str:
        board=board or None
        def yielder():
            for x,column in enumerate(board):
                for y,num in enumerate(column):
                    if num: yield str(num) 
                    else: yield "."
        return "".join(yielder())
    def boxes(self)->Iterable[list[int]]:
        for boxi in range(9):
            dx:int=boxi % 3 * 3
            dy:int=boxi // 3 * 3
            yield [self.board[x+dx][y+dy] for x in range(3) for y in range(3)]
    def rows(self)->Board:
        return list(zip(*self.board))
    @staticmethod
    def box_from_index(position:Index2D)->int:
        x,y = position
        dx=x//3
        dy=y//3
        return dy*3 + dx
    @staticmethod
    def box_as_indices(boxi:int)->list[Index2D]:
        dx:int=boxi % 3 * 3
        dy:int=boxi // 3 * 3
        return [(x+dx,y+dy) for x in range(3) for y in range(3)]
    def checkFinished(self)->bool:
        return not list(self.findNumber(0)) and self.checkValid()
    def checkValid(self)->bool: 
        return all(self.list_is_set(collumn) for collumn in self.board) and all(self.list_is_set(row) for row in self.rows()) and all(self.list_is_set(box) for box in self.boxes())
    @classmethod
    def deiterate_board(cls,iterator1d:Iterable[tuple[int,int,int]])->Board:
        """Inverse of iterate_board. Takes an Iterator with a x,y,num tuple and returns a Board"""
        board=cls.empty_board()
        for xyn in iterator1d:
            x,y,number=xyn
            board[x][y]=number
        return board
    @classmethod
    def parse_literal(cls, lit:str)->Board:
        board = cls.empty_board()
        for i,char in enumerate(lit):
            if char==".":
                num=0
            else:
                num=int(char)
            x,y=i//9,i%9
            board[x][y]=num
        return board
    @staticmethod
    def list_is_set(l:list[int])->bool: return len(l) == len(set(l)) #we can only do this because we only have integers guaranteed
    @staticmethod
    def random_full_board()->Board: return board_like(lambda _,__:randint(1,9))
    @staticmethod
    def random_board()->Board: return board_like(lambda _,__:randint(0,9))
    @staticmethod
    def empty_board()->Board:return board_like(lambda _,__:0)

