# RSA-Implementation


This project implements the encryption algorithm invented by Ron Rivest, Adi Shamir, and Leonard Adleman. It uses large, 
600-bit prime numbers to encrypt and decrypt numbers and text. It is one of the first public-key cryptosystems
and is still widely used to this day for data transmission. The difficulty in breaking RSA is similar to 
the np problem of integer factorization, and is therefore, incredibly dificult.


## Overview

milrab.py is the file that generates a prime using a given number of bits.

rsa.py is the file that generates the primes using milrab, asks for your preferred public value, and then proceeds to 
calculate the public and private keys for the program. With a successful input of e, it will produce two 
lists, one with the entire public key and the other with the private key.
(Please Note: with an unsuccessful public value it will produce the message: "GCD is not 1". Please do not panic.
This merely means the public value you have chosen is incompatible with the prime numbers produced.  
Please run the program again. If the problem persists you may want to consider changing the value of e as it may be 
a very divisible number with many unique prime factors)

encrypt.py will take in your public key credentials and your message and will give you an encrypted message.

decrypt.py will take in your private key credentials and your encrypted message and will decrypt the message for you.


## Dependancies:

random

math for the logarithmic function

## Author
Mohammad Solaiman Jawad

## Language(s)
Python

## License
This project is protected by the MIT License



*Criticism and advice is welcome and appreciated. for edits, please email me at solaimanjawad@gmail.com"



