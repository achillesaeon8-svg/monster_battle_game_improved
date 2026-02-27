import pygame
from os.path import join 
from os import walk

WINDOW_WIDTH, WINDOW_HEIGHT = 1280,720 

COLORS = {
    'black': '#000000',
    'red': '#ee1a0f',
    'gray': 'gray',
    'white': '#ffffff',
}

MONSTER_DATA = {
	'Paraprano':   {'element': 'plant', 'health': 90},
	'Paralto':     {'element': 'plant', 'health': 120},
	'Paratone':    {'element': 'plant', 'health': 130},
	'Ardaze':      {'element': 'fire',  'health': 70},
	'Armight':     {'element': 'fire',  'health': 100},
	'Blazedillo':  {'element': 'fire',  'health': 120},
	'Dracby':      {'element': 'water', 'health': 50},
	'Seagon':      {'element': 'water', 'health': 80},
	'Bermudrac':   {'element': 'water', 'health': 100},
	'Vesuverex':   {'element': 'fire',  'health': 150},
	'Vegaptor':    {'element': 'plant', 'health': 100},
	'Dragoshell':  {'element': 'plant', 'health': 100},
	'Gengharoo':   {'element': 'fire',  'health': 60},
	'Lustar':      {'element': 'water', 'health': 70},
}

ABILITIES_DATA = {
	'scratch': {'damage': 20,  'element': 'normal', 'animation': 'scratch'},
	'spark':   {'damage': 35,  'element': 'fire',   'animation': 'fire'},
	'nuke':    {'damage': 50,  'element': 'fire',   'animation': 'explosion'},
	'splash':  {'damage': 30,  'element': 'water',  'animation': 'splash'},
	'shards':  {'damage': 50,  'element': 'water',  'animation': 'ice'},
    'spiral':  {'damage': 40,  'element': 'plant',  'animation': 'green'}
}

ELEMENT_DATA = {
    'fire':   {'water': 0.5, 'plant': 2,   'fire': 1,   'normal': 1},
    'water':  {'water': 1,   'plant': 0.5, 'fire': 2,   'normal': 1},
    'plant':  {'water': 2,   'plant': 1,   'fire': 0.5, 'normal': 1},
    'normal': {'water': 1,   'plant': 1,   'fire': 1,   'normal': 1},
}