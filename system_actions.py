#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
12 December 2017
.. codeauthor: svitlana vakulenko
    <svitlana.vakulenko@gmail.com>

System (Expert) actions extracted from transcripts

'''

# transition probabilities of replies to user intents with system actions
intent2action = {
        'greeting': ['greeting']
    }

actions = {
            'greeting': [
                "Hey",
                "Hallo",
                "Hi",
                "Yo",
                "Hello",
                "Hi! How can I help you?",
                "Hi, i would like to present you my new website full of data sets!",
                "how are you ? ^^"
                ],

            'confirm': [
                "Yes, I can help you with that.",
                "Okay, I will look into it",
                "Ok",
                "Sure",
                "Oh yes of course, give me a second"
            ]
           }