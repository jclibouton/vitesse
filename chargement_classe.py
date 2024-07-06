'''original organie en classe sans commentaires'''

"""Test remote"""


import numpy as np
import pandas as pd

class Essai(object):
    """On initie """
    def __init__(self,nom):
        self.reactifs=pd.read_excel('reactifs.xlsx', usecols="A:B,D,F:Y")
        self.produits = pd.read_excel('produits.xlsx', usecols="A:AE")
        self.enthalprod= pd.read_excel('produits.xlsx',usecols=("D"))
        self.compo= pd.read_excel('compo.xlsx', usecols="A:J")
        self.mat_compo = pd.read_excel('MATRICE INVERSE REDUITE.xlsx',sheet_name='MATRICE INVERSE STATIQUE', usecols="B:O")
        self.prod_stat = pd.read_excel('MATRICE INVERSE REDUITE.xlsx', sheet_name='MATRICE INVERSE STATIQUE',usecols="A")
        self.nom=nom
    def calcul(self):
        data_enthal_prod=self.enthalprod.iloc[4:22,0]
        """"liste_ explosifs est une liste Python et non pandas.Il s'agit de la liste des composants de l'explosif (NOM) """
        data_reactifs=[self.compo.loc[(self.compo['Explosif']) == self.nom]]
        """print('data_reactifs:\n',data_reactifs)"""
        g = data_reactifs[0]
        """print('g=:\n',g)"""
        nom_mp_quant_dens_sol = g.loc[:, lambda g: ['Explosif','Densite','Solubilisation','Reactif','quantite']]
        print('repartition des reactifs:\n',nom_mp_quant_dens_sol)
        """on accroche les densités qui viennent du tableau reactifs"""
        tablecompo= pd.merge(nom_mp_quant_dens_sol, self.reactifs, left_on="Reactif", right_on="NOM", how="inner")
        nombre_reactifs=len(tablecompo)
        """print('tablecompo:\n',tablecompo)"""
        print(nombre_reactifs)
        """Calcul de masse_totale,densite,DeltaH_reactifs,DeltaH_sol,Compo_produits"""
        densi = 0
        enthalpie_solution=0
        masse_totale =0
        DeltaH_reactifs=0
        Delta_Hsol=0
        teneur_en_eau= tablecompo.loc[(tablecompo['NOM']=='Eau')]['quantite']
        print("teneur en eau:",teneur_en_eau)
        """print (tablecompo)"""
        for j in range(len(tablecompo)):
            m = tablecompo.at[j, 'quantite']
            dd = tablecompo.at[j,'DENSITE']
            if tablecompo.at[j,'Solubilisation'] == 'T':
                Delta_Hsol=Delta_Hsol + m * tablecompo.at[j,'H.SOLU(ERG/G)']
            masse_totale= masse_totale+m
            densi = densi + (m / dd)
        densinit = tablecompo.at[j,'Densite']
        densi = 1000 / densi
        ratio = densinit / densi
        print("dens-init:", densi)
        print('densinit/densite_compacte',ratio)
        moles_reactifs=tablecompo['quantite']/tablecompo['PM(G)']
        moles_reactifs=np.array(moles_reactifs)
        print('moles_reactifs=\n',pd.DataFrame(moles_reactifs.T,index=tablecompo['Reactif']))
        print('Energie de solubilisation',f"{Delta_Hsol:.2e}",'ou',f"{Delta_Hsol/4.1856/1e+10:.2e}",'cal/g')
        """print(tablecompo['DELTAH(ERG/M)'])"""
        deltaH= (moles_reactifs.T).dot(tablecompo['DELTAH(ERG/M)'])
        print('enthalpie(cal/g):',deltaH/4185.6)
        print(f"{deltaH:.2e}erg/kg")  # '.2e' signifie deux chiffres après la virgule en notation exponentielle
        """print("solu",tablecompo.at[j,'Solubilisation'])"""
        """print(f"La masse totale est:{masse_totale} g")"""
        moles=pd.Series(moles_reactifs).T
        """print('molesde reactifs:\n',moles)"""
        tablecompo=tablecompo.fillna(0)
        tablered=tablecompo.iloc[:,14:28]
        """print('tablered=\n',pd.DataFrame(tablered))"""
        compo_elements= ((moles).dot(tablered))
        print('compo_elements:\n',compo_elements)
        """Inversion de la matrice pour pouvoir rechercher les produits statiques(14 par 14)"""
        print('mat_compo:\n',self.mat_compo)
        inv_matrix = np.linalg.inv(self.mat_compo)
        print('Matrice inverse pour calculer les produits:\n',pd.DataFrame(inv_matrix,index=self.prod_stat.iloc[:],columns=compo_elements.index))
        compo_produits=(compo_elements.dot(inv_matrix))
        print('Composition des produits:\n',pd.DataFrame(compo_produits,index=self.prod_stat.iloc[:]))
        """On ajoute H2 et Na2SO3,etat,pm,vir"""
        """====================================================================================="""
        new_row=np.array(['H2'])
        index=3
        prod_stat_corr=np.insert(self.prod_stat,index,new_row,axis=0)
        new_row=np.array([0])
        compo_produits_corr=np.insert(compo_produits,index,new_row,axis=0)
        print(compo_produits_corr)
        """============================================================================================="""
        new_row=np.array([['NaCl'],['KaCl']])
        index=[7,7]
        result=np.insert(prod_stat_corr,index,new_row,axis=0)
        prod_stat_corr=result
        index=[7,7]
        new_row=np.array([0,0])
        result=np.insert(compo_produits_corr,index,new_row,axis=0)
        compo_produits_corr=result


        new_row = np.array(['Na2SO3'])
        index = [13]
        result = np.insert(prod_stat_corr, index, new_row, axis=0)
        prod_stat_corr = result
        index = [13]
        new_row = np.array([0])
        result = np.insert(compo_produits_corr, index, new_row, axis=0)
        compo_produits_corr = result
        """=========================================================================================="""
        prod= pd.DataFrame(compo_produits_corr, index=prod_stat_corr[:])
        reac=pd.DataFrame(moles_reactifs.T,index=tablecompo['Reactif'])
        """=========================================================================================="""
        """Soufre"""
        print('à verifier',prod)
        b=prod.iat[5,0]
        if b>prod.iat[14,0]:
            prod.iat[14, 0] -= b
            prod.iat[0, 0] += b
            prod.iat[13, 0] -= b
        else:
            """b = prod.iat[5, 0]
            b -= prod.iat[14, 0]
            prod.iat[0, 0] += prod.iat[14, 0]
            prod.iat[13, 0] = prod.iat[14, 0]
            prod.iat[5, 0] = b"""
            print('presence de SO2')




        print(prod)
        """Chlore"""
        if prod.iat[6,0]>0:
            b= prod.iat[6,0]/2
            if prod.iat[14,0]>b:
                print('essaico2')
                print(prod.iat[0, 0])
                print(b)
                prod.iat[0, 0]+=b
                print(prod.iat[0, 0])
                print('NaCl')
                print(prod.iat[7, 0])
                prod.iat[7, 0]+=2*b
                print(prod.iat[7, 0])
                print("h2o")
                print(prod.iat[1, 0])
                prod.iat[1, 0]+=b
                print(prod.iat[1, 0])
                prod.iat[6, 0]-=2*b
                prod.iat[14,0]-=b
                b=0
            """else:
                b-=prod.iat[14,0]
                prod.iat[0, 0]+=b
                prod.iat[7, 0]+=2*b
                prod.iat[6, 0]-=2*b
                prod.iat[1, 0]+=b
                prod.iat[14, 0]=0
                if (prod.iat[15,0]>0 and b>0):
                prod.iat[15, 0]-=b
                prod.iat[0, 0]+=b
                prod.iat[8, 0]+=b*2
                prod.iat[1, 0]+=b
                prod.iat[6, 0]-=2*b
        else:"""
            """b-=prod.iat[15,0]
            prod.iat[0, 0]+=b
            prod.iat[8, 0]+=prod.iat[15,0]
            prod.iat[1, 0]+=prod.iat[15,0]
            prod.iat[15, 0]=0"""
            print("Présence d'HCl")
        b=0
        """Hydrogène"""
        b=-2*prod.iat[2,0]
        if prod.iat[2,0]<0 :
            b=-2*prod.iat[2,0]
            prod.iat[3, 0]=b
            prod.iat[1, 0]-=b
            prod.iat[2, 0]=0

        """Enthalpie des produits"""








        """=========================================================================================="""
        print ('NaCl:\n',prod.iat[7,0])
        print ('HCl avant ajustement:',prod.iat[6,0])
        """if 'Chlorure de sodium' in reac[0]:

            prod.iat[7,0]=reac.at['Chlorure de sodium',0]
            prod.iat[6, 0] -=  prod.iat[7, 0]"""
        print ('HCl après ajustement:',prod.iat[6,0])




        prod =np.array(prod)
        data_enthal_prod=np.array(data_enthal_prod)
        print('Composition des produits:\n',pd.DataFrame(prod))
        print('Enthalpie des produits:\n',data_enthal_prod)

        enthalpie_prod=(prod.T).dot(data_enthal_prod)
        print('enthalpie des produits', enthalpie_prod)
        qp=-(enthalpie_prod-deltaH)/4.1856/1e+10
        print('qp',qp)
        n_mole_gaz=0
        for i in range(0,6,1):
            n_mole_gaz+=prod[i,0]
        vol_gaz= n_mole_gaz*22.4
        print('Volume des gaz en l/kg:',vol_gaz)
        qv=qp+.592*n_mole_gaz
        print('qv: ',qv)
        print('Bilan en O2 en mole/kg:',-b/2)






if __name__=='__main__':
    nom_explosif =('mel7')

    f = Essai(nom_explosif)
    f.calcul()




