"""
To avoid confusion.

NSOS = Shares outstanding
TA = Total Assets
NPPE = Net Property, Plant & Equipment
GW = Goodwill
TL = Total Liabilities
MV = Market Value

"""

def fun(NSOS, TA, NPPE, GW, TL, MV):
    AA = TA - NPPE - GW - TL
    FV = AA / NSOS
    print("Fair value is", FV)
    print("Market to Fair value margin", MV/FV)
    print("Market Value", MV)
    

a = int(input("Number of shares outstanding: "))
b = int(input("Total Assets: "))
c = int(input("Net Property Plant & Equipment: "))
d = int(input("Goodwill: "))
e = int(input("Total Liabilities: "))
f = float(input("Market Value: "))
        
fun(a,  b, c, d, e, f)


    
    
    
    
