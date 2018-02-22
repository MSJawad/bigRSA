from milrab import genprime

print ("choose your e")
c=input()

p = genprime (600)
q = genprime (600)
e = int(c)
z = (p-1)*(q-1)


def gcd (x, y):
    
    
    if x%y == 0:
             return y

    else:
             return gcd(y,x%y)
    

def EEAforrsa (r,q,x,y,startxy,startq):
    
    r = r + [(r[startxy] % r[startxy+1])]
    q = q + [r[startxy] // r[startxy+1]]
    x = x + [(x[startxy]-(q[startq]*x[startxy+1]))]
    y = y + [(y[startxy]-(q[startq]*y[startxy+1]))]

    if r[len(r)-1] == 1:
         if y[len(y)-1] > 0:
             return y[len(y)-1]


         else:
             return y[len(y)-1] + r[0]
                   
    else:
         return EEAforrsa (r,q,x,y,startxy+1,startq+1)
    


def keys (p,q,e,z):
    
    if e < z :
        if  gcd (z,e) == 1:
                 print (" this is your public key ")
                 print ([e, p*q])
            

                 print (" this is your private key")
                 print ( [EEAforrsa ([z,e],[0,0],[1,0],[0,1],0,2) , p*q])

        
        else: print ("gcd is not 1")
    
    else: print ("your e is out of range" )


keys (p,q,e,z)


