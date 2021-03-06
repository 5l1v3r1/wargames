#!/usr/bin/env python

# The matasano crypto challenges - Set 5 Challenge 37 (http://cryptopals.com/sets/5/challenges/37/)
#
# Copyright (c) 2015 - Albert Puigsech Galicia (albert@puigsech.com)
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.


import sys
import random
import struct
import math
import hashlib

# Cryptohelper from https://github.com/apuigsech/cryptohelper
from cryptohelper import *

N = 0xffffffffffffffffc90fdaa22168c234c4c6628b80dc1cd129024e088a67cc74020bbea63b139b22514a08798e3404ddef9519b3cd3a431b302b0a6df25f14374fe1356d6d51c245e485b576625e7ec6f44c42e9a637ed6b0bff5cb6f406b7edee386bfb5a899fa5ae9f24117c4b1fe649286651ece45b3dc2007cb8a163bf0598da48361c55d39a69163fa8fd24cf5f83655d23dca3ad961c62f356208552bb9ed529077096966d670c354e4abc9804f1746c08ca237327ffffffffffffffff
g = 2
k = 3
username = "person"
password = "good password"


side_S_info = {}
side_C_info = {}


def sha256wrapper(m):
    return hashlib.sha256(m).digest()


def dh_generate_key(g, p):
    u = random.randint(0, p-1)
    return u,modexp(g, u, p)


def pack_string_to_int(str):
    num = 0
    for i in reversed(range(len(str))):
        e = len(str)-i-1
        num += ord(str[i])*256**e
    return num


#S
def step_0_initialize(info):
    salt = random.randint(0,0xffffffff)
    x = pack_string_to_int(hashlib.sha256("{0}{1}".format(salt, password)).digest())
    v = modexp(g, x, N)
    info['salt'] = salt
    info['v'] = v
  

#C
def step_1_generate_kpub(info):
    a = 0
    kpub = 0
    info['a'] = a
    info['kpub'] = kpub
    return username, kpub


#S
def step_2_generate_kpub(info):
    b, kpub = dh_generate_key(g, N)
    kpub = k*info['v'] + kpub
    info['b'] = b
    info['kpub'] = kpub
    return info['salt'], kpub


#C
def step_3_compute_C(info, salt, kpub, password):
    S = 0
    info['salt'] = salt
    info['K'] = hashlib.sha256("{0}".format(S)).digest()


#S
def step_3_compute_S(info, kpub):
    u = pack_string_to_int(hashlib.sha256("{0}{1}".format(kpub, info['kpub'])).digest())
    S = modexp((kpub * modexp(info['v'], u, N)), info['b'], N)
    info['K'] = hashlib.sha256("{0}".format(S)).digest()


#C
def step_4_send_hash(info):
    return HMAC("{0}".format(info['salt']), info['K'], 64, sha256wrapper)


#S
def step_5_validate_hash(info, h):
    return (HMAC("{0}".format(info['salt']), info['K'], 64, sha256wrapper) == h)


def simulate_communication(password):
    username, kpub_A = step_1_generate_kpub(side_C_info)
    salt, kpub_B = step_2_generate_kpub(side_S_info)
    step_3_compute_C(side_C_info, salt, kpub_B, password)
    step_3_compute_S(side_S_info, kpub_A)
    h = step_4_send_hash(side_C_info)
    return step_5_validate_hash(side_S_info, h)


def main(argv):
    step_0_initialize(side_S_info)
    for pwd in ('good password', 'bad password 1', 'bad password 2'):
        if simulate_communication(pwd):
            status = "OK"
        else:
            status = "FAIL"
        print 'TRY: "{0}"\tACCESS {1}!'.format(pwd, status)


if __name__ == "__main__":
    main(sys.argv)