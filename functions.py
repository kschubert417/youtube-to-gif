# https://pytube.io/en/latest/api.html pytube documentation
# https://zulko.github.io/moviepy/ moviepy documentation
import os
import sqlite3
import hashlib as hl
import zipfile as zp
from pytube import YouTube
from datetime import datetime
from moviepy.editor import VideoFileClip
from moviepy.editor import *
# ffmpeg: video encoding
# VideoFileClip & CompositeVideoClip

# Tumblr limitations:
# https://tumblr.zendesk.com/hc/en-us/articles/231455068-Adding-Creating-GIFs
# Summary: <= 10MB, <= 540 px wide
# theme forest


# function for testing new ideas
def test():
    pass


# folder in directory where gifs and related objects will be stored
# gif & zip files
giffolder = os.path.join(os.getcwd(), "media", "output")

# video files that need to be downloaded to create gifs
vidfolder = os.path.join(os.getcwd(), "media", "videos")


# Database functions: responsible for creating/maintaining database inside
# application
# creating function to create database to manage backend aspects of the
# application


def createdb():
    """Short summary.
    Will create database that will be used to manage YouTube URLs and the name
    of the mp4 file it belongs to. This will help save resources when creating
    new gif files from a recycled YouTube link. Date and time the link was
    last used will be tracked so it can be deleted after a specified period
    of time.
    Parameters
    ----------
    con : type
        Connector to database

    Returns
    -------
    type
        Description of returned object.

    """
    con = sqlite3.connect("backend.db")
    cur = con.cursor()

    sql = ['''CREATE TABLE IF NOT EXISTS youtubemp4 (
            YouTubeLink     VARCHAR (200),
            MP4FileName     VARCHAR (200),
            LastUsed        DATETIME)''']

    for statement in sql:
        cur.execute(statement)

    con.commit()
    con.close()


def insertytlinkmp4(ytlink, filename):
    sql = '''INSERT INTO youtubemp4 (YouTubeLink, MP4FileName, LastUsed)
             VALUES (?, ?, ?)'''
    con = sqlite3.connect("backend.db")
    cur = con.cursor()

    cur.execute(sql, (ytlink, filename, datetime.utcnow()))

    con.commit()
    con.close()


# creating this to delete any file older than n hours to save space on drive
def deleteoldfiles(paths, hoursold=1):
    """Short summary.
    Function to look at MP4 files in database and see if any "stale" videos
    can be deleted that are older than N hours.
    Will also look into a provided folder and delete all files older than
    N hours
    Parameters
    ----------
    hoursold : number
        Option to delete files older than this

    Returns
    -------
    type
        Description of returned object.

    """
    print("TIME TO DELETE FILES")
    # going through folder and deleting old files
    now = datetime.now().timestamp()
    for path in paths:
        for filename in os.listdir(path):
            file = os.path.join(path, filename)
            # getting the time stamp of the file
            filestamp = os.stat(file).st_mtime
            # getting now minus the period of time I want to remove
            filecompare = now - hoursold * 60 * 60
            # removing files older than I want
            if filestamp < filecompare:
                os.remove(file)

    # going through DB now and doing the same thing
    con = sqlite3.connect("backend.db")
    cur = con.cursor()

    # sql statement to select videos older than N hours old
    sql = '''SELECT MP4FileName
             FROM youtubemp4
             WHERE(JULIANDAY() - JULIANDAY(LastUsed))*24 > '''\
                + str(hoursold)

    cur.execute(sql)

    for row in cur:
        deletesql = 'DELETE FROM youtubemp4 WHERE MP4FileName = \''\
                    + row[0] + '\''

        os.remove(row[0])
        cur.execute(deletesql)

    con.commit()
    con.close()


def ytlinkexist(ytlink):
    """Short summary.
    Function checks to see whether an MP4 file was already downloaded for
    a provided youtube link. If so, it returns the file path for the MP4
    filename the function should use to create a GIF instead of downloading
    the video from the internet again
    Parameters
    ----------
    ytlink : link
        YouTube link to check if it already exists

    Returns
    -------
    type
        File path for the MP4 video or "no data" if YouTube link was not
        already downloaded

    """

    con = sqlite3.connect("backend.db")
    cur = con.cursor()

    # checking to see if YT link already exists
    sql = '''SELECT COUNT(*), MP4FileName
             FROM youtubemp4
             WHERE YouTubeLink = \'''' + ytlink + "\'"

    cur.execute(sql)

    for row in cur:
        # if data is received COUNT(*) should be > 1
        if int(row[0]) > 0:
            print("YouTube link does exist")
            # updating LastUsed column for the link to now
            sql = '''UPDATE youtubemp4
                     SET LastUsed = DATETIME('now')
                     WHERE YouTubeLink = \'''' + ytlink + "\'"

            cur.execute(sql)

            con.commit()
            con.close()

            # returning file path for saved MP4 file to use to create GIF
            return row[1]
        else:
            print("YouTube link does not exist")
            return "no data"


def hashitup(firstpart, extension):
    """Short summary.
    This will create a unique file name with hash id based on current datetime
    to make sure duplicate file names are not created.
    Parameters
    ----------
    firstpart : string
        Define first part of the desired file name
    extension : string
        Define extension of the file. EX: ".zip" or ".gif"

    Returns
    -------
    type
        string with the file name containing hash

    """
    # getting datetime information to set hash
    dt = str(datetime.now())
    datehash = str(hl.md5(dt.encode()).hexdigest())

    filename = firstpart + "_" + datehash + extension

    return filename


def createzip(filenames):
    """Short summary.
    Creates zip file to download multiple gif files
    Parameters. This is handy for returning multiple files in a
    web browser
    Parameters
    ----------
    filenames : list
        ex: ['filname_1.gif', 'filname_2.gif', ...]
        Contains file names of gif files that need to be loaded into the
        zipfile

    directory : type
        Description of parameter `directory`.

    Returns
    -------
    type
        zipfile path containing gifs

    """
    zipfname = hashitup("gifzip", ".zip")
    zipfilepath = os.path.join(giffolder, zipfname)

    zipf = zp.ZipFile(zipfilepath, 'w', zp.ZIP_DEFLATED)
    for file in filenames:
        # using relative path or the entire contents of the project project
        # folder will be deposited into the gif file
        zipf.write(file, os.path.relpath(file, giffolder))

    zipf.close()

    return zipfilepath


def returnpath(filelist):
    """Short summary.
    Because only one file can be returned at a time this function will
    determine how many file names are sent in the list and either A) return
    one gif file, or B) return a zip file with multiple gif files
    Parameters
    ----------
    filelist : list
        List of files to be sent to the user

    Returns
    -------
    type
        GIF file or zip file containing multiple gifs

    """
    # functions that return lists have the ability to be scaled up to creating
    # multiple gif files. So: checking to see if the argument passed is a list.
    # If it is a list the length is checked, if len == 1, pass along the gif
    # file. If len > 1, create a zip file with the gif files.
    # If argument is not a list, return the gif file
    if type(filelist) is list:
        if len(filelist) == 1:
            return filelist[0]
        else:
            return createzip(filelist)
    else:
        return filelist


def onevidonegif(ytlink, start, end, speed=1):
    """Short summary.
    Function creates one gif with the provided start/end times from the
    provided YouTube link
    Parameters
    ----------
    ytlink : URL
        YouTube video link
    start : string
        Start time of gif, string format: "HH:MM:SS.MS"
    end : string
        Start time of gif, string format: "HH:MM:SS.MS"
    speed : number
        Choose for desired output speed of gif
        1 is normal, 0.5 if half speed, 2 is twice speed

    Returns
    -------
    gif file
        one gif with desired start and end times from one YouTube link

    """
    videoname = ytlinkexist(ytlink)

    if videoname == "no data":
        yt = YouTube(ytlink)

        videoname = hashitup("Video", ".mp4")
        videoname = os.path.join(vidfolder, videoname)

        # getting MP4 format video (stream) with highest resolution
        stream = yt.streams.filter(file_extension='mp4').get_highest_resolution()
        stream.download(filename=videoname)

        # inserting YouTube link and MP4 file name into database
        insertytlinkmp4(ytlink, videoname)
    else:
        pass
    # now creating the gif
    clip = VideoFileClip(videoname).subclip((start), (end)).resize(width=540)

    # adjusting speed of gif
    clip = clip.speedx(speed)

    # creating file path to save gif file
    fname = hashitup("gif", ".gif")

    filepath = os.path.join(os.getcwd(), giffolder, fname)

    clip.write_gif(filepath)

    clip.close()

    # running this to delete old files
    print("annhilation time")
    deleteoldfiles([giffolder])

    return filepath



def onegifpervid(dict, speed=1):
    """Short summary.
    Function takes the dictionary and creates one gif per video link. The link
    may have more than one start/end time so all those times are exported into
    one gif. Each link will get its own gif file


    Parameters
    ----------
    dict : dictionary of dictionary of lists. First dictionary key contains
            the link of the YouTube video, the value is another dictionary
            containing lists of the start and end times in "HH:MM:SS.MS" format

        Example:
        {YTLink1: {'start': ['00:00:00.00', '00:00:05.00'],
                   'end': ['00:00:04.59', '00:00:9.59']},
         YTLink1: {'start': ['00:00:00.00', '00:00:05.00'],
                   'end': ['00:00:04.59', '00:00:9.59']}}

    speed : number
        Choose for desired output speed of gif
        1 is normal, 0.5 if half speed, 2 is twice speed

    Returns
    -------
    filnames
        list of file names created
    gif
        One gif file per video link that is in the provided dictionary

    """

    # creating list that will contain gif file names
    fnames = []

    # setting up counter for file names
    counter = 1
    for link in dict:
        videoname = ytlinkexist(link)

        if videoname == 'no data':
            yt = YouTube(link)

            videoname = hashitup("Video", ".mp4")
            videoname = os.path.join(vidfolder, videoname)

            # getting MP4 format video (stream) with highest resolution
            stream = (yt.streams.filter(file_extension='mp4')
                        .get_highest_resolution())
            stream.download(filename=videoname)

            # inserting YouTube link and MP4 file name into database
            insertytlinkmp4(link, videoname)
        else:
            pass

        # counter for creating clips
        counter1 = 0
        for j in dict[link]['start']:
            if counter1 == 0:
                start = dict[link]['start'][counter1]
                end = dict[link]['end'][counter1]

                vclip = (VideoFileClip(videoname).subclip((start), (end)).
                         resize(width=540))

                clip = vclip

                counter1 += 1
            else:
                start = dict[link]['start'][counter1]
                end = dict[link]['end'][counter1]

                vclip = (VideoFileClip(videoname).subclip((start), (end)).
                         resize(width=540))

                clip = concatenate_videoclips([clip, vclip])

                counter1 += 1

        # setting gif to desired speed and creating file
        clip = clip.speedx(speed)

        fname = hashitup("gif", ".gif")

        filepath = os.path.join(giffolder, fname)

        clip.write_gif(filepath)

        clip.close()
        # appending file name to list
        fnames.append(filepath)

        counter += 1

    # running this to delete old files
    deleteoldfiles([giffolder])

    # returning list with gif files created
    return fnames


def manygifpervid(dict, speed=1):
    """Short summary.
    Function takes the dictionary and creates many gif per video link.
    Each start/stop time per YouTube link will get its own gif file

    Parameters
    ----------
    dict : dictionary of dictionary of lists. First dictionary key contains
            the link of the YouTube video, the value is another dictionary
            containing lists of the start and end times in "HH:MM:SS.MS" format

        Example:
        {YTLink: {'start': ['00:00:00.00', '00:00:05.00'],
                  'end': ['00:00:04.59', '00:00:9.59']}}

    speed : number
        Choose for desired output speed of gif
        1 is normal, 0.5 if half speed, 2 is twice speed

    Returns
    -------
    filenames
        returns a list of filenames created
    gif
        One gif file per video link that is in the provided dictionary

    """

    # creating list that will contain gif file names
    fnames = []

    # creating counter for video file names
    counter3 = 1
    # creating counter for gif file names
    counter1 = 0
    for link in dict:
        videoname = ytlinkexist(link)

        if videoname == 'no data':
            yt = YouTube(link)
            # videoname = yt.title + ".mp4"
            # videoname = "Video_" + str(counter3) + ".mp4"
            videoname = hashitup("Video", ".mp4")
            videoname = os.path.join(vidfolder, videoname)

            # getting MP4 format video (stream) with highest resolution
            stream = (yt.streams.filter(file_extension='mp4')
                        .get_highest_resolution())
            stream.download(filename=videoname)

            # inserting YouTube link and MP4 file name into data base
            insertytlinkmp4(link, videoname)
        else:
            pass

        # creating counter for dictionary indexes
        counter2 = 0
        for j in dict[link]['start']:
            start = dict[link]['start'][counter2]
            end = dict[link]['end'][counter2]

            clip = (VideoFileClip(videoname).subclip((start), (end)).
                    resize(width=540))

            fname = hashitup("gif", ".gif")
            filepath = os.path.join(giffolder, fname)

            fnames.append(filepath)

            clip = clip.speedx(speed)
            clip.write_gif(filepath)

            counter1 += 1
            counter2 += 1

        counter3 += 1

    clip.close()

    # running this to delete old files
    deleteoldfiles([giffolder])

    # returning list with gif files created
    return fnames
