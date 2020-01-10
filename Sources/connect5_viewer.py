import math

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


class Connect5Viewer:
    def __init__(self, name: str, size: int, block_size: int, padding: int):
        self.name = name
        self.size = size - 1

        self.padding = padding
        self.block_size = block_size
        self.stone_size = 0.4 * block_size
        self.stone_vertex_size = 360
        self.origin_ortho_width = padding + (self.size * block_size) / 2
        self.origin_ortho_height = padding + (self.size * block_size) / 2

        self.left_bottom_y = -self.origin_ortho_height + padding
        self.left_bottom_x = -self.origin_ortho_width + padding

        self.origin_window_width = 1000
        self.origin_window_height = 1000

        self.loop_flag = True

        self.history = []

    def show(self, main_loop=None):
        glutInit()

        glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
        glutInitWindowSize(self.origin_window_width, self.origin_window_height)
        glutCreateWindow(self.name)
        glClearColor(220 / 255, 179 / 255, 92 / 255, 1)
        glOrtho(-self.origin_ortho_width, self.origin_ortho_width, -
                self.origin_ortho_height, self.origin_ortho_height, -1.0, 1.0)
        glutDisplayFunc(self.display)
        glutReshapeFunc(self.reshapce)

        while self.loop_flag:
            glutMainLoopEvent()
            if main_loop:
                main_loop()

    def update_history(self, history: list):
        self.history = history
        self.display()

    def reshapce(self, width, height):
        size = min(width, height)

        diff_height = height - size
        diff_width = width - size

        glViewport(diff_width // 2, diff_height // 2, size, size)

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glPolygonMode(GL_FRONT, GL_FILL)
        glPolygonMode(GL_BACK, GL_LINE)
        glColor3f(0.0, 0.0, 0.0)

        for y in range(0, self.size * self.block_size, self.block_size):
            for x in range(0, self.size * self.block_size, self.block_size):
                glBegin(GL_POLYGON)
                glVertex3f(self.left_bottom_x + x,
                           self.left_bottom_y + self.block_size + y, 0)
                glVertex3f(self.left_bottom_x + self.block_size + x,
                           self.left_bottom_y + self.block_size + y, 0)
                glVertex3f(self.left_bottom_x + self.block_size +
                           x, self.left_bottom_y + y, 0)
                glVertex3f(self.left_bottom_x + x, self.left_bottom_y + y, 0)
                glEnd()

        for idx, hist in enumerate(self.history):
            if hist['color'] == "black":
                glColor3f(0, 0, 0)
            elif hist['color'] == "white":
                glColor3f(1, 1, 1)
            else:
                print('Invalid Color.')
                glColor3f(1, 0, 0)

            glBegin(GL_POLYGON)

            center_x = self.left_bottom_x + \
                int(hist['x']) * self.block_size + \
                self.padding - self.block_size / 2
            center_y = self.left_bottom_y + \
                int(hist['y']) * self.block_size + \
                self.padding - self.block_size / 2

            for vertex in range(self.stone_vertex_size):
                rad = 2 * math.pi * vertex / self.stone_vertex_size - self.block_size / 2
                glVertex3f(self.stone_size * math.cos(rad) + center_x,
                           self.stone_size * math.sin(rad) + center_y, 0)

            glEnd()

            s = str(idx)
            if hist['color'] == 'black':
                glColor3f(1., 1., 1.)
            else:
                glColor3f(0., 0., 0.)
            glPushMatrix()
            glRasterPos(center_x - self.stone_size / 4,
                        center_y - self.stone_size / 4)
            for ch in s:
                glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24,
                                    ctypes.c_int(ord(ch)))

            glPopMatrix()

        glFlush()


if __name__ == '__main__':
    Connect5Viewer('hello', 15, 10, 5).show()
