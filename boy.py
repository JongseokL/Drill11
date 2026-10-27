import math

from pico2d import get_time, load_image
from transitions import Machine


class AutoRun:
    START_SPEED = 5.0
    ACCELERATION = 0.05
    MAX_SPEED = 25.0
    START_SIZE = 100.0
    GROWTH = 0.2
    MAX_SIZE = 200.0

    @staticmethod
    def enter(boy):
        boy.frame = 0
        boy.dir = boy.face_dir
        boy.auto_run_speed = AutoRun.START_SPEED
        boy.auto_run_size = AutoRun.START_SIZE

    @staticmethod
    def update(boy):
        boy.frame = (boy.frame + 1) % 8
        boy.x += boy.dir * boy.auto_run_speed
        boy.auto_run_speed = min(
            boy.auto_run_speed + AutoRun.ACCELERATION,
            AutoRun.MAX_SPEED
        )
        boy.auto_run_size = min(
            boy.auto_run_size + AutoRun.GROWTH,
            AutoRun.MAX_SIZE
        )

        half_width = boy.auto_run_size / 2
        left = half_width
        right = 800 - half_width

        if boy.x <= left:
            boy.x = left
            boy.dir = 1
            boy.face_dir = 1
        elif boy.x >= right:
            boy.x = right
            boy.dir = -1
            boy.face_dir = -1

    @staticmethod
    def draw(boy):
        bottom = 100 if boy.dir == 1 else 0
        boy.image.clip_draw(
            boy.frame * 100, bottom, 100, 100,
            boy.x, boy.y,
            boy.auto_run_size, boy.auto_run_size
        )


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.dir = 0
        self.face_dir = 1
        self.image = load_image('animation_sheet.png')
        self.idle_start_time = 0.0

        states = ['IDLE', 'SLEEP', 'RUN', 'AUTO_RUN']
        transitions = [
            {
                'trigger': 'fall_asleep',
                'source': 'IDLE',
                'dest': 'SLEEP',
                'after': 'start_sleep'
            },
            {
                'trigger': 'wake_up',
                'source': 'SLEEP',
                'dest': 'IDLE',
                'after': 'restart_idle_timer'
            },
            {
                'trigger': 'start_run',
                'source': ['IDLE', 'SLEEP'],
                'dest': 'RUN',
                'before': 'set_run_direction'
            },
            {
                'trigger': 'stop_run',
                'source': 'RUN',
                'dest': 'IDLE',
                'after': 'finish_run'
            },
            {
                'trigger': 'start_auto_run',
                'source': 'IDLE',
                'dest': 'AUTO_RUN',
                'after': 'begin_auto_run'
            }
        ]

        self.machine = Machine(
            model=self,
            states=states,
            transitions=transitions,
            initial='IDLE',
            auto_transitions=False
        )
        self.restart_idle_timer()

    def restart_idle_timer(self):
        self.idle_start_time = get_time()

    def start_sleep(self):
        self.frame = 0
        self.dir = 0

    def set_run_direction(self, direction):
        self.dir = direction
        self.face_dir = direction

    def finish_run(self):
        self.dir = 0
        self.restart_idle_timer()

    def begin_auto_run(self):
        AutoRun.enter(self)

    def press_direction(self, direction):
        if self.state == 'IDLE' or self.state == 'SLEEP':
            self.start_run(direction)
        elif self.state == 'RUN':
            self.set_run_direction(direction)

    def release_direction(self, direction):
        if self.state == 'RUN' and self.dir == direction:
            self.stop_run()

    def update(self):
        if self.state == 'IDLE':
            self.frame = (self.frame + 1) % 8

            if get_time() - self.idle_start_time >= 5.0:
                self.fall_asleep()
        elif self.state == 'RUN':
            self.frame = (self.frame + 1) % 8
            self.x += self.dir * 5
            self.x = max(50, min(750, self.x))
        elif self.state == 'AUTO_RUN':
            AutoRun.update(self)

    def draw(self):
        if self.state == 'IDLE':
            bottom = 300 if self.face_dir == 1 else 200
            self.image.clip_draw(
                self.frame * 100, bottom, 100, 100,
                self.x, self.y
            )
        elif self.state == 'SLEEP':
            bottom = 300 if self.face_dir == 1 else 200
            self.image.clip_composite_draw(
                0, bottom, 100, 100,
                math.pi / 2, '',
                self.x, 55, 100, 100
            )
        elif self.state == 'RUN':
            bottom = 100 if self.dir == 1 else 0
            self.image.clip_draw(
                self.frame * 100, bottom, 100, 100,
                self.x, self.y
            )
        elif self.state == 'AUTO_RUN':
            AutoRun.draw(self)
