#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# Test
#############################
##########30/06/16###########
#############################

#hypothese : la balle se deplace d'un px par itération

import pygame
from pygame.locals import *
from math import pi, sqrt
from random import random, randint
from os import popen
from pygame.draw import line

def signAlea():
	x = 0
	while x == 0 :
		x = randint(-1,1)
	return x

def sign(x):
	if x < 0 :
		return -1
	else:
		return 1

def getSystemResolutionOnLinux():
	screen = popen("xrandr -q -d :0").readlines()[0]
	tmp = screen.split()
	return int( tmp[7] ) * 0.2, int( tmp[9][:-1] ) * 0.2

def appartenancePoint(x1, y1, x2, y2, w2, h2):
	if x2 <= x1 and y2 <= y1 and x1 < x2 + w2 and y1 < y2 +h2 :
		return 1
	else:
		return 0

def somme(l):
	s = 0
	for i in l:
		s += i
	return s

#ordre donner pour l'objet 1
def delimiterCollision(x1, y1, w1, h1, x2, y2, w2, h2):
	t = [ appartenancePoint(x1, y1, x2, y2, w2, h2) ]
	t += [ appartenancePoint(x1 + w1 - 1, y1, x2, y2, w2, h2) ]
	t += [ appartenancePoint(x1, y1 + h1 -1, x2, y2, w2, h2) ]
	t += [ appartenancePoint(x1 + w1 - 1, y1 + h1 - 1, x2, y2, w2, h2) ]
	s = somme(t)

	if s == 0 :
		return NULL
	elif s == 2 :
		if t[NO] and t[SO] :
			return RIGHT
		elif t[NE] and t[SE] :
			return LEFT
		elif t[NO] and t[NE] :
			return DOWN
		elif t[SO] and t[SE] :
			return UP
	elif s == 1 :
		if t[NO] :
			if appartenancePoint(x1, y1 + 1, x2, y2, w2, h2) :
				return RIGHT
			else:
				return DOWN
		elif t[NE] :
			if appartenancePoint(x1 + w1 - 1, y1 + 1, x2, y2, w2, h2) :
				return LEFT
			else:
				return DOWN
		elif t[SO] :
			if appartenancePoint(x1, y1 + h1 - 2, x2, y2, w2, h2) :
				return RIGHT
			else:
				return UP
		elif t[SE] :
			if appartenancePoint(x1 + w1 - 1, y1 + h1 - 2, x2, y2, w2, h2) :
				return LEFT
			else:
				return UP

def switch(x):
	if x:
		return False
	else:
		return True

def moveBallTrig(x, y, dt, ball_angle, V):
	return x + round( dt * V * cos(ball_angle) ), y - round( dt * V * sin(ball_angle) )

def moveBallVect(x, y, dt, v):
	return x + round( dt * v[X] ), y - round( dt * v[Y] )

#x1 : past, x2 : pres
def resoSysLinForAI(x1, y1, x2, y2, i):
	if x2 == x1 :
		return -1, 0, 0

	y1 += BALL_H // 2
	y2 += BALL_H // 2
	x = GAMER_POS_X[i]

	if i == DEUX :
		x1 += BALL_W
		x2 += BALL_W
	else:
		x += GAMER_W

	a = ( y2 - y1 ) / ( x2 - x1 )
	b = y1 - a * x1

	return int( a * x + b ), b ,a

def initBallAngle(ball_angle, a):
	ball_angle = pi / 2
	while pi / a <= ball_angle and ball_angle <= pi - pi / a or pi + pi / a <= ball_angle and ball_angle <= 2 * pi - pi / a :
		ball_angle = 2 * pi * random()
	return ball_angle

def initBallVit(V):
	vx = 0.0
	vy = 0.0
	while True :
		vx = V * random() * signAlea()
		vy = sqrt( V ** 2 - vx ** 2 ) * signAlea()
		if abs(vy) / V < 0.8 :#cos( pi / 5 ) ~ 0.8
			break
	return [ vx , vy ]

def changeBallVit(yb, yg, v, V):
	i = randint(0,1)
	i_ = ( i + 1 ) % 2
	d = V - abs(v[i])
	c = 0.0
	yb += BALL_H // 2
	yg += GAMER_H // 2

	if yg - GAMER_H // 2 <= yb and yb <= yg + GAMER_H // 2 :
		c = abs( ( yb - yg ) / ( GAMER_H // 2 ) ) * 0.75
	else:
		c = 0.75

	v[i] = v[i] + d * c * sign(v[i])
	v[i_] = sqrt( V ** 2 - v[i] ** 2 ) * sign(v[i_])

	return v

def printScore(font, score, cadre_score):
	cadre_score.fill(WHITE)
	tmp = pygame.Surface( ( int( CADRE_SCORE_W * 0.8 ) , int( CADRE_SCORE_H - CADRE_SCORE_W * 0.2 ) ) )
	tmp.fill(BLACK)
	cadre_score.blit(tmp, ( ( cadre_score.get_rect().w - tmp.get_rect().w ) // 2, ( cadre_score.get_rect().h - tmp.get_rect().h ) // 2 ))
	text_score = font.render( str(score[0]) + " - " + str(score[1]), 1, WHITE)
	cadre_score.blit(text_score, ( ( cadre_score.get_rect().w - text_score.get_rect().w ) // 2, ( cadre_score.get_rect().h - text_score.get_rect().h ) // 2 ))

def main():
	tps = [ 0.0 , 0.0 ]
	score = [ 0 , 0 ]
	gamer_pos_Y = [ [ 0 , 0 ] , [ 0 , 0 ] ]
	gamer_time = [ [ 0.0 , 0.0 ] , [ 0.0 , 0.0 ] ]
	gamer_move = [ STOP , STOP ]
	gamer_control = DEUX
	ball_pos = [ [ 0 , 0 ] , [ 0 , 0 ] ]
	ball_time = [ 0.0 , 0.0 ]
	ball_vit_norm = 400.0 / 1000 * WIDTH_SC / 1229#premier terme en px/s
	ball_vit_vect = [ ball_vit_norm * 0.85 , ball_vit_norm * sqrt(1-0.85**2) ]
	#ball_angle = pi / 2
	order = -1
	y = [ HEIGH_SC + 10 , -10 ]

	marge = randint(1, GAMER_H // 2)#MARGE >= 1 sinon c'est le chaos !
	a = [ 0.0 , 0.0 ]

	#ball_angle = initBallAngle(ball_angle, 2.2)
	#ball_vit_vect = initBallVit(ball_vit_norm)

	# Initialisation de la fenêtre d'affichage
	pygame.init()
	screen = pygame.display.set_mode((WIDTH_SC, HEIGH_SC), pygame.DOUBLEBUF | pygame.HWSURFACE)
	pygame.display.set_caption("Pong")

	bg = pygame.Surface(screen.get_size())

	gamer = pygame.Surface( ( GAMER_W , GAMER_H ) )
	gamer.fill(WHITE)
	for i in [ PRES , PAST ] :
		gamer_pos_Y[UN][i] = ( HEIGH_SC - GAMER_H ) // 2
		gamer_pos_Y[DEUX][i] = ( HEIGH_SC - GAMER_H ) // 2

	ball = pygame.Surface( ( BALL_W , BALL_H ) )
	ball.fill(BRIGHTBLUE)
	ball_pos[X][PAST] = ( WIDTH_SC - BALL_W ) // 2
	ball_pos[Y][PAST] = ( HEIGH_SC - BALL_H ) // 2

	croix = pygame.Surface( ( BALL_W , BALL_H ) )
	tmp = [ pygame.Surface( ( BALL_W // 4 , BALL_H ) ) , pygame.Surface( ( BALL_W , BALL_H // 4 ) ) ]
	croix.fill(BLACK)
	for i in range(2) :
		tmp[i].fill(RED)
		croix.blit(tmp[i], ( ( ( i + 1 ) % 2 ) * ( BALL_W // 2 - BALL_W // 8 ) , ( i % 2 ) * ( BALL_H // 2 - BALL_H // 8 ) ))
	croix.set_colorkey(BLACK)

	# Affichage d'un texte
	font = pygame.font.SysFont("arial", FONT_SIZE)

	cadre_score = pygame.Surface( ( CADRE_SCORE_W , CADRE_SCORE_H ) )
	textpos_cadre_score = cadre_score.get_rect()
	textpos_cadre_score.centerx = bg.get_rect().centerx
	textpos_cadre_score.y = int( HEIGH_SC * 0.05 )

	# Boucle d'évènements
	while 1:
		tps[PRES] = pygame.time.get_ticks()
		for event in pygame.event.get():
			if event.type == pygame.QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
				exit()
			elif ( event.type == MOUSEBUTTONDOWN and event.button ) == MB_LEFT or ( ball_pos[X][PRES] + BALL_W <= 0 or WIDTH_SC <= ball_pos[X][PRES] ) :
				ball_time[PAST] = tps[PRES]
				ball_pos[X][PAST] = ( WIDTH_SC - BALL_W ) // 2
				ball_pos[Y][PAST] = ( HEIGH_SC - BALL_H ) // 2
				#ball_angle = initBallAngle(ball_angle, 2.2)
				ball_vit_vect = initBallVit(ball_vit_norm)
			elif event.type == KEYDOWN and (event.unicode == 'w' or event.unicode == 'W') :
				gamer_move[UN] = DESC
				gamer_time[UN][PAST] = tps[PRES]
			elif event.type == KEYDOWN and (event.unicode == 'x' or event.unicode == 'X') :
				gamer_move[UN] = STOP
				gamer_pos_Y[UN][PAST] = gamer_pos_Y[UN][PRES]
			#elif event.type == KEYUP and (event.unicode == 'x' or event.unicode == 'X') :
				#gamer_move[UN] = False
			elif event.type == KEYDOWN and (event.unicode == 'c' or event.unicode == 'C') :
				gamer_move[UN] = MONT
				gamer_time[UN][PAST] = tps[PRES]
			#elif event.type == KEYUP and (event.unicode == 'c' or event.unicode == 'C') :
				#gamer_move[DEUX] = False
			#elif ( event.type == MOUSEBUTTONDOWN and event.button == MBSW_UP ) :#ajout d'un hertz
				#ball_vit_norm += 1.0 / 1000#vitesse en px/s
			#elif ( event.type == MOUSEBUTTONDOWN and event.button == MBSW_DOWN ) :
				#ball_vit_norm -= 1.0 / 1000#vitesse en px/s

		#ball_pos[X][PRES], ball_pos[Y][PRES] = moveBallTrig(ball_pos[X][PAST], ball_pos[Y][PAST], ball_time[PAST], tps[PRES], ball_angle)
		ball_pos[X][PRES], ball_pos[Y][PRES] = moveBallVect(ball_pos[X][PAST], ball_pos[Y][PAST], tps[PRES] - ball_time[PAST], ball_vit_vect)

		if ball_pos[X][PRES] + BALL_W <= 0 or WIDTH_SC <= ball_pos[X][PRES] :
			ball_time[PAST] = tps[PRES]
			ball_pos[X][PAST] = ( WIDTH_SC - BALL_W ) // 2
			ball_pos[Y][PAST] = ( HEIGH_SC - BALL_H ) // 2
			#ball_angle = initBallAngle(ball_angle, 2.2)
			ball_vit_vect = initBallVit(ball_vit_norm)
			if ball_pos[X][PRES] < 0 :
				score[1] += 1
			else:
				score[0] += 1
		###
		#Artificial Intelligence
		###
		if 0 < ball_pos[X][PRES] - ball_pos[X][PAST] :
			if gamer_control != DEUX :
				marge = randint(1, GAMER_H // 2)
			gamer_control = DEUX
		else:
			if gamer_control != UN :
				marge = randint(1, GAMER_H // 2)
			gamer_control = UN

		y[PAST] = y[PRES]
		y[PRES], a[0], a[1] = resoSysLinForAI(ball_pos[X][PAST], ball_pos[Y][PAST], ball_pos[X][PRES], ball_pos[Y][PRES], gamer_control)

		if BALL_H // 2 <= y[PRES] and y[PRES] + BALL_H // 2 < HEIGH_SC and abs( y[PRES] - y[PAST] ) <= 1 :
			#marge = 1
			if gamer_pos_Y[gamer_control][PRES] + GAMER_H // 2 - marge <= y[PRES] and y[PRES] < gamer_pos_Y[gamer_control][PRES] + GAMER_H // 2 + marge :#si la raquette est bien placée
				if gamer_move[gamer_control] != STOP :
					gamer_move[gamer_control] = STOP
					gamer_pos_Y[gamer_control][PAST] = gamer_pos_Y[gamer_control][PRES]
			else:
				if gamer_move[gamer_control] == STOP :
					if y[PRES] < gamer_pos_Y[gamer_control][PRES] :
						gamer_move[gamer_control] = MONT
						gamer_time[gamer_control][PAST] = tps[PRES]
					elif gamer_pos_Y[gamer_control][PRES] + GAMER_H <= y[PRES] + BALL_H :
						gamer_move[gamer_control] = DESC
						gamer_time[gamer_control][PAST] = tps[PRES]
		###
		for i in [ UN , DEUX ] :
			if gamer_move[i] != STOP :
				gamer_pos_Y[i][PRES] = gamer_pos_Y[i][PAST] - round( ( tps[PRES] - gamer_time[i][PAST] ) * GAMER_VIT * gamer_move[i] )

		if not( 0 <= ball_pos[Y][PRES] and ball_pos[Y][PRES] + BALL_H <= HEIGH_SC ) :
			if ball_pos[Y][PRES] < 0 :
				ball_pos[Y][PRES] += 1
			else :
				ball_pos[Y][PRES] -= 1
			ball_vit_vect[Y] = -ball_vit_vect[Y]
			#ball_angle = - ball_angle
			ball_time[PAST] = tps[PRES]
			ball_pos[X][PAST] = ball_pos[X][PRES]
			ball_pos[Y][PAST] = ball_pos[Y][PRES]

		for i in [ UN , DEUX ] :
			order = delimiterCollision(ball_pos[X][PRES], ball_pos[Y][PRES], BALL_W, BALL_H, GAMER_POS_X[i], gamer_pos_Y[i][PRES], GAMER_W, GAMER_H)
			if order == LEFT :
				ball_pos[X][PRES] -= 1
				ball_vit_vect[X] = -ball_vit_vect[X]
				ball_vit_vect = changeBallVit(ball_pos[Y][PRES], gamer_pos_Y[i][PRES], ball_vit_vect, ball_vit_norm)
				#ball_angle = pi - ball_angle
			elif order == RIGHT :
				ball_pos[X][PRES] += 1
				ball_vit_vect[X] = -ball_vit_vect[X]
				ball_vit_vect = changeBallVit(ball_pos[Y][PRES], gamer_pos_Y[i][PRES], ball_vit_vect, ball_vit_norm)
				#ball_angle = pi - ball_angle
			elif order == DOWN :
				ball_pos[Y][PRES] += 1
				ball_vit_vect[Y] = -ball_vit_vect[Y]
				#ball_angle = - ball_angle
			elif order == UP :
				ball_pos[Y][PRES] -= 1
				ball_vit_vect[Y] = -ball_vit_vect[Y]
				#ball_angle = - ball_angle
			if order != -1 :
				ball_time[PAST] = tps[PRES]
				ball_pos[X][PAST] = ball_pos[X][PRES]
				ball_pos[Y][PAST] = ball_pos[Y][PRES]

			if gamer_move[i] != STOP:
				if gamer_pos_Y[i][PRES] < 0 :
					gamer_pos_Y[i][PRES] += 1
					gamer_pos_Y[i][PAST] = gamer_pos_Y[i][PRES]
					gamer_move[i] = STOP
				elif HEIGH_SC < gamer_pos_Y[i][PRES] + GAMER_H :
					gamer_pos_Y[i][PRES] -= 1
					gamer_pos_Y[i][PAST] = gamer_pos_Y[i][PRES]
					gamer_move[i] = STOP

		if FREQ <= tps[PRES] - tps[PAST] :
			bg.fill(BLACK)
			bg.blit(gamer, (GAMER_POS_X[UN], gamer_pos_Y[UN][PRES]))
			bg.blit(gamer, (GAMER_POS_X[DEUX], gamer_pos_Y[DEUX][PRES]))
			printScore(font, score, cadre_score)
			bg.blit(cadre_score, textpos_cadre_score)
			bg.blit(ball, (ball_pos[X][PRES], ball_pos[Y][PRES]))
			bg.blit(croix, (GAMER_POS_X[gamer_control] + ( gamer_control + 1 ) % 2 * GAMER_W - BALL_W // 2, y[PRES] - BALL_H // 2))
			line(bg, GREEN, (0, a[0]), (WIDTH_SC, a[0] + a[1] * WIDTH_SC ), 1)
			screen.blit(bg, (0, 0))
			tps[PAST] = tps[PRES]
			pygame.display.flip()

#############################
#########constantes##########
#############################
WIDTH_SC, HEIGH_SC = getSystemResolutionOnLinux()
WIDTH_SC = int( WIDTH_SC * 0.9 )
HEIGH_SC = int( HEIGH_SC * 0.9 )

FREQ = 4

GAMER_W = 30 * WIDTH_SC // 1229
GAMER_H = 260 * HEIGH_SC // 1229

CADRE_SCORE_W = int( WIDTH_SC * 0.25 )
CADRE_SCORE_H = int( HEIGH_SC * 0.2 )

GAMER_POS_X = [ round( WIDTH_SC * 0.05 ) , round( WIDTH_SC * 0.95 ) - GAMER_W ]

GAMER_VIT = 600.0 / 1000 * WIDTH_SC / 1229#premier terme en px/s

BALL_W = 30 * WIDTH_SC // 1229
BALL_H = BALL_W
#BALL_VIT = 400.0 / 1000 * WIDTH_SC / 1229#vitesse en px/s

FONT_SIZE = int( CADRE_SCORE_W * 0.250 )

#ADD_ANGLE = 20.0

#Mouse Button, Scroll Wheel
MB_LEFT, MB_MIDDLE, MB_RIGHT, MBSW_UP, MBSW_DOWN = 1, 2, 3, 4, 5

#              R    G    B
WHITE      = (250, 250, 250)
BLACK      = ( 10,  10,  10)
GREEN      = (  0, 155,   0)
BRIGHTBLUE = (  0,  50, 255)
BROWN      = (174,  94,   0)
RED        = (155,   0,   0)

#############################
########enumerations#########
#############################
PRES, PAST, DELAY = 0, 1, 2
X, Y = 0, 1
VERT, HOR = 0, 1
NULL, UP, DOWN, RIGHT, LEFT = -1, 0, 1, 2, 3
NO, NE, SO, SE = 0, 1, 2, 3#points cardinaux
MONT, STOP, DESC = 1, 0, -1
UN, DEUX = 0, 1# joueur UN, joueur DEUX

#############################
########dictionnaires########
#############################
DIR = { NULL : "NULL" , UP : "UP" , DOWN : "DOWN" , RIGHT : "RIGHT" , LEFT : "LEFT" }

if __name__ == '__main__' : main()
