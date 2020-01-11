#!/usr/bin/python3

# do pairwise triangulation to estimate local surface height, but try
# to also build up a tracking structure so we could use and refine
# this as we proceed through the matching process.

import argparse
from matplotlib import pyplot as plt
from matplotlib import collections as mc
import numpy as np
from tqdm import tqdm

from props import getNode

from lib import groups
from lib import project
from lib import srtm

parser = argparse.ArgumentParser(description='Keypoint projection.')
parser.add_argument('project', help='project directory')
args = parser.parse_args()

proj = project.ProjectMgr(args.project)
proj.load_images_info()
proj.load_match_pairs()

print("Collecting stats:")
dist_stats = []
segments = []
for i, i1 in enumerate(tqdm(proj.image_list)):
    ned1, ypr1, quat1 = i1.get_camera_pose()
    for j, i2 in enumerate(proj.image_list):
        if i <= j:
            continue
        if not i2.name in i1.match_list:
            continue
        if len(i1.match_list[i2.name]) == 0:
            continue
        ned2, ypr2, quat2 = i2.get_camera_pose()
        dist = np.linalg.norm(np.array(ned2) - np.array(ned1))
        dist_stats.append( [ dist, len(i1.match_list[i2.name]) ] )
        segments.append( [(ned1[1], ned1[0]), (ned2[1], ned2[0])] )
        
dist_stats = np.array(dist_stats)
plt.figure()
plt.plot(dist_stats[:,0], dist_stats[:,1], 'ro')

fig, ax = plt.subplots()
lc = mc.LineCollection(segments)
ax.add_collection(lc)
ax.autoscale()
ax.axis('equal')

remain_list = {}
for i1 in proj.image_list:
    remain_list[i1.name] = True
    
group_list = groups.load(proj.analysis_dir)
for group in group_list:
    points = []
    for name in group:
        i1 = proj.findImageByName(name)
        if name in remain_list:
            del remain_list[name]
        ned1, ypr1, quat1 = i1.get_camera_pose()
        points.append( (ned1[1], ned1[0]) )
    points = np.array(points)
    ax.plot(points[:,0], points[:,1], '*')

points = []
for name in remain_list:
    i1 = proj.findImageByName(name)
    ned1, ypr1, quat1 = i1.get_camera_pose()
    points.append( (ned1[1], ned1[0]) )
points = np.array(points)
ax.plot(points[:,0], points[:,1], '*')

plt.show()

