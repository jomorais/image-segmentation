__author__ = 'nilson'

import numpy as np
import cv2
import multiprocessing
from multiprocessing import Pool
import time
import threading
import os
import sys

cap = cv2.VideoCapture(0)
RES_HOR = 240
RES_VERT = 320
ret = cap.set(3, RES_VERT)
ret = cap.set(4, RES_HOR)

#RES_HOR = 480
#RES_VERT = 640

N_FRAMES_BG = 16

ALFA_RMS_MIN = 0.001
CD_RMS_MIN = 0.001

HIST_CD_MAX = 10
HIST_ALFA_MAX = 20
GRID = 0.01
N_FRAMES_HIST = 10
F_INI_HIST = 30

N_PTS_H_CD = HIST_CD_MAX / GRID
N_PTS_H_ALFA = HIST_ALFA_MAX / GRID
F_END_HIST = F_INI_HIST + N_FRAMES_HIST - 1

R = 0
G = 1
B = 2

TAXA_DE_ERRO = 0.1
SAMPLES_OUT = (RES_VERT * RES_HOR * N_FRAMES_HIST * TAXA_DE_ERRO) / 100

G_ALFA_MIN = 0.2
G_ALFA_MAX = 0.7


estatistica = [0, 0, 0, 0, 0]
numero_quadros = 0
tempo_processamento = 0

t_CD = 3.5
t_alfa = -150

main_process_poison_pill = False


def segment_image(free_worker_queue, new_frames_queue, processed_frames_queue, i_media, d_p_qr, d_p_qg, d_p_qb, den, alfa_rms, CD_rms):
    pid = os.getpid()
    while True:
        t1 = time.time()
        free_worker_queue.put(pid)
        im_teste = new_frames_queue.get()

        if im_teste[0, 0][0] < 0:
            #poison pill taken..
            break

        im_teste_r = im_teste[:, :, R]
        im_teste_g = im_teste[:, :, G]
        im_teste_b = im_teste[:, :, B]

        imagem_atual = im_teste

        d_n = np.empty_like(imagem_atual)
        d_n[:, :, R] = (imagem_atual[:, :, R] * i_media[:, :, R]) / d_p_qr
        d_n[:, :, G] = (imagem_atual[:, :, G] * i_media[:, :, G]) / d_p_qg
        d_n[:, :, B] = (imagem_atual[:, :, B] * i_media[:, :, B]) / d_p_qb

        num = d_n[:, :, R] + d_n[:, :, G] + d_n[:, :, B]
        alfa = num / den

        alfa_n = (alfa - 1) / alfa_rms

        CDr = np.power((imagem_atual[:, :, R] - (alfa * i_media[:, :, R])), 2)
        CDg = np.power((imagem_atual[:, :, G] - (alfa * i_media[:, :, G])), 2)
        CDb = np.power((imagem_atual[:, :, B] - (alfa * i_media[:, :, B])), 2)
        CD = np.sqrt((CDr / d_p_qr) + (CDg / d_p_qg) + (CDb / d_p_qb))
        CD_norm = CD / CD_rms

        #mapeamento do objeto
        objeto1 = np.where((CD_norm > t_CD) | (alfa_n < t_alfa))
        #objeto1 = np.where((alfa_n < t_alfa))
        #objeto1 = np.where(CD_norm > t_CD)

        im_teste_f = np.zeros((RES_HOR, RES_VERT))
        #im_teste_f[objeto1] = 1

        #alfa_lim = np.where(alfa < G_ALFA_MIN)
        #alfa_lim1 = np.where(alfa > G_ALFA_MAX)

        imfinal = np.zeros((RES_HOR, RES_VERT, 3), dtype=np.uint8)

        imfinal_r = np.zeros((RES_HOR, RES_VERT), dtype=np.uint8)
        imfinal_g = np.zeros((RES_HOR, RES_VERT), dtype=np.uint8)
        imfinal_b = np.zeros((RES_HOR, RES_VERT), dtype=np.uint8)

        im_teste_r = im_teste_r.astype(np.uint8)
        im_teste_g = im_teste_g.astype(np.uint8)
        im_teste_b = im_teste_b.astype(np.uint8)

        imfinal_r[objeto1] = im_teste_r[objeto1]
        imfinal_g[objeto1] = im_teste_g[objeto1]
        imfinal_b[objeto1] = im_teste_b[objeto1]

        imfinal[:, :, R] = imfinal_r
        imfinal[:, :, G] = imfinal_g
        imfinal[:, :, B] = imfinal_b

        processed_frames_queue.put(imfinal)
        print 'pid: {}, t_calc: {}'.format(pid, time.time() - t1)
    print 'pid: {} exitting..'.format(pid)


def feed_new_frames(number_of_processes, new_frames_queue, free_worker_queue):
    first_time = True
    count_delay = 0
    delay = 1/number_of_processes
    while True:
        t1 = time.time()
        free_process_id = free_worker_queue.get()
        #print "feed_new_frames - process {} is free..".format(free_process_id)
        ret, frame = cap.read()
        new_frames_queue.put(frame.astype(np.float32))
        if count_delay < number_of_processes:
            delay = max(delay - (time.time() - t1), 0)
            time.sleep(delay)
            count_delay += 1
        if main_process_poison_pill:
            break
    print 'exiting feed_new_frames thread..'

if __name__ == '__main__':
    manager = multiprocessing.Manager()
    new_frames_queue = manager.Queue()
    free_worker_queue = manager.Queue()
    processed_frames_queue = manager.Queue()
    if len(sys.argv) >= 2:
        NBR_PROCESSES = int(sys.argv[1])
    else:
        print 'inform number of concurrent processes.. assuming 1'
        NBR_PROCESSES = 1

    i_soma = 0
    for i in range(1, N_FRAMES_BG + 1):
        ret, i_atual = cap.read()
        #i_atual = cv2.cvtColor(i_atual, cv2.COLOR_BGR2RGB)
        # i_atual = misc.imread('images/image{}.bmp'.format(i))
        i_soma += i_atual.astype(np.float32)
    i_media = i_soma / N_FRAMES_BG

    s_num_desvio = np.zeros((RES_HOR, RES_VERT, 3), dtype=np.double)
    for i in range(1, N_FRAMES_BG + 1):
        ret, i_atual = cap.read()
        #i_atual = cv2.cvtColor(i_atual, cv2.COLOR_BGR2RGB)
        # i_atual = misc.imread('images/image{}.bmp'.format(i))
        s_num_desvio += np.power(i_atual.astype(np.float32) - i_media, 2)
    desvio_padrao = np.sqrt(s_num_desvio / (N_FRAMES_BG - 1))

    d_p_r = np.mean(desvio_padrao[..., R], dtype=np.float32)
    d_p_g = np.mean(desvio_padrao[..., G], dtype=np.float32)
    d_p_b = np.mean(desvio_padrao[..., B], dtype=np.float32)

    print 'Desvio padrao'

    d_p_qr = np.power(d_p_r, 2) #variancia do R
    d_p_qg = np.power(d_p_g, 2) #variancia do G
    d_p_qb = np.power(d_p_b, 2) #variancia do B

    m_q = np.power(i_media, 2)

    den = (m_q[..., R] / d_p_qr) + (m_q[..., G] / d_p_qg) + (m_q[..., B] / d_p_qb)

    alfa_s = np.zeros((RES_HOR, RES_VERT), dtype=np.float32)

    CD_s = np.zeros((RES_HOR, RES_VERT), dtype=np.float32)

    for i in range(1, N_FRAMES_BG + 1):
        ret, i_atual = cap.read()
        #i_atual = cv2.cvtColor(i_atual, cv2.COLOR_BGR2RGB)
        i_atual = i_atual.astype(np.float32)
        d_n = np.empty_like(i_atual)
        d_n[:, :, R] = (i_atual[:, :, R] * i_media[:, :, R]) / d_p_qr
        d_n[:, :, G] = (i_atual[:, :, G] * i_media[:, :, G]) / d_p_qg
        d_n[:, :, B] = (i_atual[:, :, B] * i_media[:, :, B]) / d_p_qb

        num = d_n[:, :, R] + d_n[:, :, G] + d_n[:, :, B]

        alfa = num / den

        alfa_s += np.fix(np.power(alfa - 1, 2))

        CDr = np.power(i_atual[:, :, R] - (alfa * i_media[:, :, R]), 2)
        CDg = np.power(i_atual[:, :, G] - (alfa * i_media[:, :, G]), 2)
        CDb = np.power(i_atual[:, :, B] - (alfa * i_media[:, :, B]), 2)

        CD = np.sqrt((CDr / d_p_qr) + (CDg / d_p_qg) + (CDb / d_p_qb))

        CD_s += np.power(CD, 2)

    alfa_rms = np.sqrt(np.fix(alfa_s / N_FRAMES_BG))

    CD_rms = np.sqrt(CD_s / N_FRAMES_BG)

    alfa_rms[alfa_rms < ALFA_RMS_MIN] = ALFA_RMS_MIN
    CD_rms[CD_rms < CD_RMS_MIN] = CD_RMS_MIN

    print 'Aprendeu'

    thrd = threading.Thread(target=feed_new_frames,
                            args=(NBR_PROCESSES, new_frames_queue, free_worker_queue))
    thrd.start()

    pool = Pool(processes=NBR_PROCESSES)
    processes = []
    for _ in range(NBR_PROCESSES):
        p = multiprocessing.Process(target=segment_image,
                                    args=(free_worker_queue, new_frames_queue, processed_frames_queue,
                                          i_media, d_p_qr, d_p_qg, d_p_qb, den, alfa_rms, CD_rms))
        processes.append(p)
        p.start()

    while True:
        start = cv2.getTickCount()
        #cv2.imshow('Analise', cv2.cvtColor(imfinal, cv2.COLOR_RGB2BGR))
        imfinal = processed_frames_queue.get()
        cv2.imshow('Analise', imfinal)

        end = cv2.getTickCount()
        print 'mainThread - FPS: {}'.format((1/((end - start)/cv2.getTickFrequency())))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            main_process_poison_pill = True
            thrd.join()
            imfinal = imfinal.astype(np.float32)
            imfinal[0, 0][0] = -1
            print 'mainThread poison: {}'.format(imfinal[0, 0][0])
            for _ in range(NBR_PROCESSES):
                new_frames_queue.put(imfinal)
            time.sleep(0.5)
            break

    print 'main thread exitting..'
    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()