#!/usr/bin/env python3
# -*- coding: utf-8 -*

import json
import os
import requests
from urllib.parse import urlencode
import re
import subprocess

class TwitchFfmpeg:

    video_path = ''

    @staticmethod
    def stream(filename):
        channel = TwitchConfig.getChannel()

        key = channel['key']
        server = channel['server']        

        url = server+key
        
        command_list = TwitchConfig.getFfmpeg()
        command_list = TwitchFfmpeg.setInputForCommand(command_list, filename)
        command_list.append(url)

        subprocess.Popen([command_list], stdout=subprocess.PIPE)

    @staticmethod
    def setVideoPath(path):
        if re.search(r'\/$', path) == None:
            path = path + "/"        
        TwitchFfmpeg.video_path = path

    @staticmethod
    def getVideoPath():
        return TwitchFfmpeg.video_path

    @staticmethod
    def setInputForCommand(command_list, input):
        tmp = []
        for i in command_list:
            if re.search(r'^\-i (\$1)', i):
                i = i.replace(i, "-i \""+input+"\" ")
            tmp.append(i)
        return tmp

class TwitchApi:

    url_oauth = 'https://id.twitch.tv/oauth2/'
    url_helix = 'https://api.twitch.tv/helix/'

    @staticmethod
    def setTokenFromCode():
        client = TwitchConfig.getClient()

        params = {}
        params['client_id'] = client['client_id']
        params['redirect_uri'] = 'https://localhost'
        params['response_type'] = 'code'
        params['scope'] = 'channel:manage:broadcast'

        url = TwitchApi.url_oauth+"authorize?"+urlencode(params, doseq=True)
        print('Authorization URL:')
        print(url)

        code = input('ENTER CODE: ')
        assert len(code) == 30        

        token = TwitchApi.getToken(code)
        TwitchConfig.setToken(token)

    @staticmethod
    def getToken(code):
        client = TwitchConfig.getClient()

        params = {}
        params['client_id'] =  client['client_id']
        params['client_secret'] = client['client_secret']
        params['code'] = code
        params['grant_type'] = 'authorization_code'
        params['redirect_uri'] = 'https://localhost'

        response = requests.post(TwitchApi.url_oauth+"token", params)
        if response.status_code!=200:
            return False
        return response.json()

    @staticmethod
    def refreshToken():
        client = TwitchConfig.getClient()
        token = TwitchConfig.getToken()

        headers = {}
        headers['Client-Id'] = client['client_id']
        headers['Authorization'] = "Bearer " + token['access_token']

        params = {}
        params['grant_type'] = 'refresh_token'
        params['refresh_token'] = token['refresh_token']
        params['client_id'] = client['client_id']
        params['client_secret'] = client['client_secret']

        url = TwitchApi.url_oauth+"token"
        response = requests.post(url, params, headers=headers)
        if response.status_code!=200:
            print('TwitchApi.refreshToken(): Error renewing token')
            return False

        response = response.json()
        TwitchConfig.setToken(response)

    @staticmethod
    def getBroadcasterId():
        channel = TwitchConfig.getChannel()
        client = TwitchConfig.getClient()
        token = TwitchConfig.getToken()

        headers = {}
        headers['Client-Id'] = client['client_id']
        headers['Authorization'] = "Bearer " + token['access_token']        

        params = {}
        params['login'] = [channel['channel']]

        url = TwitchApi.url_helix+"users?" + urlencode(params, doseq=True)
        response = requests.get(url, headers=headers)
        if response.status_code!=200:
            print("TwitchApi.getBroadcasterId(): Error getting broadcaster_id")
            return False

        return response.json()['data'][0]['id']

    @staticmethod
    def setStreamTitle(title):
        client = TwitchConfig.getClient()
        token = TwitchConfig.getToken()        

        headers = {}
        headers['Client-Id'] = client['client_id']
        headers['Authorization'] = "Bearer " + token['access_token']

        params = {}
        params['broadcaster_id'] = TwitchApi.getBroadcasterId()
        params['title'] = title

        url = TwitchApi.url_helix+"channels?"+urlencode(params, doseq=True)
        response = requests.patch(url, headers=headers)
        if response.status_code!=204:
            print("TwitchApi.setStreamTitle(): Error changing title")
            return False
        else:
            return True

class TwitchConfig:

    path = ''

    channel_file = 'twitch_channel.json'
    @staticmethod
    def getChannel():
        path = TwitchConfig.getPath()
        channel_file = path+TwitchConfig.channel_file
        channel = json.load(open(channel_file))
        return channel

    client_file = 'twitch_client.json'
    @staticmethod
    def getClient():
        path = TwitchConfig.getPath()
        client_file = path+TwitchConfig.client_file
        client = json.load(open(client_file))
        return client   

    token_file = 'twitch_token.json'
    @staticmethod
    def getToken():
        path = TwitchConfig.getPath()
        token_file = path+TwitchConfig.token_file
        token = json.load(open(token_file))
        return token

    @staticmethod
    def setToken(data):
        path = TwitchConfig.getPath()
        token_file = path+TwitchConfig.token_file
        try:
            with open(token_file, 'w') as fp:
                json.dump(data, fp)
            return True
        except:
            print("TwitchConfig.setToken(): Error writing token to file: "+token_file)
            return False

    @staticmethod
    def getDefaultPath():
        return os.path.dirname(os.path.realpath(__file__))+"/"

    @staticmethod
    def getPath():
        if TwitchConfig.path == '':
            TwitchConfig.setPath(TwitchConfig.getDefaultPath())
        return TwitchConfig.path

    @staticmethod
    def setPath(path):
        if re.search(r'\/$', path) == None:
            path = path + "/"
        TwitchConfig.path = path

    ffmpeg_file = 'twitch_ffmpeg.json'
    @staticmethod
    def getFfmpeg():
        path = TwitchConfig.getPath()
        ffmpeg_file = path+TwitchConfig.ffmpeg_file
        ffmpeg = json.load(open(ffmpeg_file))
        return ffmpeg

