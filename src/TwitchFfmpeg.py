#!/usr/bin/env python3
# -*- coding: utf-8 -*

import sys
import json
import os
import requests
from urllib.parse import urlencode
import re
import subprocess
import time

class TwitchFfmpeg:

    Config = None
    Api = None

    def __init__(self, config_path = None):
        self.Config = TwitchConfig(config_path)
        self.Api = TwitchApi(self.Config)

    def stream(self, file_name, type):
        url = self.getStreamUrl()
        ffmpeg_config = self.Config.getFfmpeg(type)
        command_list = self.setInputForCommand(ffmpeg_config, file_name)
        command_list.append(url)
        command = "".join(command_list)

        """
        ret = os.system(command)
        while ret == 0:
            print(ret)
            self.stream(file_name, type)
        """

        command = command.split()

        process = subprocess.Popen(command)

        while self.isProcessRunning(process):
            self.streamClearCache()

        self.stream(file_name, type)

    def self.streamClearCache(self):
# TODO
        pass

    def isProcessRunning(self, process):
        if process.poll() is None:
            return True
        return False

    def streamFile(self, file_name):
        self.stream(file_name, 'filename')

    def streamVideoList(self, video_list):
        self.stream(video_list, 'videolist')

    def setInputForCommand(self, command_list, input):
        tmp = []
        for i in command_list:
            if re.search(r'^\-i (\$1)', i):
                i = i.replace(i, "-i "+input+" ")
            tmp.append(i)
        return tmp

    def getStreamUrl(self):
        channel = self.Config.getChannel()
        key = channel['key']
        server = channel['server']
        url = server+key
        return url    

class TwitchApi:

    Url = {
        "oauth": "https://id.twitch.tv/oauth2/",
        "helix": "https://api.twitch.tv/helix/"
    }

    Config = None

    def __init__(self, config):
        self.Config = config

    def setTokenFromCode(self):
        client = self.Config.getClient()

        params = {}
        params['client_id'] = client['client_id']
        params['redirect_uri'] = 'https://localhost'
        params['response_type'] = 'code'
        params['scope'] = 'channel:manage:broadcast'

        url = self.Url['oauth']+"authorize?"+urlencode(params, doseq=True)
        print('Authorization URL:')
        print(url)

        code = input('ENTER CODE: ')
        assert len(code) == 30

        token = self.getToken(code)
        self.Config.setToken(token)

    def getToken(self, code):
        client = self.Config.getClient()

        params = {}
        params['client_id'] =  client['client_id']
        params['client_secret'] = client['client_secret']
        params['code'] = code
        params['grant_type'] = 'authorization_code'
        params['redirect_uri'] = 'https://localhost'

        response = requests.post(self.Url['oauth']+"token", params)
        if response.status_code!=200:
            return False
        return response.json()

    def refreshToken(self):
        client = self.Config.getClient()
        token = self.Config.getToken()
        headers = self.getHeaders()

        params = {}
        params['grant_type'] = 'refresh_token'
        params['refresh_token'] = token['refresh_token']
        params['client_id'] = client['client_id']
        params['client_secret'] = client['client_secret']

        url = self.Url['oauth']+"token"
        response = requests.post(url, params, headers=headers)
        if response.status_code!=200:
            print('TwitchApi.refreshToken(): Error renewing token')
            return False

        response = response.json()
        self.Config.setToken(response)

    def getBroadcasterId(self):
        channel = self.Config.getChannel()
        headers = self.getHeaders()

        params = {}
        params['login'] = [channel['channel']]

        url = self.Url['helix']+"users?" + urlencode(params, doseq=True)
        print(url)
        response = requests.get(url, headers=headers)
        if response.status_code!=200:
            print("TwitchApi.getBroadcasterId(): Error getting broadcaster_id")
            return False

        return response.json()['data'][0]['id']

    def setStreamTitle(self, title):
        headers = self.getHeaders()

        params = {}
        params['broadcaster_id'] = self.getBroadcasterId()
        params['title'] = title

        url = self.Url['helix']+"channels?"+urlencode(params, doseq=True)
        response = requests.patch(url, headers=headers)
        if response.status_code!=204:
            print("TwitchApi.setStreamTitle(): Error changing title")
            return False
        else:
            return True

    def getHeaders(self):
        client = self.Config.getClient()
        token = self.Config.getToken()

        headers = {}
        headers['Client-Id'] = client['client_id']
        headers['Authorization'] = "Bearer " + token['access_token']

        return headers

class TwitchConfig:

    path = ''
    channel_file = 'twitch_channel.json'
    client_file = 'twitch_client.json'
    token_file = 'twitch_token.json'

    def __init__(self, path = None):
        self.setPath(path)

    def getChannel(self):
        path = self.getPath()
        channel_file = path+self.channel_file
        channel = json.load(open(channel_file))
        return channel
    
    def getClient(self):
        path = self.getPath()
        client_file = path+self.client_file
        client = json.load(open(client_file))
        return client   
    
    def getToken(self):
        path = self.getPath()
        token_file = path+self.token_file
        token = json.load(open(token_file))
        return token

    def setToken(self, data):
        path = self.getPath()
        token_file = path+self.token_file
        try:
            with open(token_file, 'w') as fp:
                json.dump(data, fp)
            return True
        except:
            print("TwitchConfig.setToken(): Error writing token to file: "+token_file)
            return False

    def getDefaultPath(self):
        return os.path.dirname(os.path.realpath(__file__))+"/"

    def getPath(self):
        if self.path == '':
            self.setPath(self.getDefaultPath())
        return self.path

    def setPath(self, path = None):
        if re.search(r'\/$', path) == None:
            path = path + "/"
        self.path = path

    def getFfmpeg(self, type):
        path = self.getPath()
        ffmpeg_file = path+"twitch_ffmpeg_"+type+".json"
        ffmpeg = json.load(open(ffmpeg_file))
        return ffmpeg
