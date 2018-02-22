print("enter your public key")
i=input()
j=input()

k=int(i)
n=int(j)

print("now enter your message")
q=input()


def wordscramble (loc):
   
    r=''

    while len(loc) != 0:
                r= r + str(ord(loc[0]))
                loc= loc[1:]

    return int(r)



M = wordscramble(q)


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



def encrypt (M,k,n):

    print("Here is your encrypted message")

    return binexp(1,M,k,n)


print (encrypt(M,k,n))












