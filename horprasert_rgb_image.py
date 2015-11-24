from scipy import misc
import numpy as np
__author__ = 'jmorais'

N_FRAMES_BG = 64


i_soma = 0
for i in range(N_FRAMES_BG):
    i_atual = misc.imread('/home/asoares/pos_uea/TrabalhoFinal/IMAGENS DE TESTE/image{}.bmp'.format(i))
    i_soma += i_atual.astype(float)
i_media = i_soma/N_FRAMES_BG
print i_media

s_num_desvio = 0
for i in range(N_FRAMES_BG):
    i_atual = misc.imread('/home/asoares/pos_uea/TrabalhoFinal/IMAGENS DE TESTE/image{}.bmp'.format(i))
    s_num_desvio += np.power(i_atual - i_media, 2)
desvio_padrao = np.sqrt(s_num_desvio/(N_FRAMES_BG - 1))
print 'Desvio padrao'
print desvio_padrao