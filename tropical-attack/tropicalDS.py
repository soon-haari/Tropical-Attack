#!/usr/bin/env python
# coding: utf-8

'''
code source: https://shpilrain.ccny.cuny.edu/tropicalDS.txt
'''


# In[1]:


import numpy as np
import sys
import random
import hashlib
from collections import OrderedDict
from numpy.polynomial import polynomial as P
import time
import tracemalloc
import psutil
import os


# In[2]:


# please specify your parameters here
m="Hello world"
d=100
r=127


# In[3]:


def one_v_poly(deg,r=127):
  T=[[random.randint(0,r),0]]#used to store the result

  for i in range(1,deg+1):
    T.append([random.randint(0,r),i])

  # print(T)
  # if [0,0] in T:
  #   T=T[1:]
  return T#assume we have T[0][0]+T[1][0]*x+T[2][0]*x^2+...



# # Tropical Algebra

# In[4]:


#let us code each monomial as an array
#the first element indicates the coeff and the second element indicates the deg
#2⨂x will be coded as [2,1]
#5 will be coded as [5,0]
#2⨂x⨂5=[2,1]+[5,0]=[7,1]
def mono_otimes(A,B):#otimes for monomials
  res=np.zeros(2)

  res[0]=A[0]+B[0]
  res[1]=A[1]+B[1]
  return res

def find_min_coef(A):#A is an array of array whose sec element are the same; find the minimal monomial of the same deg
  if len(A)==1:
    return A[0]
  else:
    res=np.zeros(2)
    res[0]=A[0][0]
    res[1]=A[0][1]
    for i in A:
      res[0]=min(res[0],i[0])
      # res[1]=min(res[1],i[1])
    return res


def mono_oplus(A): #where A is an array of monomials
  d=OrderedDict()
  for i in A: #go through all the monomials
    if i[1] in d:#check whether degree can be found in the dict
      d[i[1]].append(i)
    else:
      d[i[1]]=[i]
  # print(d)

  sums=[]
  for key,value in d.items():
    if len(value)==1: #there is only one monomial of deg key
      sums.append(value[0])
    else:
      sums.append(find_min_coef(value))
  return sums

#(A⊕B⊕C)⨂(D⊕E⊕F)
def poly_otimes_poly(A,B):
  res=[]
  for i in A:
    for j in B:
      temp=np.zeros(2)
      temp[0]=i[0]+j[0]
      temp[1]=i[1]+j[1]
      res.append(temp)
  # print(res)
  return mono_oplus(res)


# In[5]:


def pol_times_pol2(R,S):
    d=len(R)-1
    g=len(S)-1
    res=OrderedDict()
    for m in range(d+g+1):
        res[m]=[]
        for i in range(m+1):
            if i<=d and m-i<=g:
                res[m].append(R[i][0]+S[m-i][0])
    pol_res=[]
    for key,value in res.items():
        pol_res.append([min(value),key])
    return pol_res


# In[19]:


# pol_times1=[]
# for i in range(100):
#     start = time.time()
#     poly_otimes_poly(X,Y)
#     end = time.time()
#     pol_times1.append(end - start)
# print("running time1(pol times pol:",np.average(pol_times1))

# pol_times2=[]
# for i in range(100):
#     start = time.time()
#     pol_times_pol2(X,Y)
#     end = time.time()
#     pol_times2.append(end-start)
# print("running times2(poly times poly):",np.average(pol_times2))


# # Key Generation

# In[10]:


def hashing_to_P(m,deg=150):
  #hashing 512
  hex_str=hashlib.sha512(m.encode()).hexdigest()#SHA-512 hash
  hex_int=int(hex_str,16)#convert to decimal number
  bin_str=format(hex_int,'b')#convert to binary number

  #concatenate 3 copies of the bit string
  B=""
  for i in range(3):
    B=B+bin_str
  #print(len(B)) #error check: bit string of len 1536

  int7s=[]#convert each 7-bit block to an integer
  for i in range(deg+1):
    int7=B[(7*i):(7*i+7)]
    int7s.append(int(int7,2))#convert to decimal
  # print(min(int7s))
  # #print(len(int7s))#we need 151 coefficients; additional one for constant

  Ps=[]
  for i in range(deg+1):
    Ps.append([int7s[i],i])
  # print(len(Ps))
  return Ps


# # Scheme

# In[11]:


#two private polynomials
X=one_v_poly(d,r)
Y=one_v_poly(d,r)
# print(X)
# print(Y)

#public
M=pol_times_pol2(X,Y)

#signing
P=hashing_to_P(m,d)
U=one_v_poly(d,r)
V=one_v_poly(d,r)
N=pol_times_pol2(U,V)
sig_vec=[]
sig_vec.append(pol_times_pol2(pol_times_pol2(P,X),U))
sig_vec.append(pol_times_pol2(pol_times_pol2(P,Y),V))
sig_vec.append(N)


# In[13]:


def pol_arr_tostring(A): 
    str_vec=[]
    for i in A:
        mo=[]
        for j in i:
            mo.append(str(j))
        str_vec.append("_".join(mo))
    return " ".join(str_vec)
        


# # verification

# In[16]:


#verification 1: check that the degree of the polynomial

def deg_check_for_pol(A,deg,c):
  d=OrderedDict()
  for i in A: #go through all the monomials
    if i[1] in d:#check whether degree can be found in the dict
      d[i[1]].append(i)
    else:
      d[i[1]]=[i]
  return c*deg in d

#check neither polynomial in the signature pair is a constant multiple
#(in the tropical sense) of P⨂M or P⨂N
def constant_multiple_check(A,B):
  if len(A)==len(B): #please make sure that A and B have the same deg before the check
    coefs=np.zeros(len(A))
    for i in range(len(A)):
      coefs[i]=A[i][0]-B[i][0]#diff between coefficients for varying deg in A and B
    return len(np.unique(coefs))==1
  else:
    print("tropical polys have diff degrees")

  
def check_coef(A,d,r):
  cnt=0
  for i in A:
    if i[0]>=0 and i[0]<=r*3:
      cnt+=1
  return cnt==3*d+1


def check_coef2(A,d,r):
    cnt=0
    for i in A:
        if i[0]>=0 and i[0]<=2*r:
            cnt+=1
    return cnt==(2*d+1)
            
def verification_all3():
  if deg_check_for_pol(sig_vec[0],d,3) & deg_check_for_pol(sig_vec[1],d,3) & deg_check_for_pol(sig_vec[2],d,2) :
    poly_toCheck1=pol_times_pol2(P,M)
    poly_toCheck2=pol_times_pol2(P,N)
    exp1=not (constant_multiple_check(sig_vec[0],poly_toCheck1))
    exp2=not (constant_multiple_check(sig_vec[1],poly_toCheck1))
    exp3=not (constant_multiple_check(sig_vec[0],poly_toCheck2))
    exp4=not (constant_multiple_check(sig_vec[1],poly_toCheck2))
    if exp1 & exp2 & exp3 & exp4:
      if check_coef(sig_vec[0],d,r) & check_coef(sig_vec[1],d,r) & check_coef2(sig_vec[2],d,r):
        W1=pol_times_pol2(pol_times_pol2(pol_times_pol2(P,X),U),pol_times_pol2(pol_times_pol2(P,Y),V))
        W2=pol_times_pol2(pol_times_pol2(pol_times_pol2(P,P),M),N)
        print(np.allclose(W1,W2))
      else:
        print("coefficient not within the range")
    else:
      print("verification part2b failed")
  else:
    print("verification part2a failed; signature not accepted")

verification_all3()

