import numpy as np
def random_date():
    days_to_add = np.arange(0, 360)
    random_date = np.datetime64('2018-01-01') + np.random.choice(days_to_add)
    return random_date
    
    
    
origins = ["UK",
    "Canada",
    "US",
    "Netherlands",
    "Sweden",
    "Australia"
]


#rechem table
drugs = ["RRS-PDM-35",
    "N-(4-bromophenyl)adamantan-2-amine",
    "Baclofen",
    "URB597",
    "5-MeO-DMT",
    "4-AcO-DET",
    "Loperamide",
    "Gabapentin",
    "Etizolam"
]
rechem_table = [["drug_name", "price", "date"]]
for drug in drugs:
    for i in range(20):
        price = np.random.randint(30,50)
        date = random_date()
        rechem_table.append([drug,price,date])


drugs = ["N-(4-bromophenyl)adamantan-2-amine",
    "Baclofen",
    "URB597",
    "5-MeO-DMT",
    "4-AcO-DET",
    "Loperamide",
    "Gabapentin",
    "Etizolam",
    "Meth",
    "Cannabis",
    "Cocaine"
]

#dn1 table
#for now we'll say one drug per seller, but in reality it will be one listing title per seller
dn1_table = [["drug_name", "price", "date", "seller", "origin"]]
for drug in drugs:
    for i in range(20):
        for i in range(np.random.randint(1,5)):
            price = np.random.randint(30,50)
            date = random_date()
            seller = "seller" + str(np.random.randint(1,10))
            origin = origins[np.random.randint(0,len(origins)-1)]
            dn1_table.append([drug,price,date,seller,origin])

drugs = ["RRS-PDM-35",
    "5-MeO-DMT",
    "Loperamide",
    "Gabapentin",
    "Meth",
    "Cannabis",
    "Cocaine",
    "Fentanyl",
    "Carfentanil",
    "Heroin"
]
#dn2 table
dn2_table = [["drug_name", "price", "date", "seller", "origin"]]
for drug in drugs:
    for i in range(20):
        for i in range(np.random.randint(1,5)):
            price = np.random.randint(30,50)
            date = random_date()
            seller = "seller" + str(np.random.randint(1,10))
            origin = origins[np.random.randint(0,len(origins)-1)]
            dn2_table.append([drug,price,date,seller,origin])