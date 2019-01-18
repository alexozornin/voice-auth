import matplotlib.pyplot as plt
import json
import math
import numpy as np
import soundfile as sf

def getFrequencies(data, samplerate):
    fourierList = np.fft.rfft(data)
    fourierLen = len(fourierList)
    frequencies = []
    amplitudes = []
    maxAmp = 0
    maxFreq = 0
    i = 30
    while i < fourierLen:
        frequency = i * samplerate / fourierLen / 2
        amplitude = abs(fourierList[i])
        if amplitude > maxAmp:
            maxAmp = amplitude
            maxFreq = frequency
        frequencies.append(frequency)
        amplitudes.append(amplitude)
        i += 1
    # fig, ax = plt.subplots()
    # ax.plot(frequencies, amplitudes)
    # plt.xlabel('Frequency, Hz')
    # plt.ylabel('Amplitude')
    # plt.grid(True)
    # plt.show()
    return(maxFreq, maxAmp)


left = []
right = []

data, samplerate = sf.read('aaa.wav')
print('samplerate', samplerate)

datalen = len(data)

i = 0
while i < datalen:
    left.append(data[i][0])
    right.append(data[i][1])
    i += 1


frameSize = math.floor(samplerate / 2 - 1)

frameInterval = math.floor((datalen - frameSize) / 31) # for 32 frames

startPosition = 0
endPosition = frameSize

print("Datalen", datalen)

i = 0
while i < 32:
    datapart = left[startPosition:endPosition]
    (freq, amp) = getFrequencies(datapart, samplerate)
    print(i, "Pos", startPosition, endPosition)
    print(freq)
    startPosition += frameInterval
    endPosition += frameInterval
    i += 1

# if(datalen > samplerate + 512):
#     frame = samplerate - 1
#     interval = (datalen - samplerate) // 512
#     i = 0
#     while i < 512:
#         datapart = left[i * interval : i * interval + frame]
#         frequencies = getFrequencies(datapart, samplerate, 20, 80, 1400, 4000, 8000)
#         vector += frequencies
#         i += 1

print('end')
