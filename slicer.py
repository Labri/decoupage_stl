#!/usr/bin/env python3

"""
projet BPI, Stenzel et Cesar, 
Du le 16 décembre 2016 a 23h59
"""

import sys
import struct

#lecture_fichier()
def lecture_fichier():
    """
    lecture du fichier stl au format binaire
    On récupère les coordonnées des triangles et on les stock dans une meme liste
    """
    source = open(sys.argv[1], 'rb')
    source.read(80)
    nbr_tri = struct.unpack_from('i', source.read(4))
    l_tri = []
    x_min, y_min, y_max, z_min, z_max = 0, 0, 0, 0, 0
    print(nbr_tri)
    for k in range(nbr_tri[0]):
        tri = struct.unpack_from(('f' * 3 * 4) + 'h' , source.read(50))
        l_tri.append(tri[3:12]) # vecteur normal ne nous interresse pas

        for c in [2, 5, 8]: #on recherche lintervalles des Z 
            if tri[c] < z_min:
                z_min = tri[c]
            if tri[c] > z_max:
                z_max =tri[c]
        for c in [1, 4, 7]: #on recherche lintervale des y
            if tri[c] < y_min:
                y_min = tri[c]
            if tri[c] > y_max:
                y_max =tri[c]
        for c in [0, 3, 6]: #recherche du x_min
            if tri[c] < x_min:
                x_min = tri[c]

                
    source.close()
    return l_tri, z_min, z_max, x_min, y_min, y_max
        
                
def decoupage(liste, z_min, z_max):
    """
    on decoupe la liste de tous nos triangle en une liste de n tranches 
    qui correspondent au triangle intersecté par la tranche
    """
    tranches = []
    nbr = int(sys.argv[2])
    for k in range(nbr):
        tranches.append([])
    pas = abs(z_max - z_min) / nbr
    for tri in liste: #on va parcourir la liste que une fois plus avantageux
#si le nbr de tranche est petit devant le nbr de triangle (ce qui sera notre cas)
        for k in range(nbr):
            position, i = [False] * 3, 0
            for c in [2, 5, 8]:
                if tri[c] < z_min + pas * k :
                    position[i] = True
                i+=1
            if position != [True] * 3 and position != [False] * 3:
                tranches[k].append((tri, position))

    return tranches, pas


def creation_svg(tranches, couche,  destination, z_min, pas, x_min, y_min, y_max):
    """
    creation du fichier svg, de la couche indiquée.
    On récupère les points dintersections puis on trace des lignes svg
    """
    dest = open(destination, 'w')
    dest.write('<svg height="' + str(abs(y_max - y_min)) + '" width="' + str(abs(y_max - y_min)) + '">\n')

    for couple in tranches[couche]:
        tri, position =couple[0],  couple[1]
        elt_true, elt_false = [], []

        for k in range(len(position)):
            if position[k]:
                elt_true.append(k)
            else:
                elt_false.append(k)
        if len(elt_true) > len(elt_false):
            p1, p2, p3 = tri[3 * elt_false[0]::], tri[3 * elt_true[0]::], tri[3 * elt_true[1]::]
        else:
            p1, p2, p3 = tri[3 * elt_true[0]::], tri[3 * elt_false[0]::], tri[3 * elt_false[1]::]
        
        x_1, x_2, x_3 = p1[0], p2[0], p3[0]
        y_1, y_2, y_3 = p1[1], p2[1], p3[1]
        z_1, z_2, z_3 = p1[2], p2[2], p3[2]
        
        z_plan = z_min + pas*couche
        x_a, y_a = x_1 - (x_2 - x_1)*(z_1 - z_plan)/(z_2 - z_1), y_1 - (y_2 - y_1)*(z_1 - z_plan)/(z_2 - z_1)
        x_b, y_b = x_1 - (x_3 - x_1)*(z_1 - z_plan)/(z_3 - z_1), y_1 - (y_3 - y_1)*(z_1 - z_plan)/(z_3 - z_1)
        
        dest.write('<line x1="' + str(x_a+ abs(x_min)) + '" y1="' + str(y_a+ abs(y_min)) + '" x2="' + str(x_b+ abs(x_min)) + '" y2="' + str(y_b+ abs(y_min)) + '" style="stroke:rgb(255,0,0);stroke-width:0.5" />\n')
    dest.write('</svg>')
    dest.close()

#******************************************************************************************************************************************************
    
liste, z_min, z_max, x_min, y_min, y_max = lecture_fichier()
tranches, pas = decoupage(liste, z_min, z_max)
for k in range(int(sys.argv[2])):
    destination = str(k) + '.svg'
    creation_svg(tranches, k, destination, z_min, pas, x_min, y_min, y_max)
