
import math
import sys
import time
import pygame

# Config
WIDTH, HEIGHT = 960, 540
FPS = 60
BITE_AT = 1.4
FADE_AT = 2.0
END_AT = 2.4
BG_TOP = (5, 30, 60)
BG_BOTTOM = (0, 0, 0)

def lerp(a, b, t):
    return a + (b - a) * t

def draw_bg(screen):
    # simple vertical gradient
    for y in range(HEIGHT):
        t = y / max(HEIGHT-1, 1)
        r = int(lerp(BG_TOP[0], BG_BOTTOM[0], t))
        g = int(lerp(BG_TOP[1], BG_BOTTOM[1], t))
        b = int(lerp(BG_TOP[2], BG_BOTTOM[2], t))
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

def draw_tire(surf, cx, cy, outer_r=90, thickness=32, ring_color=(17,24,39), rim_color=(31,41,55)):
    # outer ring
    pygame.draw.circle(surf, ring_color, (int(cx), int(cy)), outer_r, thickness)
    # rim
    pygame.draw.circle(surf, rim_color, (int(cx), int(cy)), max(outer_r - thickness - 6, 6))
    # lugs
    lug_r = max(outer_r - thickness - 12, 4)
    for i in range(5):
        ang = math.radians(i * 72)
        x = cx + lug_r * math.cos(ang)
        y = cy + lug_r * math.sin(ang)
        pygame.draw.circle(surf, (14,165,233), (int(x), int(y)), 4)

def cut_bite(surf, cx, cy, angle_deg, radius=30):
    ang = math.radians(angle_deg)
    x = cx + 60 * math.cos(ang)
    y = cy + 60 * math.sin(ang)
    pygame.draw.circle(surf, (0,0,0), (int(x), int(y)), radius)

def shark_polys(x, y, mouth_open, color_body=(30,41,59), color_mouth=(11,18,32)):
    # returns list of (color, pointlist)
    body = [
        (x, y+20),
        (x+200, y-20),
        (x+260, y-6),
        (x+210, y+10),
        (x+200, y+50),
        (x, y+40),
    ]
    jaw_rot = 14 if mouth_open else 0
    # upper jaw
    uj = [(0,0),(88,-28),(120,-12),(28,8)]
    # lower jaw
    lj = [(0,0),(28,12),(120,0),(88,24)]
    # rotate around (x+170,y+38)
    ox, oy = x+170, y+38
    def rot_pts(pts, deg):
        a = math.radians(deg)
        ca, sa = math.cos(a), math.sin(a)
        out = []
        for px,py in pts:
            rx = px*ca - py*sa
            ry = px*sa + py*ca
            out.append((ox+rx, oy+ry))
        return out
    uj_pts = rot_pts(uj, -jaw_rot)
    lj_pts = rot_pts(lj, jaw_rot)
    return [
        ((30,41,59), body),
        (color_mouth, uj_pts),
        (color_mouth, lj_pts),
        ((14,165,233), [(x+170, y+15, 6)])  # eye as circle (use special-case)
    ]

def draw_shark(screen, x, y, mouth_open):
    polys = shark_polys(x, y, mouth_open)
    for color, pts in polys[:-1]:
        pygame.draw.polygon(screen, color, pts)
    eye = polys[-1][1][0]
    pygame.draw.circle(screen, (14,165,233), (int(eye[0]), int(eye[1])), int(eye[2]))

def draw_label(screen):
    font = pygame.font.SysFont("Arial", 24, bold=True)
    small = pygame.font.SysFont("Arial", 14)
    text = font.render("Tire Shark", True, (230, 230, 240))
    sub = small.render("Loading...", True, (180, 190, 200))
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT - 80))
    screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT - 52))

def main():
    pygame.init()
    pygame.display.set_caption("Tire Shark - Startup Animation (Python)")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    start = time.perf_counter()

    tire_center = (WIDTH//2 + 40, HEIGHT//2)
    shark_x = -320
    shark_y = HEIGHT//2 - 80

    done = False
    bitten = False
    fade_alpha = 0

    # pre-make a surface for tire so we can cut bite
    tire_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        t = time.perf_counter() - start

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        progress = min(t / BITE_AT, 1.0)
        shark_x = lerp(-320, tire_center[0] - 280, progress)

        if not bitten and t >= BITE_AT:
            bitten = True

        draw_bg(screen)

        # floating tire
        float_y = math.sin(t * 2.8) * 6.0
        tire_surf.fill((0,0,0,0))
        draw_tire(tire_surf, tire_center[0], tire_center[1] + float_y)
        if bitten:
            cut_bite(tire_surf, tire_center[0], tire_center[1] + float_y, angle_deg=0, radius=32)
        screen.blit(tire_surf, (0,0))

        # shark
        mouth_open = not bitten
        draw_shark(screen, shark_x, shark_y, mouth_open)

        # label
        draw_label(screen)

        # fade
        if t >= FADE_AT:
            k = min((t - FADE_AT) / max(END_AT-FADE_AT, 0.0001), 1.0)
            fade_alpha = int(255 * k)
            fade_surface = pygame.Surface((WIDTH, HEIGHT))
            fade_surface.set_alpha(fade_alpha)
            fade_surface.fill((0,0,0))
            screen.blit(fade_surface, (0,0))

        pygame.display.flip()

        if t >= END_AT:
            done = True
            running = False

    pygame.quit()
    if done:
        sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
