import matplotlib.pyplot as plt
import json
import math
import numpy as np
import soundfile as sf


def getFrequencies(data, samplerate, activation = 10):
    fourierList = np.fft.rfft(data)
    fourierLen = len(fourierList)
    frequencies = []
    amplitudes = []
    maxAmp = 0
    maxFreq = 0
    localMaxFreqs = []
    localMaxFreq = 300.0
    localMinAmp = 1
    localMaxAmp = 1
    increaseStep = abs(fourierList[0]) < activation
    i = 150  # Min = 300 Hz
    while i < fourierLen and i < 1500:  # Max = 3000 Hz
        frequency = i * samplerate / fourierLen / 2
        amplitude = abs(fourierList[i])
        if increaseStep:
            if amplitude > localMaxAmp:
                localMaxAmp = amplitude
                localMaxFreq = frequency
            else:
                localMinAmp = amplitude
                if amplitude < localMaxAmp / 10:
                    if localMaxAmp > activation:
                        localMaxFreqs.append(localMaxFreq)
                    increaseStep = False
        else:
            if amplitude < localMinAmp:
                localMinAmp = amplitude
            else:
                localMaxAmp = amplitude
                if amplitude > localMinAmp * 10:
                    increaseStep = True
        frequencies.append(frequency)
        amplitudes.append(amplitude)
        i += 1
    # print(localMaxFreqs)
    # plt.plot(frequencies, amplitudes)
    # plt.show()
    return(frequencies, amplitudes, localMaxFreqs, maxFreq, maxAmp)


def getMaxFrequency(data, samplerate):
    fourierList = np.fft.rfft(data)
    fourierLen = len(fourierList)
    maxAmp = 0
    maxFreq = 0
    i = 150  # Min = 300 Hz
    while i < fourierLen and i < 1500:  # Max = 3000 Hz
        frequency = i * samplerate / fourierLen / 2
        amplitude = abs(fourierList[i])
        if amplitude > maxAmp:
            maxAmp = amplitude
            maxFreq = frequency
        i += 1
    return(maxFreq, maxAmp)


def cropAudio(data, samplerate):
    frameSize = math.floor(samplerate / 16)
    audio = [0] * frameSize + data + [0] * frameSize
    #print(audio)
    cropStart = 0
    cropEnd = len(audio) - 1
    ### Find extra left
    startPosition = 0
    endPosition = frameSize
    lastFullStart = 0
    while True:
        datapart = audio[startPosition:endPosition]
        maxFreq, maxAmp = getMaxFrequency(datapart, samplerate)
        if maxAmp < 0.5:
            lastFullStart = startPosition
        else:
            break
        startPosition = endPosition
        endPosition += frameSize
    leftPosition = lastFullStart + frameSize
    centerPosition = lastFullStart + math.floor(frameSize / 2)
    rightPosition = lastFullStart + 2 * frameSize
    delta = frameSize
    while delta > math.ceil(samplerate / 1024):
        datapart = audio[lastFullStart:centerPosition]
        maxFreq, maxAmp = getMaxFrequency(datapart, samplerate)
        if maxAmp < 0.5:
            leftPosition = centerPosition
        else:
            rightPosition = centerPosition
        centerPosition = math.floor((leftPosition + rightPosition) / 2)
        delta = rightPosition - leftPosition
    cropStart = math.floor(centerPosition)
    ### Find extra right
    startPosition = len(audio) - 1
    endPosition = startPosition - frameSize
    lastFullStart = startPosition
    while True:
        datapart = audio[endPosition:startPosition]
        maxFreq, maxAmp = getMaxFrequency(datapart, samplerate)
        if maxAmp < 0.5:
            lastFullStart = startPosition
        else:
            break
        startPosition = endPosition
        endPosition -= frameSize
    rightPosition = lastFullStart - frameSize
    centerPosition = lastFullStart - math.floor(frameSize / 2)
    leftPosition = lastFullStart - 2 * frameSize
    delta = frameSize
    while delta > math.ceil(samplerate / 1024):
        datapart = audio[centerPosition:lastFullStart]
        maxFreq, maxAmp = getMaxFrequency(datapart, samplerate)
        if maxAmp < 0.5:
            rightPosition = centerPosition
        else:
            leftPosition = centerPosition
        centerPosition = math.floor((leftPosition + rightPosition) / 2)
        delta = rightPosition - leftPosition
    cropEnd = math.ceil(centerPosition)
    ### Crop
    return audio[cropStart:cropEnd]

def getLeftAudio(filename):
    data, samplerate = sf.read(filename)
    datalen = len(data)
    left = []
    i = 0
    while i < datalen:
        left.append(data[i][0])
        i += 1
    data = left
    return(data, datalen, samplerate)

def getAudioDigest(filename, activation):
    data, datalen, samplerate = getLeftAudio(filename)
    data = cropAudio(data, samplerate)
    datalen = len(data)
    if(datalen < samplerate / 2):
        print("Part too short")
        return None
    frameSize = math.floor(samplerate / 2 - 1)
    frameInterval = math.floor((datalen - frameSize) / 15) # for 16 frames
    startPosition = 0
    endPosition = frameSize
    digest = []
    i = 0
    while i < 16:
        datapart = data[startPosition:endPosition]
        frequencies, amplitudes, localMaxFreqs, maxFreq, maxAmp = getFrequencies(datapart, samplerate, activation)
        startPosition += frameInterval
        endPosition += frameInterval
        i += 1
        digest.append(localMaxFreqs)
    return digest

def getRMS(digest1, digest2):
    rms = 0.0
    count = 0
    i = 0
    while i < len(digest1):
        # plt.plot(digest1[i], 'b', digest2[i], 'r')
        # plt.show()
        # print(digest1[i], digest2[i])
        j = 0
        while j < len(digest1[i]):
            if digest1[i][j] < 350:
                j += 1
                continue
            k = 0
            freq = 300.0
            minDiff = 80.0
            while k < len(digest2[i]):
                diff = abs(digest1[i][j] - digest2[i][k])
                if diff < minDiff:
                    minDiff = diff
                k += 1
            rms += math.pow(minDiff, 2)
            count += len(digest1[i])
            j += 1
        i += 1
    rms /= count
    print(rms)
    return rms

def compare(obj):
    digestA = getAudioDigest(obj['a'], 5)
    if digestA == None:
        return None
    best = None
    minRMS = 8192
    tolerance = obj['t']
    i = 0
    while i < len(obj['l']):
        digestL = getAudioDigest(obj['l'][i], 10)
        if digestL == None:
            i += 1
            continue
        rms = getRMS(digestL, digestA)
        if rms <= tolerance and rms < minRMS:
            best = obj['l'][i]
            minRMS = rms
        i += 1
    return { 'best': best, 'rms': minRMS }

while True:
    lst = input()
    if lst == 'q':
        break
    obj = json.loads(lst)
    cmpr = compare(obj)
    print(json.dumps(cmpr))

