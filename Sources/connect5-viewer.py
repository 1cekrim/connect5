import math

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


class Connect5Viewer:
    def __init__(self, name: str, size: int, block_size: int, padding: int):
        self.name = name
        self.size = size

        self.padding = padding
        self.block_size = block_size
        self.stone_size = 0.4 * block_size
        self.stone_vertex_size = 360
        self.origin_ortho_width = padding + (size * block_size) / 2
        self.origin_ortho_height = padding + (size * block_size) / 2

        self.left_bottom_y = -self.origin_ortho_height + padding
        self.left_bottom_x = -self.origin_ortho_width + padding

        self.origin_window_width = 500
        self.origin_window_height = 500

        self.history = []

        glutInit()

        glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
        glutInitWindowSize(self.origin_window_width, self.origin_window_height)
        glutCreateWindow(name)
        glClearColor(220 / 255, 179 / 255, 92 / 255, 1)
        glOrtho(-self.origin_ortho_width, self.origin_ortho_width, -
                self.origin_ortho_height, self.origin_ortho_height, -1.0, 1.0)
        glutDisplayFunc(self.display)
        glutReshapeFunc(self.reshapce)
        glutMainLoop()

    def update_history(self, history: list):
        self.history = history

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

        for hist in self.history:
            if hist['color'] is "black":
                glColor3f(0, 0, 0)
            elif hist['color'] is "white":
                glColor3f(1, 1, 1)
            else:
                print('Invalid Color.')
                glColor3f(1, 0, 0)

            glBegin(GL_POLYGON)

            for vertex in range(self.stone_vertex_size):
                rad = 2 * math.pi * vertex / self.stone_vertex_size
                glVertex3f(self.left_bottom_x + int(hist['x']) * self.block_size + self.padding + self.stone_size *
                           math.cos(rad) - self.block_size / 2, self.left_bottom_y + int(hist['y']) * self.block_size + self.padding + self.stone_size * math.sin(rad) - self.block_size / 2, 0)

            glEnd()

        glFlush()


if __name__ == '__main__':
    Connect5Viewer('hello', 15, 10, 5)
