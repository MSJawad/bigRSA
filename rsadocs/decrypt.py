print("enter your private key")
i=input()
j=input()

k=int(i)
n=int(j)

print("now enter your encrypted message")
q=input()
C=int(q)


def binexp (result, base, exp ,modulo):

    while exp > 0:
        if int (exp) & 1 == 1:
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



def decrypt (C,k,n):

    print("Here is your decrypted message")

    return binexp (1,C,k,n)


m = decrypt(C,k,n)
M = str (m) 

def wordunscramble (lon):

    r=''
    while len(lon) != 0:
        
        if lon[0] == '1':
                r= r + chr(int(lon[0:3]))
                lon= lon[3:]

        else:
                r= r + chr(int(lon[0:2]))
                lon= lon[2:]

    return r

print (wordunscramble (M))
