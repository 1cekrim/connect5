from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


class Connect5Viewer:
    def __init__(self, name: str, size: int, block_size: int, padding: int):
        self.name = name
        self.size = size

        self.padding = padding
        self.block_size = block_size
        self.origin_ortho_width = padding + (size * block_size) / 2
        self.origin_ortho_height = padding + (size * block_size) / 2

        self.left_bottom_y = -self.origin_ortho_height + padding
        self.left_botton_x = -self.origin_ortho_width + padding

        self.origin_window_width = 500
        self.origin_window_height = 500

        glutInit()
        glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
        glutInitWindowSize(self.origin_window_width, self.origin_window_height)
        glutCreateWindow(name)
        glClearColor(220 / 255, 179 / 255, 92 / 255, 1)
        print(self.origin_ortho_height, self.origin_ortho_width)
        glOrtho(-self.origin_ortho_width, self.origin_ortho_width, -
                self.origin_ortho_height, self.origin_ortho_height, -1.0, 1.0)
        glutDisplayFunc(self.display)
        glutReshapeFunc(self.reshapce)
        glutMainLoop()

    def reshapce(self, width, height):
        size = min(width, height)

        diff_height = height - size
        diff_width = width - size

        glViewport(diff_width // 2, diff_height // 2, size, size)

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glColor3f(0.0, 0.0, 0.0)

        for y in range(0, self.size * self.block_size, self.block_size):
            for x in range(0, self.size * self.block_size, self.block_size):
                glBegin(GL_POLYGON)
                glVertex3f(self.left_botton_x + x, self.left_bottom_y + y, 0)
                glVertex3f(self.left_botton_x + self.block_size +
                           x, self.left_bottom_y + y, 0)
                glVertex3f(self.left_botton_x + self.block_size + x,
                           self.left_bottom_y + self.block_size + y, 0)
                glVertex3f(self.left_botton_x + x,
                           self.left_bottom_y + self.block_size + y, 0)
                glEnd()
        glFlush()


if __name__ == '__main__':
    Connect5Viewer('hello', 15, 10, 5)
