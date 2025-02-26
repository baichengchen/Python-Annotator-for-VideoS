# Python Annotator for VideoS
PAVS - A simple video labeling tool developed in PyQt5 for managing the dataset of the ASDetect Project

Annotate videos in common formats(mp4, avi, mkv, wav, mp3)

You can easily annotate video files per frame or in groups and label the video files either based on their category or create a custom label.
In the example below we have annotated an mp4 file. You can see the video player and the data after annotating the particular frames. This data table can be exported and imported into a CSV File.
Refer help.txt before proceeding with the usage of the application.

![example](https://raw.githubusercontent.com/kevalvc/Python-Annotator-for-VideoS/master/Examples/example.PNG)

## Installation
 * Dependencies

   * python-pyqt5
   * python-pyqt5.Qtmultimedia
   * python-pyqt5.QtMultimediaWidgets
   * python-pyqt5.QtCore
   * python-pyqt5.QtGui
   * os
   * csv
   * sys
   * python-numpy

## Usage
   * Running the annotator
 ```
     python pavs.py
```

## Shortcuts
- S: update start bounding box (left top corner pixel)
- E: update end bounding box (right bottom corner pixel)
- D: delete rows selected
- F:add current data to table
- Space: play/pause video
