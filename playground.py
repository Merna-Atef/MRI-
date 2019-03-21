import numpy as np
from PIL import Image
from phantom import phantom
import cv2
img = cv2.imread('128.png',  cv2.IMREAD_GRAYSCALE)



img = phantom(1500)
f_img = np.fft.fft2(img)

reconstructed = np.fft.ifft2(f_img).real

f_img = np.fft.fft2(img)
reconstructed = np.fft.ifft2(f_img)


reconstructed2 = np.zeros(np.shape(img), dtype=np.complex_)

for i in range(0, np.shape(img)[0]):
    reconstructed2[:, i] = np.fft.fft(f_img[:, i])
for i in range(0, np.shape(img)[0]):
    reconstructed2[i, :] = np.fft.fft(f_img[i, :])

# reconstructed = np.abs(reconstructed)
reconstructed2 = np.abs(reconstructed2)

img1 = Image.fromarray(f_img, 'L')
img2 = Image.fromarray(reconstructed2, 'L')
img3 = Image.fromarray(img, 'L')


img1.show()
img2.show()
img3.show()
# from rotation import rotateX, rotateZ
#
# matrix = np.zeros((512, 512, 3), dtype=np.complex_)
# x = np.complex(2,3)
# print(x)
# sigmaZ = np.sum(matrix[:, :, 2])
# print(sigmaZ)
