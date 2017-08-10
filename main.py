#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import threading
#import pypyodbc as pyodbc
import urllib
import requests 
import datetime
from xml.etree import ElementTree as ET
import subprocess

from bs4 import BeautifulSoup
import re 

import telebot
from telebot import types

from datetime import datetime

#import botan - statistics module

from telegram_bot_users import *

#google speech
#import speech_recognition as sr

import bot_voice

#import pyglet

from io import BytesIO

from time import time, sleep

#from pydub import AudioSegment
#AudioSegment.converter = 'C:\ffmpeg\bin'

import botan

import locale
#import socket
#socket.getaddrinfo('localhost', 8080)

#import telegram.ext
#import telegram
from extentions import EnumHelper, FileHelper, TextHelper

import xml.etree.ElementTree as XmlElementTree

import settings

from pymongo import MongoClient
import sys

from pyshorteners import Shortener


import sqlite3


import socket
socket.setdefaulttimeout(30)

#import socket
#socket.getaddrinfo('localhost', 8080)

#import socket
#socket.setdefaulttimeout(10)
#print(socket.getdefaulttimeout())

exchange = u'\U0001F4B1'
quotes = u'\U0001F4C8'
#ГОСБ
index = u'\U0001F3E0'
#СРБ
srbindex = u'\U0001F3EB'
#ЦА
caindex = u'\U0001F3E2'
question = u'\U0000270F'
menuback = u'\U0001F519'

# SqlServer connection string
#cnxn = pyodbc.connect('Driver={SQL Server};''Server=localhost;''Database=SRB-FINANALIT02;')
#cursor = cnxn.cursor()

# Constants to indicate steps while user is entering password
TEAM_USER_LOGGING = 0
TEAM_USER_ACCEPTED = 1

# Data structure for list of bot`s users
team_users = TeamUserList()

# Insert your telegram bot`s token here
TOKEN = settings.Telegram.TOKEN

api_key = settings.Shorter.API_KEY

bot = telebot.TeleBot(TOKEN)

#For botan statistic
botan_key = settings.Botan.TOKEN

user_step = {}
user_active_dialog = {}
reply_data_db = {}

    
# Команда старт
@bot.message_handler(commands=['help','start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Welcome to SRB-BOT!")
    bot.send_message(message.chat.id,"Отправьте слово Заявка,чтобы получить доступ")
    #bot.send_message(message.chat.id, "/on - войти с паролем")
    #bot.send_message(message.chat.id, "/off - выйти из запароленой области")
    #bot.send_message(message.chat.id, "/again - обратно в меню")


#Перехватчик заявок
@bot.message_handler(func=lambda message:message.text == 'Заявка')
@bot.message_handler(func=lambda message:message.text == 'заявка')
def reg(message):
    if message.chat.id not in team_users:
        logbotmessage(message)
        #Запись
        date = datetime.now()
        my_file = open("Feedback.txt", "ab")
        feedback1 = (str(date)+" "+str(message.chat.id)+" "+str(message.chat.last_name)+str(message.chat.first_name)+"\n").encode('UTF-8')
        my_file.write(feedback1)
        my_file.close()
        print('Заявка')
        #Сообщение
        bot.send_message(message.chat.id,"Заявка принята на рассмотрение")
        bot.send_message(message.chat.id,"Напишите слово Меню через 1 минуту")


'''
# Custom command to add user to an operator`s team
@bot.message_handler(commands=['on'])
def subscribe_chat(message):
    if message.chat.id in team_users:
        bot.reply_to(message, "Вы уже авторизованы ")
    else:
        user_step[message.chat.id] = TEAM_USER_LOGGING
        bot.reply_to(message, "Введите пароль:")


# Here we catch user message after '/on' command and
# interpret it as a password
@bot.message_handler(func=lambda message: user_step.get(message.chat.id) == TEAM_USER_LOGGING)
def team_user_login(message):
    if message.text == 'Password1':
        team_users.add(TeamUser(message.chat.id))
        user_step[message.chat.id] = TEAM_USER_ACCEPTED
        bot.reply_to(message, "Верный пароль!")
        #bot.edit_message(message.chat.id,'**********')
        process(message)
    else:
        bot.reply_to(message, "Пароль неверный.Попробуйте еще раз /on")
'''

#выход из запароленной области 
@bot.message_handler(commands=['off'])
def team_user_logout(message):
    if message.chat.id not in team_users:
        bot.reply_to(message, "Вы уже ввели пароль")
    else:
        team_users.remove_by_chat_id(message.chat.id)
        #Close Keyboard 
        keyboard_hider = types.ReplyKeyboardHide()
        bot.reply_to(message, "Вы выключили сообщения",reply_markup=keyboard_hider)

        

#меню основное
@bot.message_handler(commands=['again'])
@bot.message_handler(func=lambda message:message.text == 'Меню')
@bot.message_handler(func=lambda message:message.text == 'меню')
@bot.message_handler(func=lambda message:message.text == 'Меню'+menuback)
def processmenu(message):
    if message.chat.id in team_users:
        logbotmessage(message)
        markup = types.ReplyKeyboardMarkup()
        markup.row('Оперативка','Аналитика')
        markup.row('Материалы ЦА','Ключевое')
        markup.row('Прочее')
        bot.send_message(message.chat.id, "Выберите показатель:", reply_markup=markup)

#%Прочее
@bot.message_handler(func=lambda message:message.text == 'Прочее')
def process(message):
    if message.chat.id in team_users:
        logbotmessage(message)
        botan.track(botan_key, message.chat.id, message, 'Прочее')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(exchange+'Валюта')
        markup.row(quotes+'Котировки')
        markup.row('Акции Сбербанка')
        markup.row('Меню'+menuback)
        bot.send_message(message.chat.id, "Выберите:", reply_markup=markup)        
        
 
#%Пункт главного меню - Оперативка 
@bot.message_handler(func=lambda message:message.text == 'Оперативка')
def process(message):
    if message.chat.id in team_users:
        logbotmessage(message)
        botan.track(botan_key, message.chat.id, message, 'Оперативка')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row('ФБ','КБ')
        markup.row('РБ')
        markup.row('Меню'+menuback)
        bot.send_message(message.chat.id, "Выберите:", reply_markup=markup)

@bot.message_handler(func=lambda message:message.text == 'ФБ' , content_types=['text'])
def pokaz_SRB(message):
    if message.chat.id in team_users:
        try:
            logbotmessage(message)
            bot.send_message(message.chat.id,"Оперативка:ФБ:")
            #bot.send_message(message.chat.id,r"https://drive.google.com/open?id=0Bxfebnhj7Hp_S0phSHNwMlhlbFU")
            #shortener = Shortener('Google', api_key=api_key)
            #top1=format(shortener.short("https://drive.google.com/open?id=0Bxfebnhj7Hp_S0phSHNwMlhlbFU"))
            con = sqlite3.connect(settings.BDconnection.path)
            cur = con.cursor()
            string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='FB'")
            data = string.fetchone()
            if data:
                url = data[0]
            bot.send_message(message.chat.id,urlshorter(url))
            #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин") 
            #pdfgosboper = open(r'C:\Users\ivan\Desktop\SRBbot 1.5\Oper\FB.pdf', 'rb')
            #bot.send_chat_action(message.chat.id,'upload_document')
            #bot.send_document(message.chat.id, pdfgosboper, timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")

@bot.message_handler(func=lambda message:message.text == 'КБ' , content_types=['text'])
def pokaz_SRB(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message)
           bot.send_message(message.chat.id,"Оперативка:КБ:")
           con = sqlite3.connect(settings.BDconnection.path)
           cur = con.cursor()
           string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='KB'")
           data = string.fetchone()
           if data:
               url = data[0]
           bot.send_message(message.chat.id,urlshorter(url)) 
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdfgosboper = open(r'C:\Users\ivan\Desktop\SRBbot 1.5\Oper\KB.pdf', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdfgosboper, timeout = 60 )
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")

@bot.message_handler(func=lambda message:message.text == 'РБ' , content_types=['text'])
def pokaz_SRB(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message)
           bot.send_message(message.chat.id,"Оперативка:РБ:")
           con = sqlite3.connect(settings.BDconnection.path)
           cur = con.cursor()
           string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='RB'")
           data = string.fetchone()
           if data:
               url = data[0]
           bot.send_message(message.chat.id,urlshorter(url)) 
           #bot.send_message(message.chat.id,"Оперативка:РБ:")
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdfgosboper = open(r'C:\Users\ivan\Desktop\SRBbot 1.5\Oper\RB.pdf', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdfgosboper, timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")



        
#%Пункт главного меню - Аналитика
@bot.message_handler(func=lambda message:message.text == 'Аналитика')
def process(message):
    if message.chat.id in team_users:
        logbotmessage(message)
        botan.track(botan_key, message.chat.id, message, 'Аналитика')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row('Бирюза','PD')
        markup.row(srbindex+'Смотр-конкурс')
        markup.row('Меню'+menuback)
        bot.send_message(message.chat.id, "Выберите:", reply_markup=markup)

@bot.message_handler(func=lambda message:message.text == 'Сравнение ТБ' , content_types=['text'])
def pokaz_SRB(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message)
           bot.send_message(message.chat.id,"Аналитика:Сравнение ТБ:")
           bot.send_message(message.chat.id,"Файл пока не загружен")
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdfgosboper = open(r'', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdfgosboper, timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")
        

@bot.message_handler(func=lambda message:message.text == srbindex+'Смотр-конкурс' , content_types=['text'])
def pokaz_SRB(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message)
           bot.send_message(message.chat.id,"Аналитика:Смотр-конкурс:")
           con = sqlite3.connect(settings.BDconnection.path)
           cur = con.cursor()
           string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='Smotr'")
           data = string.fetchone()
           if data:
               url = data[0]
           bot.send_message(message.chat.id,urlshorter(url)) 
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdfgosboper = open(r'C:\Users\ivan\Desktop\SRBbot 1.5\Analit\SmotrTB.pdf', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdfgosboper, timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")


@bot.message_handler(func=lambda message:message.text == 'Бирюза' , content_types=['text'])
def pokaz_SRB(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message)
           bot.send_message(message.chat.id,"Аналитика:Бирюза:")
           con = sqlite3.connect(settings.BDconnection.path)
           cur = con.cursor()
           string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='Biruza'")
           data = string.fetchone()
           if data:
               url = data[0]
           bot.send_message(message.chat.id,urlshorter(url)) 
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdfgosboper = open(r'C:\Users\ivan\Desktop\python bot\SRBbot0.85\Analit\Biruza.pdf', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdfgosboper, timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")


#PD ANALIT
@bot.message_handler(func=lambda message:message.text == 'PD' , content_types=['text'])
def pokaz_SRB(message):
    if message.chat.id in team_users:
           logbotmessage(message)
           botan.track(botan_key, message.chat.id, message, 'Аналитика-PD')
           bot.send_message(message.chat.id,index+"PD:")
           markup = types.ReplyKeyboardMarkup()
           markup.row('PDСРБ')
           markup.row('Юг','Cевер','Восток','Запад')
           markup.row('Смоленск','Тула','Брянск')
           markup.row('Рязань','Тверь','Калуга')
           markup.row('Меню'+menuback)
           bot.send_message(message.chat.id, "Выберите показатель:", reply_markup=markup)            

#PD по ГОСБ
@bot.message_handler(func=lambda message:message.text == 'PDСРБ' , content_types=['text'])
def pokaz_Gosb_pd(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message)
           bot.send_message(message.chat.id,"Аналитика:СРБ:")
           con = sqlite3.connect(settings.BDconnection.path)
           cur = con.cursor()
           string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='PDSRB'")
           data = string.fetchone()
           if data:
               url = data[0]
           bot.send_message(message.chat.id,urlshorter(url)) 
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdfgosboper = open(r'C:\Users\ivan\Desktop\python bot\SRBbot0.85\ЧАТ NEW\Аналитика\PD\PD_SRB.pdf', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdfgosboper, timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")

           
@bot.message_handler(func=lambda message:message.text == 'Юг' , content_types=['text'])
def pokaz_Gosb_pd(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message)
           bot.send_message(message.chat.id,"Аналитика:Юг:")
           con = sqlite3.connect(settings.BDconnection.path)
           cur = con.cursor()
           string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='PDUg'")
           data = string.fetchone()
           if data:
               url = data[0]
           bot.send_message(message.chat.id,urlshorter(url)) 
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdfgosboper = open(r'C:\Users\ivan\Desktop\python bot\SRBbot0.75\GOSB\GOSB_PD_UG.pdf', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdfgosboper,timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")

           
@bot.message_handler(func=lambda message:message.text == 'Cевер' , content_types=['text'])
def pokaz_Gosb_pd(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message)
           bot.send_message(message.chat.id,"Аналитика:Север:")
           con = sqlite3.connect(settings.BDconnection.path)
           cur = con.cursor()
           string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='PDSever'")
           data = string.fetchone()
           if data:
               url = data[0]
           bot.send_message(message.chat.id,urlshorter(url)) 
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdfgosboper = open(r'C:\Users\ivan\Desktop\python bot\SRBbot0.75\GOSB\GOSB_PD_Sever.pdf', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdfgosboper, timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")


@bot.message_handler(func=lambda message:message.text == 'Восток' , content_types=['text'])
def pokaz_Gosb_pd(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message)         
           bot.send_message(message.chat.id,"Аналитика:Восток:")
           con = sqlite3.connect(settings.BDconnection.path)
           cur = con.cursor()
           string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='PDVostok'")
           data = string.fetchone()
           if data:
               url = data[0]
           bot.send_message(message.chat.id,urlshorter(url)) 
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdfgosboper = open(r'C:\Users\ivan\Desktop\python bot\SRBbot0.75\GOSB\GOSB_PD_Vostok.pdf', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdfgosboper,timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")


@bot.message_handler(func=lambda message:message.text == 'Запад' , content_types=['text'])
def pokaz_Gosb_pd(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message)
           bot.send_message(message.chat.id,"Аналитика:Запад:")
           con = sqlite3.connect(settings.BDconnection.path)
           cur = con.cursor()
           string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='PDZapad'")
           data = string.fetchone()
           if data:
               url = data[0]
           bot.send_message(message.chat.id,urlshorter(url)) 
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdfgosboper = open(r'C:\Users\ivan\Desktop\python bot\SRBbot0.75\GOSB\GOSB_PD_Zapad.pdf', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdfgosboper,timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")


@bot.message_handler(func=lambda message:message.text == 'Смоленск' , content_types=['text'])
def pokaz_Gosb_pd(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message)
           bot.send_message(message.chat.id,"Аналитика:Смоленск:")
           con = sqlite3.connect(settings.BDconnection.path)
           cur = con.cursor()
           string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='PDSmolensk'")
           data = string.fetchone()
           if data:
               url = data[0]
           bot.send_message(message.chat.id,urlshorter(url)) 
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdfgosboper = open(r'C:\Users\ivan\Desktop\python bot\SRBbot0.75\GOSB\GOSB_PD_Smolensk.pdf', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdfgosboper, timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")


@bot.message_handler(func=lambda message:message.text == 'Тула' , content_types=['text'])
def pokaz_Gosb_pd(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message)
           bot.send_message(message.chat.id,"Аналитика:Тула:")
           con = sqlite3.connect(settings.BDconnection.path)
           cur = con.cursor()
           string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='PDTula'")
           data = string.fetchone()
           if data:
               url = data[0]
           bot.send_message(message.chat.id,urlshorter(url)) 
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdfgosboper = open(r'C:\Users\ivan\Desktop\python bot\SRBbot0.75\GOSB\GOSB_PD_Tula.pdf', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdfgosboper, timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")


@bot.message_handler(func=lambda message:message.text == 'Брянск' , content_types=['text'])
def pokaz_Gosb_pd(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message)
           bot.send_message(message.chat.id,"Аналитика:Брянск:")
           con = sqlite3.connect(settings.BDconnection.path)
           cur = con.cursor()
           string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='PDBryansk'")
           data = string.fetchone()
           if data:
               url = data[0]
           bot.send_message(message.chat.id,urlshorter(url)) 
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdfgosboper = open(r'C:\Users\ivan\Desktop\python bot\SRBbot0.75\GOSB\GOSB_PD_Bryansk.pdf', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdfgosboper,timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")

@bot.message_handler(func=lambda message:message.text == 'Рязань' , content_types=['text'])
def pokaz_Gosb_pd(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message)
           bot.send_message(message.chat.id,"Аналитика:Рязань:")
           con = sqlite3.connect(settings.BDconnection.path)
           cur = con.cursor()
           string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='PDRyzan'")
           data = string.fetchone()
           if data:
               url = data[0]
           bot.send_message(message.chat.id,urlshorter(url)) 
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdfgosboper = open(r'C:\Users\ivan\Desktop\python bot\SRBbot0.75\GOSB\GOSB_PD_Ryazan.pdf', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdfgosboper,timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")

@bot.message_handler(func=lambda message:message.text == 'Тверь' , content_types=['text'])
def pokaz_Gosb_pd(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message)
           bot.send_message(message.chat.id,"Аналитика:Тверь:")
           con = sqlite3.connect(settings.BDconnection.path)
           cur = con.cursor()
           string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='PDTver'")
           data = string.fetchone()
           if data:
               url = data[0]
           bot.send_message(message.chat.id,urlshorter(url)) 
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdfgosboper = open(r'C:\Users\ivan\Desktop\python bot\SRBbot0.75\GOSB\GOSB_PD_Tver.pdf', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdfgosboper,timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")

@bot.message_handler(func=lambda message:message.text == 'Калуга' , content_types=['text'])
def pokaz_Gosb_pd(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message)
           bot.send_message(message.chat.id,"Аналитика:Калуга:")
           con = sqlite3.connect(settings.BDconnection.path)
           cur = con.cursor()
           string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='PDKaluga'")
           data = string.fetchone()
           if data:
               url = data[0]
           bot.send_message(message.chat.id,urlshorter(url)) 
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdfgosboper = open(r'C:\Users\ivan\Desktop\python bot\SRBbot0.75\GOSB\GOSB_PD_UG.pdf', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdfgosboper,timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")
 
#%Пункт главного меню - Материалы ЦА
@bot.message_handler(func=lambda message:message.text == 'Материалы ЦА')
def processCA(message):
    if message.chat.id in team_users:
        logbotmessage(message)
        botan.track(botan_key, message.chat.id, message, 'Материалы ЦА')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row('Опер итоги','Факт итоги')
        markup.row('Встреча лидеров','Change')
        markup.row('Оперативка КБ ЦА','Оперативка РБ ЦА')
        markup.row('Меню'+menuback)
        bot.send_message(message.chat.id, "Выберите:", reply_markup=markup)

@bot.message_handler(func=lambda message:message.text == 'Опер итоги' , content_types=['text'])
def pokaz_SRB(message):
    if message.chat.id in team_users:
        try:
            logbotmessage(message)
            botan.track(botan_key, message.chat.id, message, 'МатЦА-Опер итоги')
            bot.send_message(message.chat.id,"Материалы ЦА:Опер итоги:")
            con = sqlite3.connect(settings.BDconnection.path)
            cur = con.cursor()
            string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='OPitogi'")
            data = string.fetchone()
            if data:
                url = data[0]
            bot.send_message(message.chat.id,urlshorter(url)) 
            #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
            #pdfgosboper = open(r'C:\Users\ivan\Desktop\SRBbot 1.5\MatCA\OperDF.pdf', 'rb')
            #bot.send_chat_action(message.chat.id,'upload_document')
            #bot.send_document(message.chat.id, pdfgosboper ,timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")

@bot.message_handler(func=lambda message:message.text == 'Оперативка КБ ЦА' , content_types=['text'])
def pokaz_SRB(message):
    if message.chat.id in team_users:
        try:
            logbotmessage(message)
            botan.track(botan_key, message.chat.id, message, 'МатЦА-Опер итоги-Оперативка КБ ЦА')
            bot.send_message(message.chat.id,"Раздел в разработке")
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            #markup.row('Прил 1')
            #markup.row('Прил 2')
            markup.row('Меню'+menuback)
            bot.send_message(message.chat.id, "Выберите:", reply_markup=markup)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")

@bot.message_handler(func=lambda message:message.text == 'Оперативка РБ ЦА' , content_types=['text'])
def pokaz_SRB(message):
    if message.chat.id in team_users:
        try:
            logbotmessage(message)
            botan.track(botan_key, message.chat.id, message, 'МатЦА-Опер итоги-Оперативка РБ ЦА')
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row('RB_1')
            markup.row('RB_2')
            markup.row('Меню'+menuback)
            bot.send_message(message.chat.id, "Выберите:", reply_markup=markup)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")


@bot.message_handler(func=lambda message:message.text == 'RB_1' , content_types=['text'])
def pokaz_SRB(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message)
           bot.send_message(message.chat.id,"Материалы ЦА:Оперативка РБ ЦА:RB_1")
           con = sqlite3.connect(settings.BDconnection.path)
           cur = con.cursor()
           string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='RB1'")
           data = string.fetchone()
           if data:
               url = data[0]
           bot.send_message(message.chat.id,urlshorter(url)) 
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdfgosboper = open(r'C:\Users\ivan\Desktop\SRBbot 1.5\MatCA\Oper RB\RBSergmentsExpCRMMDM.pdf', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdfgosboper, timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")

@bot.message_handler(func=lambda message:message.text == 'RB_2' , content_types=['text'])
def pokaz_SRB(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message)
           bot.send_message(message.chat.id,"Материалы ЦА:Оперативка РБ ЦА:RB_2")
           con = sqlite3.connect(settings.BDconnection.path)
           cur = con.cursor()
           string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='RB2'")
           data = string.fetchone()
           if data:
              url = data[0]
           bot.send_message(message.chat.id,urlshorter(url)) 
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdfgosboper = open(r'C:\Users\ivan\Desktop\SRBbot 1.5\MatCA\Oper RB\RBHRCreditDepCards.pdf', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdfgosboper, timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")

@bot.message_handler(func=lambda message:message.text == 'Факт итоги' , content_types=['text'])
def pokaz_SRB(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message)
           bot.send_message(message.chat.id,"Материалы ЦА:Факт итоги:")
           con = sqlite3.connect(settings.BDconnection.path)
           cur = con.cursor()
           string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='FCitogi'")
           data = string.fetchone()
           if data:
              url = data[0]
           bot.send_message(message.chat.id,urlshorter(url))
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdfgosboper = open(r'C:\Users\ivan\Desktop\SRBbot 1.5\MatCA\FactDF.pdf', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdfgosboper, timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")

@bot.message_handler(func=lambda message:message.text == 'Change')
def process(message):
    if message.chat.id in team_users:
        logbotmessage(message)
        botan.track(botan_key, message.chat.id, message, 'МатЦА-Change')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row('Big Data','Scrum')
        markup.row('Меню'+menuback)
        bot.send_message(message.chat.id, "Выберите:", reply_markup=markup)

@bot.message_handler(func=lambda message:message.text == 'Scrum' , content_types=['text'])
def pokaz_SRB(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message)
           bot.send_message(message.chat.id,"СРБ:СHANGE:Scrum:")
           con = sqlite3.connect(settings.BDconnection.path)
           cur = con.cursor()
           string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='Scrum'")
           data = string.fetchone()
           if data:
              url = data[0]
           bot.send_message(message.chat.id,urlshorter(url))
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdf = open(r'C:\Users\ivan\Desktop\python bot\SRBbot0.75\SRB\Change\Scrum.pdf', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdf,timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")

@bot.message_handler(func=lambda message:message.text == 'Big Data' , content_types=['text'])
def pokaz_SRB(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message) 
           bot.send_message(message.chat.id,"СРБ:СHANGE:Big Data:")
           con = sqlite3.connect(settings.BDconnection.path)
           cur = con.cursor()
           string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='Bigdata'")
           data = string.fetchone()
           if data:
              url = data[0]
           bot.send_message(message.chat.id,urlshorter(url))
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdf = open(r'C:\Users\ivan\Desktop\python bot\SRBbot0.75\SRB\Change\BigData.pdf', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdf,timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")

@bot.message_handler(func=lambda message:message.text == 'Встреча лидеров' , content_types=['text'])
def pokaz_SRB(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message)
           botan.track(botan_key, message.chat.id, message, 'МатЦА-Встреча лидеров')
           bot.send_message(message.chat.id,"Материалы ЦА:Встреча лидеров:")
           markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
           markup.row('Фокусы CIB(Буланцев)')
           markup.row('Вып. 3кварталКБ(Карташов)')
           markup.row('Кред. папйлайн(Соколов)')
           markup.row('Качество кред.портфеля(Бессонов)')
           markup.row('изм моделей PD на рейтинг(Ревина)')
           markup.row('Agile-трансформация статус(Чупина)')
           markup.row('Программа мероприятий к 175-летию(Миронюк)')
           markup.row('Статус передачи КБ в РБ')
           markup.row('Статус передачи КБ в РБ(целевая сеть)')
           markup.row('Приложение контактность')
           markup.row('Опер итоги августа(Агуреев)')
           markup.row('Меню'+menuback)
           bot.send_message(message.chat.id, "Выберите:", reply_markup=markup)
        except Exception as e:
           logboterror(message,e)
           print(e)
           bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")


@bot.message_handler(func=lambda message:message.text == 'Фокусы CIB(Буланцев)' , content_types=['text'])
def lider(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message)
           bot.send_message(message.chat.id,"Встреча лидеров:")
           con = sqlite3.connect(settings.BDconnection.path)
           cur = con.cursor()
           string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='Bulanzev'")
           data = string.fetchone()
           if data:
              url = data[0]
           bot.send_message(message.chat.id,urlshorter(url))
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdf = open(r'C:\Users\ivan\Desktop\SRBbot 1.05\MatCA\Lider\1FocusCIB (Bulavinzev).pdf', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdf,timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")

@bot.message_handler(func=lambda message:message.text == 'Вып. 3кварталКБ(Карташов)' , content_types=['text'])
def lider(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message)
           bot.send_message(message.chat.id,"Встреча лидеров:")
           con = sqlite3.connect(settings.BDconnection.path)
           cur = con.cursor()
           string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='Kartashov'")
           data = string.fetchone()
           if data:
              url = data[0]
           bot.send_message(message.chat.id,urlshorter(url))
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdf = open(r'C:\Users\ivan\Desktop\SRBbot 1.05\MatCA\Lider\2BP3kvarKB(Kartashov).pdf', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdf,timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")

@bot.message_handler(func=lambda message:message.text == 'Кред. папйлайн(Соколов)' , content_types=['text'])
def lider(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message) 
           bot.send_message(message.chat.id,"Встреча лидеров:")
           con = sqlite3.connect(settings.BDconnection.path)
           cur = con.cursor()
           string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='Sokolov'")
           data = string.fetchone()
           if data:
              url = data[0]
           bot.send_message(message.chat.id,urlshorter(url))
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdf = open(r'C:\Users\ivan\Desktop\SRBbot 1.05\MatCA\Lider\3CredPaipline(Sokolov).pdf', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdf,timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")

@bot.message_handler(func=lambda message:message.text == 'Качество кред.портфеля(Бессонов)' , content_types=['text'])
def lider(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message)
           bot.send_message(message.chat.id,"Встреча лидеров:")
           con = sqlite3.connect(settings.BDconnection.path)
           cur = con.cursor()
           string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='Bessonov'")
           data = string.fetchone()
           if data:
              url = data[0]
           bot.send_message(message.chat.id,urlshorter(url))
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdf = open(r'C:\Users\ivan\Desktop\SRBbot 1.05\MatCA\Lider\4CredQuality (Bessonov).pdf', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdf,timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")

@bot.message_handler(func=lambda message:message.text == 'изм моделей PD на рейтинг(Ревина)' , content_types=['text'])
def lider(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message)
           bot.send_message(message.chat.id,"Встреча лидеров:")
           con = sqlite3.connect(settings.BDconnection.path)
           cur = con.cursor()
           string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='Revina'")
           data = string.fetchone()
           if data:
              url = data[0]
           bot.send_message(message.chat.id,urlshorter(url))
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdf = open(r'C:\Users\ivan\Desktop\SRBbot 1.05\MatCA\Lider\5modelsPD(Revina).pdf', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdf,timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")


@bot.message_handler(func=lambda message:message.text == 'Agile-трансформация статус(Чупина)' , content_types=['text'])
def lider(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message)
           bot.send_message(message.chat.id,"Встреча лидеров:")
           con = sqlite3.connect(settings.BDconnection.path)
           cur = con.cursor()
           string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='Chupina'")
           data = string.fetchone()
           if data:
              url = data[0]
           bot.send_message(message.chat.id,urlshorter(url))
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdf = open(r'C:\Users\ivan\Desktop\SRBbot 1.05\MatCA\Lider\6Agile-transform(Chupina).pdf', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdf,timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")


@bot.message_handler(func=lambda message:message.text == 'Программа мероприятий к 175-летию(Миронюк)' , content_types=['text'])
def lider(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message)
           bot.send_message(message.chat.id,"Встреча лидеров:")
           con = sqlite3.connect(settings.BDconnection.path)
           cur = con.cursor()
           string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='Mironuk'")
           data = string.fetchone()
           if data:
              url = data[0]
           bot.send_message(message.chat.id,urlshorter(url))
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdf = open(r'C:\Users\ivan\Desktop\SRBbot 1.05\MatCA\Lider\7Fest175(Mironuk).pdf', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdf,timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")

@bot.message_handler(func=lambda message:message.text == 'Статус передачи КБ в РБ' , content_types=['text'])
def lider(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message)
           bot.send_message(message.chat.id,"Встреча лидеров:")
           con = sqlite3.connect(settings.BDconnection.path)
           cur = con.cursor()
           string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='KBvRB'")
           data = string.fetchone()
           if data:
              url = data[0]
           bot.send_message(message.chat.id,urlshorter(url))
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdf = open(r'C:\Users\ivan\Desktop\SRBbot 1.05\MatCA\Lider\8StatusKBvRB.PDF', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdf,timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")

@bot.message_handler(func=lambda message:message.text == 'Статус передачи КБ в РБ(целевая сеть)' , content_types=['text'])
def lider(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message)
           bot.send_message(message.chat.id,"Встреча лидеров:")
           con = sqlite3.connect(settings.BDconnection.path)
           cur = con.cursor()
           string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='KBvRB(net)'")
           data = string.fetchone()
           if data:
              url = data[0]
           bot.send_message(message.chat.id,urlshorter(url))
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdf = open(r'C:\Users\ivan\Desktop\SRBbot 1.05\MatCA\Lider\9StatusKBvRB(net).pdf', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdf,timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")

@bot.message_handler(func=lambda message:message.text == 'Приложение контактность' , content_types=['text'])
def lider(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message)
           bot.send_message(message.chat.id,"Встреча лидеров:")
           con = sqlite3.connect(settings.BDconnection.path)
           cur = con.cursor()
           string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='PrilContact'")
           data = string.fetchone()
           if data:
              url = data[0]
           bot.send_message(message.chat.id,urlshorter(url))
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdf = open(r'C:\Users\ivan\Desktop\SRBbot 1.05\MatCA\Lider\10sociability.pdf', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdf,timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")

@bot.message_handler(func=lambda message:message.text == 'Опер итоги августа(Агуреев)' , content_types=['text'])
def lider(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message)
           bot.send_message(message.chat.id,"Встреча лидеров:")
           con = sqlite3.connect(settings.BDconnection.path)
           cur = con.cursor()
           string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='Agureev'")
           data = string.fetchone()
           if data:
              url = data[0]
           bot.send_message(message.chat.id,urlshorter(url))
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdf = open(r'C:\Users\ivan\Desktop\SRBbot 1.05\MatCA\Lider\11Operaugust (Agureev).pdf', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdf,timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")


#%Пункт главного меню - Ключевое
@bot.message_handler(func=lambda message:message.text == 'Ключевое')
def process(message):
    if message.chat.id in team_users:
        logbotmessage(message)
        botan.track(botan_key, message.chat.id, message, 'Ключевое')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row('Контрольные показатели')
        markup.row('Формат ДФ')
        markup.row('Численность по ТБ')
        markup.row('Меню'+menuback)
        bot.send_message(message.chat.id, "Выберите:", reply_markup=markup)

@bot.message_handler(func=lambda message:message.text == 'Контрольные показатели' , content_types=['text'])
def pokaz_SRB(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message)
           bot.send_message(message.chat.id,"Ключевое:Контрольные показатели:")
           con = sqlite3.connect(settings.BDconnection.path)
           cur = con.cursor()
           string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='KP'")
           data = string.fetchone()
           if data:
               url = data[0]
           bot.send_message(message.chat.id,urlshorter(url)) 
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdfgosboper = open(r'C:\Users\ivan\Desktop\SRBbot 1.5\Key\KP.pdf', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdfgosboper, timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")


@bot.message_handler(func=lambda message:message.text == 'Формат ДФ' , content_types=['text'])
def pokaz_SRB(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message)
           bot.send_message(message.chat.id,"Ключевое:Оперативка Морозова:")
           con = sqlite3.connect(settings.BDconnection.path)
           cur = con.cursor()
           string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='OperMorozov'")
           data = string.fetchone()
           if data:
               url = data[0]
           bot.send_message(message.chat.id,urlshorter(url)) 
           #bot.send_message(message.chat.id,"Файл пока отсутствует")
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdfgosboper = open(r'C:\Users\ivan\Desktop\SRBbot 1.5\Key\Oper_Moroz.pdf', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdfgosboper, timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")


@bot.message_handler(func=lambda message:message.text == 'Численность по ТБ' , content_types=['text'])
def pokaz_SRB(message):
    if message.chat.id in team_users:
        try:
           logbotmessage(message)
           bot.send_message(message.chat.id,"Ключевое:Численность по ТБ:")
           con = sqlite3.connect(settings.BDconnection.path)
           cur = con.cursor()
           string = cur.execute("SELECT URL FROM chatdoc WHERE [INDEX]='NumTB'")
           data = string.fetchone()
           if data:
               url = data[0]
           bot.send_message(message.chat.id,urlshorter(url)) 
           #bot.send_message(message.chat.id,"Фаайл пока отсутствует")
           #bot.send_message(message.chat.id,"Файл загружается,подождите 1 мин")
           #pdfgosboper = open(r'C:\Users\ivan\Desktop\SRBbot 1.5\Key\TBNumber.pdf', 'rb')
           #bot.send_chat_action(message.chat.id,'upload_document')
           #bot.send_document(message.chat.id, pdfgosboper, timeout = 60)
        except Exception as e:
            logboterror(message,e)
            print(e)
            bot.send_message(message.chat.id,"Файл не удалось загрузить \n Возможно он отстутствует\n Попробуйте еще раз или напишите в обратную связь ")




#Котировки
@bot.message_handler(func=lambda message:message.text == quotes+'Котировки' , content_types=['text'])
def valuta(message):
    if message.chat.id in team_users:
        logbotmessage(message)
        bot.send_chat_action(message.chat.id,'typing')
        #kotirovki(message)
        bot.send_message(message.chat.id,'На данный момент не могу выдать котировки - смотрите на сайте:')
        bot.send_message(message.chat.id,'http://www.sberbank.ru/ru/person')

#Котировки
@bot.message_handler(func=lambda message:message.text == 'Акции Сбербанка' , content_types=['text'])
def valuta(message):
    if message.chat.id in team_users:
        logbotmessage(message)
        bot.send_chat_action(message.chat.id,'typing')
        #share(message)
        bot.send_message(message.chat.id,'На данный момент не могу выдать котировки - смотрите на сайте:')
        bot.send_message(message.chat.id,'http://www.sberbank.ru/ru/person')


#Перенапраление помощи на указатель помощи
@bot.message_handler(func=lambda message:message.text =='help', content_types=['text'])
def yelp(message):
    if message.chat.id in team_users:
        logbotmessage(message)
        bot.send_chat_action(message.chat.id,'typing')
        bot.send_message(message.chat.id,'Пожалуйста наберите /help')
        bot.send_chat_action(message.chat.id,'typing')
        
@bot.message_handler(func=lambda message:message.text == exchange+'Валюта' , content_types=['text'])
def valuta(message):
    if message.chat.id in team_users:
        logbotmessage(message)
        bot.send_chat_action(message.chat.id,'typing')
        id_dollar = "R01235"
        id_evro = "R01239"
        valuta = ET.parse(urllib.request.urlopen("http://www.cbr.ru/scripts/XML_daily.asp?date_req"))
        for line in valuta.findall('Valute'):
            id_v = line.get('ID')
            if id_v == id_dollar:
                rub = line.find('Value').text
                sdollar = "" + rub + " рублей"
            if id_v == id_evro:
                rub = line.find('Value').text
                sevro = "" + rub + " рублей" 
        bot.send_message(message.chat.id,"Курс валют ЦБ:\n"+"USD(Доллар США): " +sdollar+"\nEUR(Евро): "+sevro)
        sbervaluta(message)

def sbervaluta(message):
    try:
        r = requests.get('http://kurs24.ru/sbrf.html')
        data = r.text
        soup = BeautifulSoup(data, "html.parser")
        tables = soup.findChildren('table')
        # This will get the first (and only) table. Your page may have more.
        my_table = tables[0]
        # You can find children with multiple tags by passing a list of strings
        rows = my_table.findChildren(['th', 'tr'])
        i = 0
        for row in rows:
            if i==7:
                break
            else:
                cells = row.findChildren('td')
                for cell in cells:
                    value = cell.string
                    if  value is not None:
                        i=i+1
                        if i==2:
                            usdbuy=re.sub(r'\s', '', value)
                        elif i==3:
                            usdsell=re.sub(r'\s', '', value)
                        elif i==4:
                            eurbuy=re.sub(r'\s', '', value)
                        elif i==5:
                            eursell=re.sub(r'\s', '', value)
        string = "Курс валют Сбербанка:\n USD(Доллар США):\n Покупка:" + usdbuy +"\n Продажа:"+ usdsell +" \nEUR(Евро):\n Покупка:"+ eurbuy +"\n Продажа:"+ eursell
        bot.send_message(message.chat.id,string)
    except Exception as e:
        logboterror(message,e)
        print(e)
        bot.send_message(message.chat.id,"Данные не удалось со скрэпить \n c сайта Сбербанка \n напишите в обратную связь \n либо зайдите позже")

def kotirovki(message):
    try:
        r = requests.get('http://rur.bz/bank/sberbank/slitki/')
        data = r.text
        soup = BeautifulSoup(data, "html.parser")
        tables = soup.findChildren('table')                                                                    
        # This will get the first (and only) table. Your page may have more.
        my_table = tables[0]
        # You can find children with multiple tags by passing a list of strings
        rows = my_table.findChildren(['th', 'tr'])
        i = 0
        for row in rows:
            if i==6:
                break
            else:
                cells = row.findChildren('td')
                for cell in cells:
                    value = cell.string
                    if  value is not None:
                        i=i+1
                        if i==2:
                            usdbuy=re.sub(r'\s', '', value)
                        elif i==3:
                            usdsell=re.sub(r'\s', '', value)
                        elif i==5:
                            eurbuy=re.sub(r'\s', '', value)
                        elif i==6:
                            eursell=re.sub(r'\s', '', value)
        stringmetal = "Золото:\n Покупка:" + usdbuy +"\n Продажа:"+ usdsell +" \nСеребро:\n Покупка:"+ eurbuy +"\n Продажа:"+ eursell
        r = requests.get('http://ru.investing.com/commodities/brent-oil')
        data = r.text
        soup = BeautifulSoup(data, "html.parser")
        time = soup.find("span",{"class":"bold pid-8833-time"})
        value = soup.find("span",{"id":"last_last"})
        change = soup.find("span",{"class":"pid-8833-pc"})
        changeproc = soup.find("span",{"class":"pid-8833-pcp"})
        stringBrent = "Нефть на "+ str(time.text) +" \n"+ "Brent: " +str(value.text)+" "+str(change.text)+" "+str(changeproc.text)
        r = requests.get('http://ru.investing.com/commodities/crude-oil')
        data = r.text
        soup = BeautifulSoup(data, "html.parser")
        valuewti = soup.find("span",{"id":"last_last"})
        changewti = soup.find("span",{"class":"pid-8849-pc"})
        changeprocwti = soup.find("span",{"class":"pid-8849-pcp"})
        stringWTI = "WTI: " +str(valuewti.text) +" "+str(changewti.text)+" "+str(changeprocwti.text)
        stringOil = stringBrent+"\n"+stringWTI
        stringkot= stringmetal+"\n"+stringOil
        bot.send_message(message.chat.id,str(stringkot))
    except Exception as e:
        logboterror(message,e)
        print(e)
        bot.send_message(message.chat.id,"Данные не удалось со скрэпить \n c сайта Сбербанка \n напишите в обратную связь \n либо зайдите позже")

#Акции
def share(message):
    try:
        r = requests.get('http://ru.investing.com/equities/sberbank-rossii-oao?cid=13711#')
        data = r.text
        soup = BeautifulSoup(data, "html.parser")
        time = soup.find("span",{"class":"bold pid-13711-time"})
        value = soup.find("span",{"id":"last_last"})
        change = soup.find("span",{"class":"pid-13711-pc"})
        changeproc = soup.find("span",{"class":"pid-13711-pcp"})
        stringShare = "Акции на "+ str(time.text) +" цена в руб \n"+ "SBER: " +str(value.text)+" "+str(change.text)+" "+str(changeproc.text)
        bot.send_message(message.chat.id,stringShare)
        r = requests.get('http://ru.investing.com/equities/sberbank-p_rts')
        data = r.text
        soup = BeautifulSoup(data, "html.parser")
        time = soup.find("span",{"class":"bold pid-13712-time"})
        value = soup.find("span",{"id":"last_last"})
        change = soup.find("span",{"class":"pid-13712-pc"})
        changeproc = soup.find("span",{"class":"pid-13712-pcp"})
        stringShare = "Акции(прив.) на "+ str(time.text) +" цена в руб \n"+ "SBER_p: " +str(value.text)+" "+str(change.text)+" "+str(changeproc.text)
        bot.send_message(message.chat.id,stringShare)
    except Exception as e:
        logboterror(message,e)
        print(e)
        bot.send_message(message.chat.id,"Данные не удалось со скрэпить \n c сайта Сбербанка \n напишите в обратную связь \n либо зайдите позже")

'''
#Голос
@bot.message_handler(content_types=['voice'])
def voice(message):
    if message.chat.id in team_users:
        #bot.send_message(message.chat.id,'Голос ')
        #Для забора файла через реквест
        file_id=message.voice.file_id
        voice_url = bot.get_file(file_id).file_path
        voice_content = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, voice_url)).content
        voice_text = bot_voice.Speech.stt(content=voice_content, request_id=file_id)
        bot.send_message(
            message.chat.id,
            text=voice_text
        )
        if voice_text == 'прибыль за 6 месяцев 2016 года' or voice_text == 'прибыль за 6 месяцев 2016':
            bot.send_message(message.chat.id,'29 558млн')
        if voice_text == 'Меню' or voice_text == 'меню' or voice_text == 'открыть меню' or voice_text =='выйти в меню':
            processmenu(message)
'''
#Голосовое меню
@bot.message_handler(func=lambda message:message.text == 'голос' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'Голос' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'голосовое управление' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'Голосовое управление' , content_types=['text'])
def voicetxtmenu(message):
    if message.chat.id in team_users:
        bot.send_message(message.chat.id,"Есть три основных раздела"+"\n"+"голосового управления"+"\n"+"Выберите:")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row('Итого Банк')
        markup.row('rКБ','rРБ')                
        bot.send_message(message.chat.id, "Выберите:", reply_markup=markup)            


#Декораторы под голосовое
#Итого банка -прибыль
@bot.message_handler(func=lambda message:message.text == 'Прибыль' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'прибыль' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'pl' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'Pl' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'PL' , content_types=['text'])
def voicetxtpribil(message):
    if message.chat.id in team_users:
        bot.send_message(message.chat.id,"на 01.10.2016\n=43,2 млрд.")
        photo = open(r'C:\Users\user\Desktop\SRBbot 1.5\profit.JPG', 'rb')
        bot.send_chat_action(message.chat.id,'upload_photo')
        bot.send_photo(message.chat.id,photo)   

#Итого банка -операционный доход
@bot.message_handler(func=lambda message:message.text == 'операционный доход' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'Операционный доход' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'oi' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'Oi' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'OI' , content_types=['text'])
def voicetxtoi(message):
    if message.chat.id in team_users:
        bot.send_message(message.chat.id,"на 01.10.2016\n=96,3 млрд.")
        photo = open(r'C:\Users\user\Desktop\SRBbot 1.5\od.JPG', 'rb')
        bot.send_chat_action(message.chat.id,'upload_photo')
        bot.send_photo(message.chat.id,photo)


#Итого банка -cost income
@bot.message_handler(func=lambda message:message.text == 'cost income' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'Cost income' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'ci' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'CI' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'Ci' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'c/i' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'C/I' , content_types=['text'])
def voicetxtci(message):
    if message.chat.id in team_users:
        bot.send_message(message.chat.id,"на 01.10.2016\n=31,1%")
        photo = open(r'C:\Users\user\Desktop\SRBbot 1.5\CIR.JPG', 'rb')
        bot.send_chat_action(message.chat.id,'upload_photo')
        bot.send_photo(message.chat.id,photo)        

#Итого банка -уровень операционного риска
@bot.message_handler(func=lambda message:message.text == 'уровень операционного риска' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'Уровень операционного риска' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'Уор' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'uor' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'УОР' , content_types=['text'])
def voicetxtuor(message):
    if message.chat.id in team_users:
        bot.send_message(message.chat.id,"на 01.10.2016\n=0.45%")
        photo = open(r'C:\Users\user\Desktop\SRBbot 1.5\uor.JPG', 'rb')
        bot.send_chat_action(message.chat.id,'upload_photo')
        bot.send_photo(message.chat.id,photo)

#Итого банка -операционные расходоы
@bot.message_handler(func=lambda message:message.text == 'операционные расходы' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'операционные расходы' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'Oc' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'oc' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'OC' , content_types=['text'])
def voicetxtoc(message):
    if message.chat.id in team_users:
        bot.send_message(message.chat.id,"на 01.10.2016\n=-29,9 млрд.")
        photo = open(r'C:\Users\user\Desktop\SRBbot 1.5\oc.JPG', 'rb')
        bot.send_chat_action(message.chat.id,'upload_photo')
        bot.send_photo(message.chat.id,photo)


#РБ -активы
@bot.message_handler(func=lambda message:message.text == 'активы РБ' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'Активы РБ' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'активы розничного блока' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'Активы розничного блока' , content_types=['text'])
def voicetxtRBassets(message):
    if message.chat.id in team_users:
        bot.send_message(message.chat.id,"за 3Q2016 = 400,1 млрд")
        photo = open(r'C:\Users\user\Desktop\SRBbot 1.5\RBassets.JPG', 'rb')
        bot.send_chat_action(message.chat.id,'upload_photo')
        bot.send_photo(message.chat.id,photo)
        
#РБ -пассивы
@bot.message_handler(func=lambda message:message.text == 'пассивы РБ' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'Пассивы РБ' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'пассивы розничного блока' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'Пассивы розничного блока' , content_types=['text'])
def voicetxtRBliab(message):
    if message.chat.id in team_users:
        bot.send_message(message.chat.id,"за 3Q2016 = 1 143 млрд")
        photo = open(r'C:\Users\user\Desktop\SRBbot 1.5\RBliabilities.jpg', 'rb')
        bot.send_chat_action(message.chat.id,'upload_photo')
        bot.send_photo(message.chat.id,photo)

#КБ -активы
@bot.message_handler(func=lambda message:message.text == 'активы КБ' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'Активы КБ' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'активы корпоративного блока' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'Активы корпоративного блока' , content_types=['text'])
def voicetxtKBassets(message):
    if message.chat.id in team_users:
        bot.send_message(message.chat.id,"за 3Q2016 = 772,2млрд")
        photo = open(r'C:\Users\user\Desktop\SRBbot 1.5\KBassets.jpg', 'rb')
        bot.send_chat_action(message.chat.id,'upload_photo')
        bot.send_photo(message.chat.id,photo)        

#КБ -пассивы
@bot.message_handler(func=lambda message:message.text == 'пассивы КБ' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'Пассивы КБ' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'пассивы корпоративного блока' , content_types=['text'])
@bot.message_handler(func=lambda message:message.text == 'Пассивы корпоративного блока' , content_types=['text'])
def voicetxtKBliab(message):
    if message.chat.id in team_users:
        bot.send_message(message.chat.id,"за 3Q2016 = 409,8млрд")
        photo = open(r'C:\Users\user\Desktop\SRBbot 1.5\KBliabilities.jpg', 'rb')
        bot.send_chat_action(message.chat.id,'upload_photo')
        bot.send_photo(message.chat.id,photo)



#Голос
@bot.message_handler(content_types=['voice'])
def voice(message):
    try:
        if message.chat.id in team_users:
            #bot.send_message(message.chat.id,'Голос ')
            #Для забора файла через реквест
            file_id=message.voice.file_id
            voice_url = bot.get_file(file_id).file_path
            voice_content = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, voice_url)).content
            voice_text = bot_voice.Speech.stt(content=voice_content, request_id=file_id)
            bot.send_message(message.chat.id,text=voice_text)
            logbotvoice(message,voice_text)
            #if voice_text == 'прибыль':
                #photo = open(r'C:\Users\ivan\Desktop\SRBbot 1.1\profit.png', 'rb')
                #bot.send_chat_action(message.chat.id,'upload_photo')
                #bot.send_photo(message.chat.id,photo)            
            #if voice_text == 'прибыль за 6 месяцев 2016 года' or voice_text == 'прибыль за 6 месяцев 2016':
                #bot.send_message(message.chat.id,'29 558млн')
            if voice_text == 'Меню' or voice_text == 'меню' or voice_text == 'открыть меню' or voice_text =='выйти в меню':
                processmenu(message)
            #if voice_text == 'Заявка' or voice_text == 'заявка' or voice_text == 'принять заявку' or voice_text == 'завка':
                #reg(message)
            if voice_text == 'голосовое управление' or voice_text == 'что можно узнать голосом' or voice_text == 'что ты можешь ответить' or voice_text == 'голос' or voice_text =='Голос':
                voicetxtmenu(message)
            #if voice_text == 'Прибыль':
                #photo = open(r'C:\Users\ivan\Desktop\SRBbot 1.1\profit.png', 'rb')
                #bot.send_chat_action(message.chat.id,'upload_photo')
                #bot.send_photo(message.chat.id,photo)
            #Итого банк
            if voice_text == 'прибыль' or voice_text == 'Прибыль':
                voicetxtpribil(message)
            if voice_text == 'операционный доход' or voice_text == 'Операционный доход' :
                voicetxtoi(message)
            if voice_text == 'операционные расходы' or voice_text == 'Операционные расходы':
                voicetxtoc(message)
            if voice_text == 'резервы':
                bot.send_message(message.chat.id,"на 01.10.2016\n=-28,4 млрд.")
                photo = open(r'C:\Users\user\Desktop\SRBbot 1.1\profit.png', 'rb')
                #bot.send_chat_action(message.chat.id,'upload_photo')
                #bot.send_photo(message.chat.id,photo)
            if voice_text == 'комиссия' or voice_text == 'комиссии':
                bot.send_message(message.chat.id,"на 01.10.2016\n=26,7 млрд.")
                photo = open(r'C:\Users\user\Desktop\SRBbot 1.1\profit.png', 'rb')
                #bot.send_chat_action(message.chat.id,'upload_photo')
                #bot.send_photo(message.chat.id,photo)
            if voice_text == 'cost income' or voice_text =='сир' or voice_text == 'Cost income' or voice_text =='Сир':
                voicetxtci(message)
            if voice_text == 'уровень операционного риска' or voice_text == 'Уровень операционного риска':
                voicetxtuor(message)
            #КБ
            if voice_text == 'активы кб' or voice_text == 'активы к б' or voice_text == 'Активы кб' or voice_text == 'Активы к б':
                voicetxtKBassets(message)
            if voice_text == 'пассивы кб' or voice_text == 'пассивы к б' or voice_text == 'Пассивы кб' or voice_text == 'Пассивы к б':
                voicetxtKBliab(message)
            r'''    
            if voice_text == 'прибыль кб':
                bot.send_message(message.chat.id,"на 01.10.2016\n=15,6 млрд.")
                photo = open(r'C:\Users\ivan\Desktop\SRBbot 1.1\profit.png', 'rb')
                bot.send_chat_action(message.chat.id,'upload_photo')
                bot.send_photo(message.chat.id,photo)
            if voice_text == 'операционный доход кб':
                bot.send_message(message.chat.id,"на 01.10.2016\n=45,4 млрд.")
                photo = open(r'C:\Users\ivan\Desktop\SRBbot 1.1\profit.png', 'rb')
                bot.send_chat_action(message.chat.id,'upload_photo')
                bot.send_photo(message.chat.id,photo)
            if voice_text == 'резервы кб':
                bot.send_message(message.chat.id,"на 01.10.2016\n=-22,2 млрд.")
                photo = open(r'C:\Users\ivan\Desktop\SRBbot 1.1\profit.png', 'rb')
                bot.send_chat_action(message.chat.id,'upload_photo')
                bot.send_photo(message.chat.id,photo)
            if voice_text == 'комиссия кб' or voice_text == 'комиссии кб':
                bot.send_message(message.chat.id,"на 01.10.2016\n=12,2 млрд.")
                photo = open(r'C:\Users\ivan\Desktop\SRBbot 1.1\profit.png', 'rb')
                bot.send_chat_action(message.chat.id,'upload_photo')
                bot.send_photo(message.chat.id,photo)
            if voice_text == 'cost income кб':
                bot.send_message(message.chat.id,"на 01.10.2016\n=16.7%")
                photo = open(r'C:\Users\ivan\Desktop\SRBbot 1.1\profit.png', 'rb')
                bot.send_chat_action(message.chat.id,'upload_photo')
                bot.send_photo(message.chat.id,photo)
            '''
            #РБ
            if voice_text == 'активы рб' or voice_text == 'активы р б' or voice_text == 'Активы рб' or voice_text == 'Активы р б':
                voicetxtRBassets(message)
            if voice_text == 'пассивы рб' or voice_text == 'пассивы р б' or voice_text == 'Пассивы рб' or voice_text == 'Пассивы р б':
                voicetxtRBliab(message)
            r'''
            if voice_text == 'прибыль рб':
                bot.send_message(message.chat.id,"на 01.10.2016\n=25,6 млрд.")
                photo = open(r'C:\Users\ivan\Desktop\SRBbot 1.1\profit.png', 'rb')
                bot.send_chat_action(message.chat.id,'upload_photo')
                bot.send_photo(message.chat.id,photo)
            if voice_text == 'операционный доход рб':
                bot.send_message(message.chat.id,"на 01.10.2016\n=54,7 млрд.")
                photo = open(r'C:\Users\ivan\Desktop\SRBbot 1.1\profit.png', 'rb')
                bot.send_chat_action(message.chat.id,'upload_photo')
                bot.send_photo(message.chat.id,photo)
            if voice_text == 'резервы рб':
                bot.send_message(message.chat.id,"на 01.10.2016\n=-6,2 млрд.")
                photo = open(r'C:\Users\ivan\Desktop\SRBbot 1.1\profit.png', 'rb')
                bot.send_chat_action(message.chat.id,'upload_photo')
                bot.send_photo(message.chat.id,photo)
            if voice_text == 'комиссия рб' or voice_text == 'комиссии рб':
                bot.send_message(message.chat.id,"на 01.10.2016\n=14,5 млрд.")
                photo = open(r'C:\Users\ivan\Desktop\SRBbot 1.1\profit.png', 'rb')
                bot.send_chat_action(message.chat.id,'upload_photo')
                bot.send_photo(message.chat.id,photo)
            if voice_text == 'cost income рб':
                bot.send_message(message.chat.id,"на 01.10.2016\n=41.8%")
                photo = open(r'C:\Users\ivan\Desktop\SRBbot 1.1\profit.png', 'rb')
                bot.send_chat_action(message.chat.id,'upload_photo')
                bot.send_photo(message.chat.id,photo)
                '''
            '''
            #Итого банк
            if voice_text == 'прибыль на 1 октября 2016' or voice_text =='прибыль на 1 октября 2016 года':
                bot.send_message(message.chat.id,"37 665 млн")
            if voice_text == 'прибыль на 1 января 2017'or voice_text =='прибыль на 1 октября 2016 года' :
                bot.send_message(message.chat.id,"54 755 млн")
            if voice_text == 'операционный доход на 1 октября 2016' or voice_text == 'операционный доход на 1 октября 2016 года':
                bot.send_message(message.chat.id,"96 540 млн")
            if voice_text == 'операционный доход на 1 января 2017' or voice_text == 'операционный доход на 1 января 2016 года':
                bot.send_message(message.chat.id,"130 880 млн")
            if voice_text == 'расходы на резервы на 1 октября 2016' or voice_text == 'расходы на резервы на 1 октября 2016 года':
                bot.send_message(message.chat.id,"-28 442 млн")
            if voice_text == 'расходы на резервы на 1 января 2017' or voice_text == 'расходы на резервы на 1 января 2017 года':
                bot.send_message(message.chat.id,"-32 816 млн")
            if voice_text == 'комиссии на 1 октября 2016' or voice_text =='комиссия на 1 октября 2016' or voice_text == 'комиссии на 1 октября 2016' or voice_text =='комиссия на 1 октября 2016':
                bot.send_message(message.chat.id,"26 660 млн")
            if voice_text == 'комиссии на 1 января 2017' or voice_text =='комиссия на 1 января 2017' or voice_text == 'комиссии на 1 октября 2016' or voice_text =='комиссия на 1 октября 2016':
                bot.send_message(message.chat.id,"37 221 млн")
            if voice_text == 'cost income на 1 октября 2016' or voice_text == 'cost income на 1 октября 2016 года':
                bot.send_message(message.chat.id,"31,5%")
            if voice_text == 'cost income на 1 января 2017' or voice_text == 'cost income на 1 января 2017 года':
                bot.send_message(message.chat.id,"32,6%")
            if voice_text == 'уровень операционного риска':
                bot.send_message(message.chat.id,"На текущую дату: 422\nмлн.(0,45%,4 место)")
            #КБ
            if voice_text == 'прибыль кб на 1 октября 2016' or voice_text =='прибыль кб на 1 октября 2016 года':
                bot.send_message(message.chat.id,"37 665 млн")
            if voice_text == 'прибыль кб на 1 января 2017'or voice_text =='прибыль кб на 1 октября 2016 года' :
                bot.send_message(message.chat.id,"54 755 млн")
            if voice_text == 'операционный доход кб на 1 октября 2016' or voice_text == 'операционный доход кб на 1 октября 2016 года':
                bot.send_message(message.chat.id,"96 540 млн")
            if voice_text == 'операционный доход кб на 1 января 2017' or voice_text == 'операционный доход кб на 1 января 2016 года':
                bot.send_message(message.chat.id,"130 880 млн")
            if voice_text == 'расходы кб на резервы на 1 октября 2016' or voice_text == 'расходы кб на резервы на 1 октября 2016 года':
                bot.send_message(message.chat.id,"-28 442 млн")
            if voice_text == 'расходы кб на резервы на 1 января 2017' or voice_text == 'расходы кб на резервы на 1 января 2017 года':
                bot.send_message(message.chat.id,"-32 816 млн")
            if voice_text == 'комиссии кб на 1 октября 2016' or voice_text =='комиссия  кб на 1 октября 2016' or voice_text == 'комиссии кб на 1 октября 2016' or voice_text =='комиссия  кб на 1 октября 2016':
                bot.send_message(message.chat.id,"26 660 млн")
            if voice_text == 'комиссии кб на 1 января 2017' or voice_text =='комиссия кб на 1 января 2017' or voice_text == 'комиссии  кб на 1 октября 2016' or voice_text =='комиссия кб на 1 октября 2016':
                bot.send_message(message.chat.id,"37 221 млн")
            if voice_text == 'cost income кб на 1 октября 2016' or voice_text == 'cost income кб на 1 октября 2016 года':
                bot.send_message(message.chat.id,"31,5%")
            if voice_text == 'cost income кб на 1 января 2017' or voice_text == 'cost income кб на 1 января 2017 года':
                bot.send_message(message.chat.id,"32,6%")              
            #РБ
            if voice_text == 'прибыль рб на 1 октября 2016' or voice_text =='прибыль рб на 1 октября 2016 года':
                bot.send_message(message.chat.id,"37 665 млн")
            if voice_text == 'прибыль рб на 1 января 2017'or voice_text =='прибыль рб на 1 октября 2016 года' :
                bot.send_message(message.chat.id,"54 755 млн")
            if voice_text == 'операционный доход рб на 1 октября 2016' or voice_text == 'операционный доход  рб на 1 октября 2016 года':
                bot.send_message(message.chat.id,"96 540 млн")
            if voice_text == 'операционный доход рб на 1 января 2017' or voice_text == 'операционный доход рб на 1 января 2016 года':
                bot.send_message(message.chat.id,"130 880 млн")
            if voice_text == 'расходы на резервы рб на 1 октября 2016' or voice_text == 'расходы на резервы рб на 1 октября 2016 года':
                bot.send_message(message.chat.id,"-28 442 млн")
            if voice_text == 'расходы на резервы рб на 1 января 2017' or voice_text == 'расходы на резервы рб на 1 января 2017 года':
                bot.send_message(message.chat.id,"-32 816 млн")
            if voice_text == 'комиссии рб на 1 октября 2016' or voice_text =='комиссия рб на 1 октября 2016' or voice_text == 'комиссии рб на 1 октября 2016' or voice_text =='комиссия рб на 1 октября 2016':
                bot.send_message(message.chat.id,"26 660 млн")
            if voice_text == 'комиссии рб на 1 января 2017' or voice_text =='комиссия рб на 1 января 2017' or voice_text == 'комиссии рб на 1 октября 2016' or voice_text =='комиссия рб на 1 октября 2016':
                bot.send_message(message.chat.id,"37 221 млн")
            if voice_text == 'cost income рб на 1 октября 2016' or voice_text == 'cost income рб на 1 октября 2016 года':
                bot.send_message(message.chat.id,"31,5%")
            if voice_text == 'cost income рб на 1 января 2017' or voice_text == 'cost income рб на 1 января 2017 года':
                bot.send_message(message.chat.id,"32,6%")
                '''
    except Exception as e:
        logboterror(message,e)
        #Cообщение для правльного использования голосового управления
        bot.send_message(message.chat.id,"Неправильное использование голосового управления!'+'/n'+'Зажмите клавишу микрофона,скажите команду,отпустите клавишу!")
        print(e)

#То,что можно узнать голосом
@bot.message_handler(func=lambda message:message.text == 'Итого Банк' , content_types=['text'])
def voiceIB(message):
    if message.chat.id in team_users:
        #bot.send_message(message.chat.id,"Итого Банк: \nПрибыль на 1 октября 2016 \nПрибыль на 1 января 2017 \nОперационный доход на 1 октября 2016 \nОперационный доход на 1 января 2017 \nРасходы на резервы на 1 октября 2016 \nРасходы на резервы на 1 января 2017 \nКомиссии(я) на 1 октября 2016 \nКомиссии(я) на 1 января 2017 \nCost/Income на 1 октября 2016 \nCost/Income на 1 января 2017 \nУровень операционного риска")
        bot.send_message(message.chat.id,"Итого Банк: \nПрибыль(Pl)\nОперационный доход(Oi) \nОперационные расходы(Oc) \nCost/Income(Ci) \n Уровень операционного риска(Уор)")

@bot.message_handler(func=lambda message:message.text == 'rКБ' , content_types=['text'])
def voiceKB(message):
    if message.chat.id in team_users:
        bot.send_message(message.chat.id,"КБ: Активы КБ \nПассивы КБ")
        #bot.send_message(message.chat.id,"Итого Банк: \nПрибыль КБ  \nОперационыый доход КБ\nРезервы КБ\nКомиссии(я) КБ\nCost/Income КБ")

@bot.message_handler(func=lambda message:message.text == 'rРБ' , content_types=['text'])
def voiceRB(message):
    if message.chat.id in team_users:
        bot.send_message(message.chat.id,"РБ: Активы РБ \nПассивы РБ")
        #bot.send_message(message.chat.id,"Итого Банк: \nПрибыль РБ  \nОперационыый доход РБ\nРезервы РБ\nКомиссии(я) РБ\nCost/Income РБ")

#Функция логгирования всех текстовых сообщений
def logbotmessage(message):
    try:
        non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
        client = MongoClient()
        db = client.trylogbotmessage
        lastname=message.chat.last_name
        mcid=message.chat.id
        firstname=message.chat.first_name
        mtype=message.chat.type
        mdate=message.date
        mid=message.message_id
        mctype=message.content_type
        mtext=str(message.text).translate(non_bmp_map)
        db.trylogbotmessage.insert({
        'last_name': lastname,
        'id': mcid,
        'first_name': firstname,
        'type': mtype,
        'date': mdate,
        'message_id': mid,
        'content_type': mctype,
        'text': mtext
        })
        #cursor = db.trylogbotmessage.find()
        #for document in cursor:
            #print(document)
    except Exception as e:
        logboterror(message,e)
        print(e)

#Функция логгирования всех голосовых сообщений
def logbotvoice(message,voicetext):
    try:
        non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
        client = MongoClient()
        db = client.trylogbotmessage
        lastname=message.chat.last_name
        mcid=message.chat.id
        firstname=message.chat.first_name
        mtype=message.chat.type
        mdate=message.date
        mid=message.message_id
        mctype='voice'
        mtext=voicetext
        db.trylogbotmessage.insert({
        'last_name': lastname,
        'id': mcid,
        'first_name': firstname,
        'type': mtype,
        'date': mdate,
        'message_id': mid,
        'content_type': mctype,
        'text': mtext
        })
        #cursor = db.trylogbotmessage.find()
        #for document in cursor:
            #print(document)
    except Exception as e:
        logboterror(message,e)
        print(e)

#Функция логгирования ошибок
def logboterror(message,e):
    client = MongoClient()
    db = client.trylogbotmessage
    date = message.date
    db.trylogbotmessage.insert({
    'date' : date,
    'error' : e
    })
    
#функция сокращения ссылок
def urlshorter(bigurl):
    shortener = Shortener('Google', api_key=api_key)
    shorturl=format(shortener.short(bigurl))
    return shorturl

                    
if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(str(e))
            sleep(5)
            continue
            #рестатр приложения -так не работает 
            #os.execv(sys.executable,['python']+sys.argv)
            #os.kill
            #time.sleep(15)
            #print(e.message)


