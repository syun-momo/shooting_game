import pyglet
from pyglet.window.key import *
import math
import random


# window

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()

@window.event
def on_draw():
    pyglet.gl.glClearColor(*background, 1)
    window.clear()
    batch.draw()
    if score_draw:
        snl = score_now_label
        snl.text = f'Score {score_now:08d}'
        snl.font_size = window.height//30
        snl.draw()
        sbl = score_best_label
        sbl.text = f'Best {score_best:08d}'
        sbl.font_size = window.height//30
        sbl.x = window.width
        sbl.draw()
    if fps_draw:
        fl = fps_label
        fl.text = f'{pyglet.clock.get_fps():.1f} fps'
        fl.font_size = window.height//30
        fl.x = window.width//2
        fl.draw()


# score

score_draw = False
score_now = score_best = 0
score_now_label = pyglet.text.Label()
score_best_label = pyglet.text.Label(anchor_x='right')

def score(s=0):
    global score_draw, score_now, score_best
    score_draw = True
    score_now = max(0, score_now+s)
    score_best = max(score_now, score_best)
    return score_now


# fps

fps_draw = False
fps_label = pyglet.text.Label(anchor_x='center')


# key

key_state = key_state_old = set()

@window.event
def on_key_press(symbol, modifiers):
    key_state.add(symbol)

@window.event
def on_key_release(symbol, modifiers):
    key_state.discard(symbol)

def key(k):
    return k in key_state

def key_old(k):
    return k in key_state_old


# mouse

mouse_state = mouse_state_old = (0, 0, False)

def mouse_move(x, y, button):
    global mouse_state
    w2, h2 = window.width//2, window.height//2
    mouse_state = ((x-w2)/w2, (y-h2)/w2, button)

@window.event
def on_mouse_motion(x, y, dx, dy):
    mouse_move(x, y, mouse_state[2])

@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    mouse_move(x, y, True)

@window.event
def on_mouse_press(x, y, button, modifiers):
    mouse_move(x, y, True)

@window.event
def on_mouse_release(x, y, button, modifiers):
    mouse_move(x, y, False)

def mouse():
    return mouse_state

def mouse_old():
    return mouse_state_old


# camera

camera_x = camera_y = 0

def camera(x=None, y=None):
    global camera_x, camera_y
    if x:
        camera_x = x
    if y:
        camera_y = y
    return camera_x, camera_y


# mover

mover = []
time_sum = 0
time_min = 1/60*0.9
pause = False

class Mover:
    pass

def add(move_func, image=None, size=0.1, 
        x=0, y=0, vx=0, vy=0, **kargs):
    m = Mover()
    m.move = move_func
    m.image = image
    if image:
        m.sprite = pyglet.sprite.Sprite(image, batch=batch)
        m.sprite.scale_x = m.sprite.scale_y = 0
    else:
        m.sprite = None
    m.sx = m.sy = size
    m.x, m.y, = x, y
    m.vx, m.vy = vx, vy
    m.r = m.state = m.time = 0
    m.life = 1
    for k, v in kargs.items():
        setattr(m, k, v)
    mover.append(m)
    return m

def move(dt):
    global pause, time_sum, time_min, mover
    time_sum += dt
    if not pause and time_sum >= time_min:
        time_sum = 0
        for m in mover:
            m.move(m)
        w, w2, h2 = window.width, window.width//2, window.height//2
        for m in mover:
            if m.sprite:
                m.sprite.image = m.image
                m.sprite.scale_x = m.sx*w/m.image.width
                m.sprite.scale_y = m.sy*w/m.image.height
                m.sprite.x = (m.x-camera_x)*w2+w2
                m.sprite.y = (m.y-camera_y)*w2+h2
                m.sprite.rotation = -m.r*360
        old_mover = mover
        mover = [m for m in old_mover if m.life > 0]
        old_mover.clear()
    global score_now, fps_draw
    if key(ESCAPE):
        pyglet.app.exit()
    if key(BACKSPACE):
        score_now = 0
        mover.clear()
        start()
    if key(F) and not key_old(F):
        fps_draw = not fps_draw
    if key(S) and not key_old(S):
        pause = not pause
    global key_state_old, mouse_state_old
    key_state_old = key_state.copy()
    mouse_state_old = mouse_state

def group(*move):
    for m in mover:
        if m.move in move:
            yield m


# image

def image(file):
    img = pyglet.resource.image(file)
    img.anchor_x = img.width//2
    img.anchor_y = img.height//2
    return img


# sound

snd_dummy = None

def sound(file):
    global snd_dummy
    if not snd_dummy:
        snd_dummy = pyglet.resource.media('dummy.wav')
        snd_dummy.play()
    snd = pyglet.resource.media(file, streaming=False)
    return snd


# run

def run(start_func, w=window.width, h=window.height, 
        bg=(1, 1, 1), fs=False, tc=(0.5, 0.5, 0.5), tfn='Arial'):
    global start, background, text_color, text_font_name
    start = start_func
    background = bg
    snl, sbl, fl = score_now_label, score_best_label, fps_label
    snl.color = sbl.color = fl.color = \
        int(255*tc[0]), int(255*tc[1]), int(255*tc[2]), 255
    snl.font_name = sbl.font_name = fl.font_name = tfn
    window.set_size(w, h)
    window.set_fullscreen(fs)
    start()
    pyglet.clock.schedule(move)
    pyglet.app.run()