#!/usr/bin/env python3
# -*- coding: utf-8 -*

from src.TwitchFfmpeg import TwitchFfmpeg

tf = TwitchFfmpeg('/home/projects/twitch-ffmpeg/config')
#tf.Api.refreshToken()
tf.Api.setStreamTitle('FROGA BIDEO ZERRENDA')
#tf.streamFile('/home/zital/Bideoak/dragoi_bola/db/018.mp4')
tf.streamVideoList('/home/zital/scripts/bash/twitch/db.list')
