import pickle

List=[]


List=[["Gujrat Fire & Safety Agency", 22.299774, 73.202672, "0265 242 8519"],
["Vadodara Central Fire Station",22.300031, 73.201142,"0265 241 3754"],
["Mavdi Road Fire Station",22.271225, 70.789847,"093277 07487"],
["JMC Fire and emergency services",22.467840, 70.067657,"Not Available"],]

 
pickle.dump( List, open( "save.p", "wb" ) )
