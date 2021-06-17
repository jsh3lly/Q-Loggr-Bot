def splitQueueFile(queueFileText):      # Returns listOfListOfTrackInfo
    listOfAllTracks = queueFileText.split("\n")
    listOfListOfTrackInfo = []
    for track in listOfAllTracks:
        serialNumberAndRemainingList = track.strip().split(")",1)
        serialNumber = serialNumberAndRemainingList[0]
        remaining = serialNumberAndRemainingList[1]
        print(remaining)
        artistAndSongANDTime = remaining.strip().rsplit(" ",1)
        artistAndSong = artistAndSongANDTime[0]
        time = artistAndSongANDTime[1]
        trackInfoList = [serialNumber, artistAndSong, time]         # important
        listOfListOfTrackInfo.append(trackInfoList)

    return listOfListOfTrackInfo



# a = splitQueueFile("""1) Lynyrd Skynyrd - Free Bird       5:45
# 2) Tom Petty - Runnin' Down A Dream 4:23""")
#
# print(a)

