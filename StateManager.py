from collections import deque
import threading
from threading import Thread
from pygame import time, display, gfxdraw as gfx
from pygame.color import Color
from pygame.font import SysFont
from pygame.surface import Surface
from typing import Iterable, Optional

def get_from_set(s:set|Iterable):
    for x in s:return x


class State:
    manager: "StateManager" = NotImplemented
    @staticmethod
    def exit(to: "State", **kwargs)->None:
        """ Call this function to exit the current state to another state """
        raise NotImplementedError("Use a state only with a state manager")
    def on_init(self)->None:pass
    def on_enter(self,frm: str, **kwargs)->None:pass
    def on_exit(self,to:str)->None:pass
    def update(self,dt:float)->None:pass
    def draw(self,s:Surface)->None:pass

class LoadingState:
    font = SysFont(None,26) #type: ignore
    def __init__(self):
        self.cx,self.cy = display.get_surface().get_rect().center
        self.text = self.font.render("Loading...", True, Color("black"))
        self.text_rect = self.text.get_rect(center=(self.cx,self.cy-100))
        self.angle = 320
    def update(self,dt:float, _: State)->None:
        self.angle -= dt//10
        if self.angle <=10:
            self.angle = 320
    def draw(self,s:Surface)->None:
        s.blit(self.text,self.text_rect)
        gfx.arc(s,self.cx,self.cy-100,50,0,self.angle, Color("black"))

class StateManager:
    def __getitem__(self, key: str)->State:
        return self.states[key]
    def _state_exit(self):
        def inner_func(to: str,**kwargs):
            self.set_state(to,**kwargs)
        return inner_func
    def __init__(self,states: dict[str,State],*, start: str="", loading_state: Optional[LoadingState] = None, preload: bool = False):
        assert "" not in states, "\"\" (the empty string) cannot be name of a state"
        self.states = states
        self.loading_state = loading_state or LoadingState()
        self.inited = {k:False for k in self.states.keys()}
        self.loading = {k:False for k in self.states.keys()}
        self.threads: dict[str,Thread] = {}
        for name, state in states.items(): # tell states to which manager they belong
            state.exit = self._state_exit() #type: ignore
            state.manager = self
            if preload:
                self._init_state(name)
        if len(self.states) == 1:
            print("Why would you only have one state? It has one upside, we automatically started the StateManager for you. ")
            start = get_from_set(self.states)
        if start:
            self.start(start)
    def start(self,state: str)->bool:
        """ Start the state manager with the given state and return whether start succeeded"""
        if not self._current_state:
            assert state in self.states, "Start state has to be in managers states"
            self._current_state = state #type: ignore
            self._init_state(state)
            return True
        return False
    def __call__(self, dt: Optional[float] = None, s: Optional[Surface] = None)->None:
        """ __Calling__ the manager is like updating and drawing at the same time """
        dt = dt or time.get_ticks()
        s = s or display.get_surface()
        self.update(dt)
        self.draw(s)
    def update(self, dt: float)->None:
        """ Update the state manager with the given delta time """
        if not self._current_state:
            raise Exception("StateManager wasn't started yet")
        else:
            if not self.loading[self._current_state]:
                self.current_state().update(dt)
            else:
                if self.loading_state is not None:
                    self.loading_state.update(dt, self.current_state())
    def draw(self, s: Surface)->None:
        """ Draw the state manager to the given Surface """
        if not self._current_state:
            raise Exception("StateManager wasn't started yet")
        else:
            if not self.loading[self._current_state]:
                self.current_state().draw(s)
            else:
                if self.loading_state is not None:
                    self.loading_state.draw(s)

    _current_state: str = ""
    def current_state(self)->State:
        if self._current_state:
            return self.states[self._current_state]
        else: 
            raise ValueError("Current state not set")
    def current_state_str(self):
        """ The current state as a string"""
        return self._current_state
    def set_state(self, new_state: str, **kwargs):
        if not self._current_state:
            print("Don't call set_state without starting the StateManager (explicit is better than implicit)")
            self.start(new_state)
        else:
            assert new_state in self.states and new_state,f"State invalid `{new_state}`"
            self._change_state(new_state,kwargs)
    def _init_state(self, state: str)->None:
        if not self.inited[state]:
            self.loading[state] = True
            def thread_func(): # Thread this
                self[state].on_init()
                self.inited[state] = True
                self.loading[state] = False
                del self.threads[threading.current_thread().name]
            thread = Thread(target = thread_func)
            self.threads[thread.name] = thread
            thread.start()
    def _change_state(self, new_state: str, kwargs)->None:
        old_state = self._current_state
        self.loading[new_state] = True
        self._current_state = new_state
        def thread_func():
            self[old_state].on_exit(new_state)
            if not self.inited[new_state]:
                self[new_state].on_init()
                self.inited[new_state] = True
            self[new_state].on_enter(frm = old_state, **kwargs)
            self.loading[new_state] = False
            del self.threads[threading.current_thread().name]
        thread = Thread(target = thread_func)
        self.threads[thread.name] = thread
        thread.start()
            
    def __del__(self):
        for thread in self.threads.values():
            thread.join()

class StackStateManager():
    _state_stack: deque[str] = deque()
    def _state_exit(self):
        def inner_func(to: str,**kwargs):
            self.set_state(to,**kwargs)
        return inner_func
    def _state_push(self):
        def inner_func(to: str,**kwargs):
            self.set_state(to,**kwargs)
        return inner_func
    def __init__(self,states: dict[str,State],*,start: str=""):
        assert "" not in states, "\"\" cannot be the name of a state"
        self.states = states
        self.inited = {k:False for k in self.states.keys()}
        for state in states.values(): # tell states to which manager they belong
            state.exit = self._state_exit() #type: ignore
            state.manager = self # type: ignore
        if len(self.states) == 1:
            print("Why do you only have one state? It has one upside, we automatically started the StateManager for you. ")
            self.start(get_from_set(self.states))
        elif start:
            self.start(start)
    def start(self,state: str):
        if not self._current_state:
            assert state in self.states, "Start state has to be in managers states"
            self._current_state = state #type: ignore
            self.current_state().on_init()
            self.inited[self._current_state] = True #type: ignore
    def __call__(self,dt:float,s:Surface)->None:
        self.update(dt)
        self.draw(s)
    def update(self,dt:float)->None:
        if not self._current_state:
            raise Exception("StateManager wasn't started yet")
        else:
            self.active_state().update(dt)
    def draw(self,s:Surface)->None:
        if not self._current_state:
            raise Exception("StateManager wasn't started yet")
        else:
            self.active_state().draw(s)
    def peek_state(self):
        elem = self.pop_state()
        if elem is not None:
            self._state_stack.append(elem)
        return elem
    def push_state(self,state:str):
        self._state_stack.append(state)
        if not self.inited[state]:
            self.states[state].on_init()
    def pop_state(self):
        try:
            return self._state_stack.pop()
        except IndexError:
            return None
    _current_state: str = ""
    def current_state(self)->State:
        if self._current_state:
            return self.states[self._current_state]
        else: 
            raise ValueError("Current state not set")
    @property
    def _active_state(self):
        return self.peek_state() or self._current_state
    def active_state(self):
        return self.states[self._active_state]
    def set_state(self, state:str, **kwargs):
        if not self._current_state:
            print("Don't call set_state without starting the StateManager")
            self.start(state)
        else:
            assert state in self.states and state is not None,"State invalid "+state
            self.current_state().on_exit(to=state)
            last_state = self._current_state
            self._current_state = state
            if not self.inited[state]:
                self.current_state().on_init()
            self.current_state().on_enter(frm=last_state,**kwargs)
    def current_state_str(self):return self._current_state
    def active_state_str(self): return self._active_state
