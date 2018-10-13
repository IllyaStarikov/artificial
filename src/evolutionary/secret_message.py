#!/usr/local/bin/python3
#
# secret-message.py
# src
#
# Created by Illya Starikov on 10/12/18.
# Copyright 2018. Illya Starikov. MIT License.
#


class SecretMessage:
    def __init__(self, message):
        """Initialize a Secret Message object.

        :message (str): The secret message to hide.
        """
        self.__message = message

    def letters_match(self, message):
        """Determine how many characters match the secret message.

        Note:
            The message length and the secret message length must be the same length (accessed via the length property).


        :message (str): The message to compare the secret message to.
        :returns (int): The number of characters matched.
        """
        return sum(self.__message[char] == message[char] for char in range(len(message)))

    @property
    def length(self):
        """Get the length of the secret message.

        :returns (int): The length of the secret message.
        """
        return len(self.__message)
