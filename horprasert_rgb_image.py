from scipy import misc
import numpy as np
__author__ = 'jmorais'

N_FRAMES_BG = 64


i_soma = 0
for i in range(1, N_FRAMES_BG + 1):
    print i
    i_atual = misc.imread('images/image{}.bmp'.format(i))
    print i_atual.shape
    i_soma += i_atual.astype(np.double)
i_media = i_soma/(N_FRAMES_BG)

s_num_desvio = np.zeros((240, 320, 3), dtype=np.double)
for i in range(1 , N_FRAMES_BG + 1):
    i_atual = misc.imread('images/image{}.bmp'.format(i))
    s_num_desvio += np.power(i_atual.astype(np.double) - i_media, 2)
desvio_padrao = np.sqrt(s_num_desvio/(N_FRAMES_BG - 1))


d_p_r = np.mean(desvio_padrao[..., 0], dtype=np.double)
d_p_g = np.mean(desvio_padrao[..., 1], dtype=np.double)
d_p_b = np.mean(desvio_padrao[..., 2], dtype=np.double)

print 'Desvio padrao'


d_p_qr = np.power(d_p_r, 2)
d_p_qg = np.power(d_p_g, 2)
d_p_qb = np.power(d_p_b, 2)

m_q = np.power(i_media, 2)

print d_p_qr

den = (m_q[...,0]/d_p_qr) + (m_q[...,1]/d_p_qg) + (m_q[...,2]/d_p_qb)

