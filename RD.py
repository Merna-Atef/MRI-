import numpy as np


def decay(matrix, T2, t = 1):
    rows = matrix.shape[0]
    cols = matrix.shape[1]
    for i in range(0, rows):
        for j in range(0, cols):
            exp = np.array([ [np.exp(-t/(T2[i][j])),  0, 0],
                            [0, np.exp(-t/(T2[i][j])),  0],
                            [0,        0,               1] ])
            decayedMat = exp.dot(matrix[i][j])
    return decayedMat

def recovery(matrix, T1, t = 1):
    rows = matrix.shape[0]
    cols = matrix.shape[1]
    for i in range(0, rows):
        for j in range(0, cols):
            exp = np.array([ [1 ,  0, 0],
                            [0,    1,  0],
                            [0,    0,   np.exp(-t/(T1[i][j]))] ])
            recoveryMat = exp.dot(matrix[i][j]) + np.array([0, 0, 1 - np.exp(-t/(T1[i][j]))])
    return recoveryMat

    
