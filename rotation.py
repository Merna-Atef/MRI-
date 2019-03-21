import numpy as np
from math import sin, cos, pi


def rotateX(matrix, cosFA, sinFA):
    shape = np.shape(matrix)
    rows = shape[0]
    cols = shape[1]
    #angle = (angle) * (pi / 180)
    newMatrix = np.zeros(shape)
    for i in range(0, rows):
        for j in range(0, cols):
            newMatrix[i, j] = np.dot(
                np.array([[1, 0, 0], [0, cosFA, -1 * sinFA], [0, sinFA, cosFA]]), matrix[i, j])
    return newMatrix


def rotateZ(matrix, angle):
    shape = np.shape(matrix)
    rows = shape[0]
    cols = shape[1]
    angle = (angle) * (pi / 180)
    newMatrix = np.zeros(shape)
    for i in range(0, rows):
        for j in range(0, cols):
            newMatrix[i, j] = np.dot(
                np.array([[cos(angle), -1 * sin(angle), 0], [sin(angle), cos(angle), 0], [0, 0, 1]]), matrix[i, j])
    return newMatrix


def gradientXY(matrix, stepY, stepX):
    shape = np.shape(matrix)
    rows = shape[0]
    cols = shape[1]
    newMatrix = np.zeros(shape)
    for i in range(0, rows):
        for j in range(0, cols):
            angle = stepY * j + stepX * i
            angle = (angle) * (pi / 180)
            newMatrix[i, j] = np.dot(
                np.array([[cos(angle), -1 * sin(angle), 0], [sin(angle), cos(angle), 0], [0, 0, 1]]), matrix[i, j])
    return newMatrix
