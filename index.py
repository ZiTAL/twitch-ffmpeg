#!/usr/bin/env python3
# -*- coding: utf-8 -*

from src.TwitchFfmpeg import TwitchFfmpeg
from src.TwitchFfmpeg import TwitchApi
from src.TwitchFfmpeg import TwitchConfig

TwitchConfig.setPath('/home/projects/twitch-ffmpeg/config')
#TwitchApi.setTokenFromCode()

#TwitchApi.refreshToken()
#TwitchApi.setStreamTitle('froga')
#TwitchFfmpeg.setVideoPath("/home/zital/Bideoak/dragoi_bola/db")
TwitchFfmpeg.stream(""/home/zital/Bideoak/dragoi_bola/db"/01.mp4")
