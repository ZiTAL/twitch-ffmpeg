#!/usr/bin/env python3
# -*- coding: utf-8 -*

import json
import os
import requests
from urllib.parse import urlencode

class TwitchFfmpeg:

    @staticmethod
    def init():
        print(TwitchApi.authorize())

class TwitchApi:

    url_oauth = 'https://id.twitch.tv/oauth2/'

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

class TwitchConfig:

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
    def getPath():
        return os.path.dirname(os.path.realpath(__file__))+"/"