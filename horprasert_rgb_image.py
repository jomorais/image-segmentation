from scipy import misc
import numpy as np
import matplotlib.pyplot as plt

__author__ = 'jmorais'

N_FRAMES_BG = 64

ALFA_RMS_MIN = 0.01
CD_RMS_MIN = 0.01

HIST_CD_MAX = 10
HIST_ALFA_MAX = 20
GRID = 0.01
N_FRAMES_HIST = 10
F_INI_HIST = 30

N_PTS_H_CD = HIST_CD_MAX / GRID
N_PTS_H_ALFA = HIST_ALFA_MAX / GRID
F_END_HIST = F_INI_HIST + N_FRAMES_HIST - 1

TAXA_DE_ERRO = 0.1
SAMPLES_OUT = (320 * 240 * N_FRAMES_HIST * TAXA_DE_ERRO) / 100

G_ALFA_MIN = 0.2
G_ALFA_MAX = 0.7

RES_HOR = 240
RES_VERT = 320

estatistica = [0, 0, 0, 0, 0]
numero_quadros = 0
tempo_processamento = 0

t_CD = 4.5

i_soma = 0
for i in range(1, N_FRAMES_BG + 1):
    i_atual = misc.imread('images/image{}.bmp'.format(i))
    i_soma += i_atual.astype(np.double)
i_media = i_soma / N_FRAMES_BG

s_num_desvio = np.zeros((240, 320, 3), dtype=np.double)
for i in range(1, N_FRAMES_BG + 1):
    i_atual = misc.imread('images/image{}.bmp'.format(i))
    s_num_desvio += np.power(i_atual.astype(np.double) - i_media, 2)
desvio_padrao = np.sqrt(s_num_desvio / (N_FRAMES_BG - 1))

d_p_r = np.mean(desvio_padrao[..., 0], dtype=np.double)
d_p_g = np.mean(desvio_padrao[..., 1], dtype=np.double)
d_p_b = np.mean(desvio_padrao[..., 2], dtype=np.double)

print 'Desvio padrao'

d_p_qr = np.power(d_p_r, 2)
d_p_qg = np.power(d_p_g, 2)
d_p_qb = np.power(d_p_b, 2)

m_q = np.power(i_media, 2)

den = (m_q[..., 0] / d_p_qr) + (m_q[..., 1] / d_p_qg) + (m_q[..., 2] / d_p_qb)

alfa_s = np.zeros((240, 320), dtype=np.double)

CD_s = np.zeros((240, 320), dtype=np.double)

for i in range(1, N_FRAMES_BG + 1):
    i_atual = misc.imread('images/image{}.bmp'.format(i)).astype(np.double)

    d_n = np.empty_like(i_atual)
    d_n[:, :, 0] = (i_atual[:, :, 0] * i_media[:, :, 0]) / d_p_qr
    d_n[:, :, 1] = (i_atual[:, :, 1] * i_media[:, :, 1]) / d_p_qg
    d_n[:, :, 2] = (i_atual[:, :, 2] * i_media[:, :, 2]) / d_p_qb

    num = d_n[:, :, 0] + d_n[:, :, 1] + d_n[:, :, 2]

    alfa = num / den

    alfa_s += np.fix(np.power(alfa - 1, 2))

    CDr = np.power(i_atual[:, :, 0] - (alfa * i_media[:, :, 0]), 2)
    CDg = np.power(i_atual[:, :, 1] - (alfa * i_media[:, :, 1]), 2)
    CDb = np.power(i_atual[:, :, 2] - (alfa * i_media[:, :, 2]), 2)

    CD = np.sqrt((CDr / d_p_qr) + (CDg / d_p_qg) + (CDb / d_p_qb))

    CD_s += np.power(CD, 2)

alfa_rms = np.fix(np.sqrt(np.fix(alfa_s / N_FRAMES_BG)))

CD_rms = np.sqrt(CD_s / N_FRAMES_BG)

alfa_rms[alfa_rms < ALFA_RMS_MIN] = ALFA_RMS_MIN
CD_rms[CD_rms < CD_RMS_MIN] = CD_RMS_MIN

N_FRAMES_BG = 207

for i in range(201, N_FRAMES_BG + 1):
    im_ref = misc.imread('images/imageref{}.bmp'.format(i)).astype(np.double)
    im_ref = np.fix(im_ref * 255)
    im_ref = im_ref[..., 0]
    frame = misc.imread('images/image{}.bmp'.format(i))
    im_teste = frame.astype(np.double)

    im_teste_r1 = im_teste[:, :, 0]
    im_teste_g1 = im_teste[:, :, 1]
    im_teste_b1 = im_teste[:, :, 2]

    im_teste_r = im_teste[:, :, 0]
    im_teste_g = im_teste[:, :, 1]
    im_teste_b = im_teste[:, :, 2]

    imagem_atual = im_teste

    d_n = np.empty_like(imagem_atual)
    d_n[:, :, 0] = (imagem_atual[:, :, 0] * i_media[:, :, 0]) / d_p_qr
    d_n[:, :, 1] = (imagem_atual[:, :, 1] * i_media[:, :, 1]) / d_p_qg
    d_n[:, :, 2] = (imagem_atual[:, :, 2] * i_media[:, :, 2]) / d_p_qb

    num = d_n[:, :, 0] + d_n[:, :, 1] + d_n[:, :, 2]
    alfa = num / den

    alfa_n = (alfa - 1) / alfa_rms

    CDr = np.power((imagem_atual[:, :, 0] - (alfa * i_media[:, :, 0])), 2)
    CDg = np.power((imagem_atual[:, :, 1] - (alfa * i_media[:, :, 1])), 2)
    CDb = np.power((imagem_atual[:, :, 2] - (alfa * i_media[:, :, 2])), 2)
    CD = np.sqrt((CDr / d_p_qr) + (CDg / d_p_qg) + (CDb / d_p_qb))
    CD_norm = CD / CD_rms

    objeto1 = np.where(CD_norm > t_CD)

    im_teste_f = np.zeros((RES_HOR, RES_VERT), dtype=np.double)
    im_teste_f[objeto1] = 1

    alfa_lim = np.where(alfa < G_ALFA_MIN)
    alfa_lim1 = np.where(alfa > G_ALFA_MAX)

    imfinal = np.zeros((RES_HOR, RES_VERT, 3), dtype=np.double)
    imfinal_r = np.zeros((RES_HOR, RES_VERT), dtype=np.double)
    imfinal_g = np.zeros((RES_HOR, RES_VERT), dtype=np.double)
    imfinal_b = np.zeros((RES_HOR, RES_VERT), dtype=np.double)

    im_teste_r = im_teste_r.astype(np.uint8)
    im_teste_g = im_teste_g.astype(np.uint8)
    im_teste_b = im_teste_b.astype(np.uint8)

    imfinal_r[objeto1] = im_teste_r[objeto1]
    imfinal_g[objeto1] = im_teste_g[objeto1]
    imfinal_b[objeto1] = im_teste_b[objeto1]

    imfinal[:, :, 0] = imfinal_r
    imfinal[:, :, 1] = imfinal_g
    imfinal[:, :, 2] = imfinal_b

    imtestefinal = [frame, imfinal]

    plt.subplot(121)
    plt.imshow(frame)
    plt.subplot(122)
    plt.imshow(imfinal)
    plt.show()
