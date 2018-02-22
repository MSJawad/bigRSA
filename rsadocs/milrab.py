import random
import math


def binexp (result, base, exp ,modulo):

    while exp > 0:
        if int(exp) & 1 == 1:
            result= result*base
            result= result % modulo
            base = base*base
            base= base % modulo
            exp = exp >> 1

        else:
            base = base*base
            base= base % modulo
            exp = exp >> 1

    return result

def breakdown (n):

    b=0

    while n % 2 ==0:
        n= n//2
        n=int(n)
        b = b+1

    return [2,b,n]


def milrab1 (pro):

    oneless = pro - 1
    broken  = breakdown (oneless)
    expcont = broken[1]
    expon   = broken[2]
    base    = random.randrange (2, oneless - 1)
    drake   = binexp(1,base,expon,pro)

    if drake == 1 or drake == oneless:
        return True
    
    else:
        return milrab2(base,pro,expon,expcont)



def milrab2 (base,modulo,exponent,expcounter):
    
    counter = 0
    oneless = modulo - 1
    result  = 0

    while result != 1 and result!= oneless and counter < expcounter:
        result    = binexp (1,base,exponent,modulo)
        exponent  = exponent * 2
        counter   = counter + 1

    if result == oneless:
        return True

    else:
        return False
    

def genprime(k):
     r=100*(math.log(k,2)+1)
     a=2**(k-1)
     b=2**(k)
     while r>0:
         n = random.randrange(a,b)
         r-=1
         if n % 2 == 1:
             if milrab1(n) == True:
                 if milrab1(n) == True:
                     return n
     return genprime(k)



