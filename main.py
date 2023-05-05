from random import random

import pygame as pg

pg.init()


# Just for the meme (only used in FPS)
def getDep(location, count=1):
    with open("resources/coconut.bmp", "rb") as dependency:
        dependency.seek(location)
        return int.from_bytes(dependency.read(count), "big")


# Tile resources
WALL_TILE_IMG = pg.image.load("resources/wall.png")
GRUOND_TILE_IMG = pg.image.load("resources/ground.png")
END_TILE_IMG = pg.image.load("resources/end.png")

# Entity resources
PLAYER_IMG = pg.image.load("resources/player.png")
ENEMY_IMG = pg.image.load("resources/enemy.png")

WWIDTH = 320
WHEIGHT = 320
TILE_SIZE = 16
FPS = getDep(0x738e)

window = pg.display.set_mode((WWIDTH, WHEIGHT))
pg.display.set_caption("Libilabirintus")
running = True


# Resize window ww width and wh height
def resize_window(ww, wh):
    global window, WWIDTH, WHEIGHT
    window = pg.display.set_mode((ww, wh))
    WWIDTH = ww
    WHEIGHT = wh


def entity_reset():
    global entities, player, spacedCounter
    entities = list()
    player = Entity(PLAYER_IMG, 1, 1)
    entities.append(player)
    spacedCounter = spacedCounterMax


def entity_clear():
    global entities, player
    entities = None
    player = None


# Draw a transparent rectangle col color, w width, h height, to x,y coordinates
def draw_opacity_rect(col, w, h, x, y):
    r = pg.Surface((w, h), pg.SRCALPHA)
    r.fill(col)
    window.blit(r, (x, y))


# Based on difficulty level gives back any type of data: e when easy, m when medium, h when hard
def get_val_by_difficulty(e, m, h):
    if difficulty == 0:
        return e
    elif difficulty == 1:
        return m
    else:
        return h


# Returns a random direction up/down/left/right (x,y) coordinate
def randdir():
    r = int(random() * 2)  # 0 or 1
    return (r * 2 - 1, 0) if random() < 0.5 else (0, r * 2 - 1)  # x, y: (+-1, 0) or (0, +-1)


# Class for map generation algorithm
class Group():
    def __init__(self, n):
        self.value = n


# map tiles class
class Tile():
    # constructor where x and y are coordinates in the map
    def __init__(self, texture, x, y, type, groupn):
        self.texture = texture
        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE
        self.type = type  # 0:grund, 1:solid, 2:end
        self._groupn = Group(groupn)
        self._parent = None
        self.child = None

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, p):
        self._parent = p
        p.child = self

    @property
    def groupn(self):
        return self._groupn.value

    @groupn.setter
    def groupn(self, group):
        self._groupn.value = group

    def get_group(self):
        return self._groupn

    # get great-great-...-grandfather
    def get_adam(self):
        if self.parent is not None:
            return self.parent.get_adam()
        return self

    # get grand-grand-...-grandchild
    def get_genz(self):
        if self.child is not None:
            return self.child.get_genz()
        return self

    # used during map generation
    def refresh_group(self, tile):
        adam = self.get_adam()
        while adam.child is not None:
            adam.child.change(tile)
            adam = adam.child
        adam.change(tile)

    def change(self, tile, texture=None, type=None):
        self._groupn = tile.get_group()
        if texture is not None:
            self.texture = texture
        if type is not None:
            self.type = type
        return self

    # draw tile
    def draw(self):
        window.blit(self.texture, (self.x, self.y))


# entity class
class Entity():
    def __init__(self, texture, x, y):
        self.texture = texture
        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE

    # entity movement check and execute
    def move(self, x, y):
        MW = WWIDTH // TILE_SIZE
        MH = WHEIGHT // TILE_SIZE
        if 0 <= self.y // TILE_SIZE + y < MH and 0 <= self.x // TILE_SIZE + x < MW and (
                currentScreen.map[self.y // TILE_SIZE + y][self.x // TILE_SIZE + x].type == 0 or
                currentScreen.map[self.y // TILE_SIZE + y][self.x // TILE_SIZE + x].type == 2):
            self.x += x * TILE_SIZE
            self.y += y * TILE_SIZE

    # draw entity
    def draw(self):
        window.blit(self.texture, (self.x, self.y))


# enemy class
class Enemy(Entity):
    def __init__(self, texture, x, y, movedelaymax):
        super().__init__(texture, x, y)
        self.movedelaymax = movedelaymax
        self.movedelay = 0

    # it moves before drawing
    def draw(self):
        self.movedelay += 1
        if self.movedelay == self.movedelaymax:
            self.move(*randdir())
            self.movedelay = 0
        super().draw()


# basic creen class
class Screen:
    def __init__(self, ww, wh):
        self.ww = ww
        self.wh = wh
        self.buttons = dict()

    def init(self):
        resize_window(self.ww, self.wh)

    def get_buttons(self):
        return self.buttons

    def draw(self):
        pass


class ScreenMainMenu(Screen):
    def __init__(self):
        super().__init__(320, 260)

    def draw(self):
        window.fill((0, 127, 127))
        # Buttons
        color = (0, 192, 0)
        self.buttons["difficulty"] = pg.draw.rect(window, color,
                                                  pg.Rect(16, 140, 60 + get_val_by_difficulty(35, 55, 33), 24))
        self.buttons["start"] = pg.draw.rect(window, color, pg.Rect(60, 180, 85, 37))
        self.buttons["exit"] = pg.draw.rect(window, color, pg.Rect(200, 180, 60, 37))
        self.buttons["keybinds"] = pg.draw.rect(window, color, pg.Rect(16, 90, 112, 37))
        self.buttons["endless"] = pg.draw.rect(window, color, pg.Rect(184, 90, 120, 24))
        font = pg.font.SysFont("arial", 54)
        pg.draw.rect(window, (0, 0, 128), pg.Rect(0, 0, WWIDTH, 80))
        window.blit(font.render("LibiLabi", True, (128, 255, 0)), (80, 20))
        font = pg.font.SysFont("arial", 18)
        window.blit(font.render("Difficulty: " + get_val_by_difficulty("easy", "medium", "hard"), True, (0, 0, 0)),
                    (16, 140))
        window.blit(font.render("Endless mode: " + ("on" if endless else "off"), True, (0, 0, 0)), (184, 90))
        font = pg.font.SysFont("arial", 32)
        window.blit(font.render("START", True, (0, 0, 0)), (60, 180))
        window.blit(font.render("EXIT", True, (0, 0, 0)), (200, 180))
        window.blit(font.render("Keybinds", True, (0, 0, 0)), (16, 90))


class ScreenGameOver(Screen):
    def __init__(self, dat):
        super().__init__(320, 320)
        self.dat = dat

    def draw(self):
        window.fill((127, 0, 0))
        # Buttons
        color = (192, 192, 0)
        self.buttons["start"] = pg.draw.rect(window, color, pg.Rect(60, 180, 85, 37))
        self.buttons["exit"] = pg.draw.rect(window, color, pg.Rect(200, 180, 60, 37))
        self.buttons["main_menu"] = pg.draw.rect(window, color, pg.Rect(60, 240, 152, 37))
        font = pg.font.SysFont("arial", 24)
        window.blit(font.render("last level: " + str(self.dat["lvl"]), True, (0, 0, 0)), (32, 32))
        font = pg.font.SysFont("arial", 32)
        window.blit(font.render("START", True, (0, 0, 0)), (60, 180))
        window.blit(font.render("EXIT", True, (0, 0, 0)), (200, 180))
        window.blit(font.render("MAIN MENU", True, (0, 0, 0)), (60, 240))


class ScreenLevel(Screen):
    def __init__(self, lvl, ww, wh, view_radius):
        super().__init__(ww, wh)
        self.lvl = lvl
        self._map = self.generate_map()
        self.view_radius = view_radius * TILE_SIZE

    @property
    def map(self):
        return self._map

    def generate_map(self):
        m = []
        MW = self.ww // TILE_SIZE
        MH = self.wh // TILE_SIZE
        groupn = 0
        # init map
        m.append([Tile(WALL_TILE_IMG, j, 0, 1, 0) for j in range(MW)])
        for i in range(1, MH - 1):
            m.append([Tile(WALL_TILE_IMG, 0, i, 1, 0)])
            for j in range(1, MW - 1):
                if j % 2 == 0 or i % 2 == 0:
                    m[i].append(Tile(WALL_TILE_IMG, j, i, 1, 0))
                else:
                    groupn += 1
                    m[i].append(Tile(GRUOND_TILE_IMG, j, i, 0, groupn))
            m[i].append(Tile(WALL_TILE_IMG, MW - 1, i, 1, 0))
        m.append([Tile(WALL_TILE_IMG, j, MH - 1, 1, 0) for j in range(MW)])

        # Kruskal's algorithm for maze generation based on https://vishald.com/blog/kruskals-maze-generation/
        def randloc():
            return int((random() * (MH - 1)) // 2) * 2 + 1, int((random() * (MW - 1)) // 2) * 2 + 1

        groupset = set(range(1, groupn + 1))
        while len(groupset) != 1:
            rx, ry = randloc()
            # print(rx,ry,m[rx][ry].groupn)
            dx, dy = randdir()
            # print("d's",dx,dy)
            wallx = dx + rx;
            wally = dy + ry
            dx += wallx;
            dy += wally
            if 0 <= dx < MH and 0 <= dy < MW and m[rx][ry].groupn != m[dx][dy].groupn and m[wallx][wally].groupn == 0:
                min_tile = None
                groupset.discard(max(m[rx][ry].groupn, m[dx][dy].groupn))
                if min(m[rx][ry].groupn, m[dx][dy].groupn) == m[rx][ry].groupn:
                    min_tile = m[rx][ry]
                    min_tile.get_adam().parent = m[dx][dy].get_genz()
                else:
                    min_tile = m[dx][dy]
                    min_tile.get_adam().parent = m[rx][ry].get_genz()
                m[wallx][wally].change(min_tile, GRUOND_TILE_IMG, 0)
                min_tile.get_adam().parent = m[wallx][wally]
                m[wallx][wally].refresh_group(min_tile)
        ex, ey = randloc()
        m[ex][ey].change(m[ex][ey], END_TILE_IMG, 2)
        self.endloc = {"x": ey * TILE_SIZE, "y": ex * TILE_SIZE}
        global entities
        for i in range(int(random() * 5 * get_val_by_difficulty(1, 2, 3)) + 5 + self.lvl):
            en = Enemy(ENEMY_IMG, *randloc(), 10 + int(random() * 10))  # Warning: FPS inc means faster enemy
            addable = True
            for e in entities:
                if e.x == en.x and e.y == en.y:
                    addable = False
                    break
            if addable and en.x >= TILE_SIZE * 4 and en.y >= TILE_SIZE * 4:
                entities.append(en)
            else:
                i -= 1
        return m

    def draw(self):
        for r in self._map:
            for e in r:
                if e is not None:
                    e.draw()


class ScreenKeybinds(Screen):
    def __init__(self):
        super().__init__(260, 220)

    def draw(self):
        window.fill((0, 127, 92))
        color = (0, 192, 0)
        self.buttons["back"] = pg.draw.rect(window, color, pg.Rect(40, 140, 74, 37))
        font = pg.font.SysFont("arial", 32)
        window.blit(font.render("BACK", True, (0, 0, 0)), (40, 140))
        font = pg.font.SysFont("arial", 16)
        window.blit(font.render("-->D", True, (0, 0, 0)), (5 * TILE_SIZE, 4 * TILE_SIZE))
        window.blit(font.render("A<--", True, (0, 0, 0)), (2 * TILE_SIZE, 4 * TILE_SIZE))
        window.blit(font.render("W", True, (0, 0, 0)), (4.33 * TILE_SIZE, 1.66 * TILE_SIZE))
        window.blit(font.render("^", True, (0, 0, 0)), (4.45 * TILE_SIZE, 2.66 * TILE_SIZE))
        window.blit(font.render("|", True, (0, 0, 0)), (4.5 * TILE_SIZE, 3 * TILE_SIZE))
        window.blit(font.render("|", True, (0, 0, 0)), (4.5 * TILE_SIZE, 5 * TILE_SIZE))
        window.blit(font.render("V", True, (0, 0, 0)), (4.33 * TILE_SIZE, 5.75 * TILE_SIZE))
        window.blit(font.render("S", True, (0, 0, 0)), (4.33 * TILE_SIZE, 6.75 * TILE_SIZE))
        Tile(PLAYER_IMG, 4, 4, 0, 0).draw()

        Tile(PLAYER_IMG, 8, 4, 0, 0).draw()
        draw_opacity_rect((0, 255, 0, 127), TILE_SIZE, 4, 8 * TILE_SIZE, 5 * TILE_SIZE)
        Tile(WALL_TILE_IMG, 9, 4, 0, 0).draw()
        Tile(PLAYER_IMG, 10, 4, 0, 0).draw()
        draw_opacity_rect((0, 0, 0, 127), TILE_SIZE, 4, 10 * TILE_SIZE, 5 * TILE_SIZE)
        draw_opacity_rect((0, 127, 92, 150), TILE_SIZE, TILE_SIZE, 10 * TILE_SIZE, 4 * TILE_SIZE)
        window.blit(font.render("--SPACE+D-->", True, (0, 0, 0)), (8 * TILE_SIZE, 3 * TILE_SIZE))
        window.blit(font.render("ESC: close game", True, (0, 0, 0)), (128, 108))
        window.blit(font.render("P: pause game", True, (0, 0, 0)), (128, 124))


# winning screen
class ScreenGG(Screen):
    def __init__(self):
        super().__init__(320, 128)
        self.particles = list()
        for i in range(100):
            self.add_particle()
        self.d = 0

    def add_particle(self):
        self.particles.append(
            [(random() * 0xff, random() * 0xff, random() * 0xff), random() * WWIDTH, random() * 10, 1])  # col,x,y,h

    def draw(self):
        window.fill((0, 255, 127))
        for p in self.particles:
            pg.draw.rect(window, p[0], pg.Rect(p[1], p[2], 2, p[3]))
            p[2] += p[2] / 100 + random()
            p[3] += random() / 2
            if p[2] > WHEIGHT:
                self.particles.remove(p)
                self.add_particle()
        font = pg.font.SysFont("arial", 32)
        txt = font.render("ESCAPED! CONGRATULATION!", True, (0, 0, 0))
        window.blit(txt, (txt.get_rect().width - self.d, 0))
        self.d = (self.d + 1) % (2 * txt.get_rect().width)
        color = (64, 192, 0)
        self.buttons["main_menu"] = pg.draw.rect(window, color, pg.Rect((WWIDTH - 152) / 2, 43, 152, 37))
        window.blit(font.render("MAIN MENU", True, (0, 0, 0)), ((WWIDTH - 152) / 2, 43))


grad = 20
gradW = 2
entities = None  # list()
player = None  # Entity(PLAYER_IMG, 1, 1)
mainmenuScreen = ScreenMainMenu()
keybindsScreen = ScreenKeybinds()
gameoverScreen = None
currentScreen = mainmenuScreen
currentScreen.init()

spaced = False
spacedCounterMax = FPS * 8
spacedCounter = spacedCounterMax
difficulty = 0
clock = pg.time.Clock()
paused = False
endless = False
while running:
    clock.tick(FPS)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.KEYDOWN:
            if player is not None:
                if event.key == pg.K_p:
                    paused = not paused
                if not paused:
                    if spaced:
                        unit = 2
                        spacedCounter = 0
                        spaced = False
                    else:
                        unit = 1
                    if event.key == pg.K_w:
                        player.move(0, -unit)
                    elif event.key == pg.K_a:
                        player.move(-unit, 0)
                    elif event.key == pg.K_s:
                        player.move(0, unit)
                    elif event.key == pg.K_d:
                        player.move(unit, 0)
                    elif event.key == pg.K_SPACE:
                        if not spaced and spacedCounter == 0:
                            spacedCounter = spacedCounterMax
                        elif spacedCounter == spacedCounterMax:
                            spaced = True
            if event.key == pg.K_ESCAPE:
                running = False
        elif event.type == pg.MOUSEBUTTONUP:
            for n, b in currentScreen.get_buttons().items():
                if b.collidepoint(pg.mouse.get_pos()):
                    # print("Mouse released on the "+n)
                    if n == "start":
                        entity_reset()
                        currentScreen = ScreenLevel(1, 336 * 2 - 16, 336, get_val_by_difficulty(10, 8, 6))
                        currentScreen.init()
                    elif n == "exit":
                        running = False
                    elif n == "difficulty":
                        difficulty = (difficulty + 1) % 3
                    elif n == "keybinds":
                        currentScreen = keybindsScreen
                        currentScreen.init()
                    elif n == "back" or n == "main_menu":
                        currentScreen = mainmenuScreen
                        currentScreen.init()
                    elif n == "endless":
                        endless = not endless
    if paused:
        pg.draw.rect(window, (255, 255, 255), pg.Rect(WWIDTH / 2 - 8 - 20, WHEIGHT / 2 - 50, 16, 100))
        pg.draw.rect(window, (255, 255, 255), pg.Rect(WWIDTH / 2 - 8 + 20, WHEIGHT / 2 - 50, 16, 100))
        pg.display.update()
        continue
    currentScreen.draw()
    if isinstance(currentScreen, ScreenLevel):
        for e in entities:
            e.draw()

        if spaced:
            draw_opacity_rect((0, 127, 255, 92), TILE_SIZE, TILE_SIZE, player.x, player.y)

        color = (0, 0, 0)
        pg.draw.rect(window, color, pg.Rect(0, player.y + currentScreen.view_radius + TILE_SIZE, WWIDTH, WHEIGHT))
        pg.draw.rect(window, color, pg.Rect(player.x + currentScreen.view_radius + TILE_SIZE, 0, WWIDTH, WHEIGHT))
        pg.draw.rect(window, color, pg.Rect(0, 0, player.x - currentScreen.view_radius, WHEIGHT))
        pg.draw.rect(window, color, pg.Rect(0, 0, WWIDTH, player.y - currentScreen.view_radius))
        for i in range(grad):
            r = pg.Surface((currentScreen.view_radius * 2 + TILE_SIZE, gradW), pg.SRCALPHA)
            r.fill((0, 0, 0, (255 // grad) * (grad - i)))
            window.blit(r, (player.x - currentScreen.view_radius, player.y - currentScreen.view_radius + i * gradW))
            window.blit(r, (
                player.x - currentScreen.view_radius,
                player.y + currentScreen.view_radius + TILE_SIZE - (i + 1) * gradW))
            r = pg.Surface((gradW, currentScreen.view_radius * 2 + TILE_SIZE), pg.SRCALPHA)
            r.fill((0, 0, 0, (255 // grad) * (grad - i)))
            window.blit(r, (player.x - currentScreen.view_radius + i * gradW, player.y - currentScreen.view_radius))
            window.blit(r, (
                player.x + currentScreen.view_radius + TILE_SIZE - i * gradW, player.y - currentScreen.view_radius))

        if spacedCounter < spacedCounterMax:
            spacedCounter += 1
            draw_opacity_rect((0, 0, 0, 127), TILE_SIZE, 4, player.x, player.y + TILE_SIZE)
            draw_opacity_rect((0, 255, 0, 127), TILE_SIZE * spacedCounter / spacedCounterMax, 4, player.x,
                              player.y + TILE_SIZE)
        # Gui element
        font = pg.font.SysFont("arial", 16)
        lvltext = font.render("Level: " + str(currentScreen.lvl), True, (0, 0, 255))
        draw_opacity_rect((0, 0, 0, 128), lvltext.get_rect().width, lvltext.get_rect().height, 0, 0)
        window.blit(lvltext, (0, 0))

        isgameover = False
        for e in entities:
            if e.x == player.x and e.y == player.y and isinstance(e, Enemy):
                isgameover = True
        if isgameover:
            entity_clear()
            currentScreen = ScreenGameOver({"lvl": currentScreen.lvl})  # game over
            currentScreen.init()
            continue
        if player.x == currentScreen.endloc.get("x") and player.y == currentScreen.endloc.get("y"):
            entity_reset()
            if endless or currentScreen.lvl < 8:
                currentScreen = ScreenLevel(currentScreen.lvl + 1,
                                            min(currentScreen.ww + 32, pg.display.get_desktop_sizes()[0][0]),
                                            min(currentScreen.wh + 32, pg.display.get_desktop_sizes()[0][1]),
                                            max(currentScreen.view_radius / TILE_SIZE - 1, 3))
            else:
                currentScreen = ScreenGG()
            currentScreen.init()
    pg.display.update()
pg.quit()
