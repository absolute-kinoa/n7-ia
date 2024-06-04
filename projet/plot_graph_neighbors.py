import numpy as np
import pandas as pd
from tqdm import tqdm
from dataclasses import dataclass
from swarm_sim import *
import networkx as nx
import random
from matplotlib.widgets import Slider


# Chemin vers le fichier source des donnes
PATH = './output50.csv'
# Nombre de temps a analyser
MAXTEMPS = 100
# Constantes de distance
MAX_RANGE = 60
MID_RANGE = 30
MIN_RANGE = 20

satellites_nb=50
chosen_range=MIN_RANGE

###
### Manipulation du fichier source.
###

print("### Importation des données ### ")
df = pd.read_csv(PATH, header=0)

print("### Reformatage des données : ajout d'un index sur le temps ### ")
#On genere un tableau qui servira d'index de temps pour chaque echantillon
names = ['1']
i=2
while len(names)<11603 :
  names.append(''+ str(i))
  i=i+1

#On modifie le df pour ajouter en tete de colone notre index de temps
save = df.columns
df.columns = names
df.loc[-1] = save
df.index = df.index + 1 
df = df.sort_index()
print("### Reformatage des données : ajout d'un index sur les satelites ### ")
# On genere les noms des satelite 
satnames = ['satx1']
i=1
while len(satnames)<(3*satellites_nb) :
  if (i !=1):
    satnames.append('satx'+ str(i))
  satnames.append('saty'+ str(i))
  satnames.append('satz'+ str(i))
  i=i+1
# On applique notre index
df['coords'] = satnames
df = df.set_index('coords', drop=True)

# On transpose notre df pour avoir le temps en ligne et les coordonees de satelites en colonnes
dft = df.transpose()


###
### Mise en forme de la donnee en memoire (Creation des structures de donnees necessaires)
###

# On itère sur les elements de notre df pour en extraire des Node comme implantes dans swarm_sim
def GetNodes(time):
  nodes = {}
  id = 1
  while id < (satellites_nb+1):
    node = Node(id - 1, dft.loc[str(time)]['satx'+str(id)], dft.loc[str(time)]['saty'+str(id)], dft.loc[str(time)]['satz'+str(id)])
    nodes[id - 1] = node
    id = id +1
  return nodes  

# Cette fonction permet, a partir du swarm, d'extraire une matrice d'adjaceance qui prend en compte le cout des differents liens.
def GetWeightedMatrix(Swarm):
  # On prend comme base le reseau avec une portee minimale puis on vient ajouter les chemins necessitant plus de portee en multipliant par un coefficient.
  matrix20 = Swarm.neighbor_matrix(MIN_RANGE)
  matrix40 = Swarm.neighbor_matrix(MID_RANGE)
  matrix60 = Swarm.neighbor_matrix(MAX_RANGE)
  x=0
  y=0 
  while x < len(matrix20) :
    y=0
    while y < len(matrix20):
      if (matrix20[x][y] == 0 and matrix40[x][y] == 1) :
        matrix20[x][y]=2
      if (matrix20[x][y] == 0 and matrix40[x][y] == 0 and matrix60[x][y] == 1):
        matrix20[x][y]=3 
      y=y+1
    x=x+1
  return matrix20

def CreateNeighbors(Swarm, Range=MAX_RANGE):
  for t in range(len(Swarm)):
    matrix = Swarm[t].neighbor_matrix(Range)
    # print(len(matrix))
    for i in range(int(np.floor(len(matrix)/2))):
      for j in range(int(np.floor(len(matrix)/2))):
        if (matrix[i][j]>0):
          node_i = Swarm[t].get_node_by_id(i)
          node_j = Swarm[t].get_node_by_id(j)

          node_i.add_neighbor(node_j)
          node_j.add_neighbor(node_i)

print("### Génération des tableaux de nodes en fonction du temps ### ")
def GetPositions(): 
  Positions = {}
  temps = 0
  while temps < MAXTEMPS:
    Positions[temps] = GetNodes(temps+1)
    temps = temps+1
  return Positions
Positions = GetPositions()

print("### Génération des swarms correspondants a chaque instants ###")
def InitSwarms(Positions):
  Swarms = {}
  temps = 0
  while temps < MAXTEMPS:
    Swarms[temps] = Swarm(MAX_RANGE, list(Positions[temps].values()))
    temps = temps+1
  return Swarms

Swarms = InitSwarms(Positions)
CreateNeighbors(Swarms, chosen_range)

def getBiggestSubset(swarm):
  max_index,max_nodes = 0,swarm[0]
  for k,v in swarm.items():
    if v.get_size() > max_nodes.get_size():
      max_nodes = v
      max_index = k

  # print(max_index)
  return swarm[max_index]


# Generate fireswarm
def generateFireSwarms(swarms):
  s_list = list()
  for i in range(len(swarms)):
    fire_swarm = swarms[i].ForestFire()
    s_list.append(getBiggestSubset(fire_swarm))
  return s_list

def generateRNS(swarms):
  s_list = list()
  for i in range(len(swarms)):
    fire_swarm = swarms[i].ForestFire()
    s_list.append(getBiggestSubset(fire_swarm))
  return s_list

max_fireswarms =  generateFireSwarms(Swarms)# Init fireswarm
# max_rns = generateRNS(Swarms)

# Display fireSwarm contents
def displayFSwarmContent(fireSwarm):
  for k in fireSwarm.keys():
    print(str(k) + " ->" + str(fireSwarm[k]))


print("=============================")
print("Showcasing Neighbor Graph")
print("=============================")

fig = plt.figure(figsize=(20,20))

# Add subplots to the figure
ax0 = fig.add_subplot(221, projection='3d')
ax1 = fig.add_subplot(222, projection='3d')

# =====================
# Creation du Slider
# # =====================
axtime = fig.add_axes([0.25, 0.1, 0.65, 0.03])
t_slider = Slider(
          ax=axtime,
          label="Time (in seconds)",
          valmin=0,
          valmax=MAXTEMPS-1,
          valinit=0,
          orientation="horizontal",
          valstep=int(MAXTEMPS/2))

def update(val):
    time_val = int(val)
    Swarms[time_val].plot_edges(ax0, time=time_val, range=-1, title="Regular graph")
    max_fireswarms[time_val].plot_edges(ax1, time=time_val, range=-1, title="Forestfire graph")
    fig.canvas.draw_idle()

update(0)
t_slider.on_changed(update)
plt.show()
