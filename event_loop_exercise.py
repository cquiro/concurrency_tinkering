from collections import deque
from time import sleep
import typing as T

class Event:
    def __init__(self, name: str, action: T.Callable[..., None],
                    next_event: T.Optional["Event"] = None) -> None:
        self.name = name
        self.action = action
        self.next_event = next_event

    def execute_action(self, event_loop) -> None:
        self.action(self)
        if self.next_event:
            event_loop.register_event(self.next_event)

class EventLoop:
    def __init__(self) -> None:
        self._events: deque[Event] = deque()

    def register_event(self, event: Event) -> None:
        self._events.append(event)

    def run_forever(self) -> None:
        print(f"Queue running with {len(self._events)} events")
        while True:
            try:
                event = self._events.popleft()
            except IndexError:
                continue
            event.execute_action(self)

def knock(event: Event) -> None:
    print(event.name)
    sleep(1)

def who(event: Event) -> None:
    print(event.name)
    sleep(1)

if __name__ == "__main__":
    loop = EventLoop()
    replying = Event("Who's there?", who) 
    knocking = Event("Knock-knock", knock, replying)
    for _ in range(2):
        loop.register_event(knocking)
    loop.run_forever()
