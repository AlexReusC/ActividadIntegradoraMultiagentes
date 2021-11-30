from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid

from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid as PathGrid
from pathfinding.finder.a_star import AStarFinder

from random import randint

WIDTH = 14
HEIGHT = 14
DURATION = 500
NUMBER_BOXES = 15
NUMBER_ROBOTS = 5

class Wall(Agent):
	def __init__(self, model, pos):
		super().__init__(model.next_id(), model)
		self.pos = pos
		self.condition = 0
	def step(self):
		pass

class Box(Agent):
	def __init__(self, model, pos):
		super().__init__(model.next_id(), model)
		self.pos = pos
		self.condition = 0
	def step(self):
		pass

class Pallet(Agent):
	EMPTY = 0
	BOX_1 = 1
	BOX_2 = 2
	BOX_3 = 3
	BOX_4 = 4
	BOX_5 = 5
	
	def __init__(self, model, pos):
		super().__init__(model.next_id(), model)
		self.pos = pos
		self.condition = self.EMPTY
	def step(self):
		pass

class Robot(Agent):
	WITH_BOX = 0
	WITHOUT_BOX = 1
	def __init__(self, model, pos):
		super().__init__(model.next_id(), model)
		self.pos = pos
		self.condition = self.WITHOUT_BOX
	def step(self):
		if self.condition == self.WITHOUT_BOX:
			next_moves = self.model.grid.get_neighborhood(self.pos, moore=False)
			next_move = self.random.choice(next_moves)
			while(self.model.matrix[next_move[1]][next_move[0]] == 0):
				next_move = self.random.choice(next_moves)
			self.model.grid.move_agent(self, next_move)
			tmp = self.model.grid.get_cell_list_contents([next_move])[0]
			if isinstance(tmp, Box):
				self.model.grid.remove_agent(tmp)
				self.condition = self.WITH_BOX
				self.lookForPath()
		else:
			if len(self.path) != 0:
				self.model.grid.move_agent(self, self.path[0])
				self.path.pop(0)
				if len(self.path) == 0:
					self.placeBox()
			else:
				self.model.grid.move_agent(self, (self.pos[0], self.pos[1]-1))
				self.placeBox()
	
	def placeBox(self):
		tmp = self.model.grid.get_cell_list_contents([self.pos])[0]
		if tmp.condition != Pallet.BOX_5:
			tmp.condition +=  1
			self.condition = self.WITHOUT_BOX
			self.model.numberBoxes = self.model.numberBoxes - 1
			if self.model.numberBoxes == 0:
				self.model.allBoxesAddedTime = self.model.schedule.steps


	
	def lookForPath(self):
		pathGrid = PathGrid(matrix=self.model.matrix)
		start = pathGrid.node(self.pos[0], self.pos[1])
		end = pathGrid.node(12, 8)
		finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
		self.path, _ = finder.find_path(start, end, pathGrid)
		self.path.pop(0)

class Store(Model):
	def __init__(self):
		super().__init__()
		self.schedule = RandomActivation(self)
		self.grid = MultiGrid(WIDTH, HEIGHT, torus=False)
		self.duration = DURATION
		self.numberBoxes = NUMBER_BOXES
		self.allBoxesAddedTime = None

		self.matrix = [
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
			[0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
			[0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
			[0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
			[0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
			[0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0],
			[0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0],
			[0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 0],
			[0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 2, 0],
			[0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
			[0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
			[0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
			[0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
		]

		for _,x,y in self.grid.coord_iter():
			if self.matrix[y][x] == 0:
				wall = Wall(self, (x,y))
				self.grid.place_agent(wall, wall.pos)
				self.schedule.add(wall)
			elif self.matrix[y][x] == 2:
				pallet = Pallet(self, (x,y))
				self.grid.place_agent(pallet, pallet.pos)
				self.schedule.add(pallet)



		for _ in range(NUMBER_ROBOTS):
			x, y = randint(0, WIDTH-1), randint(0, HEIGHT-1)
			while self.matrix[y][x] == 0:
				x, y = randint(0, WIDTH-1), randint(0, HEIGHT-1)
			robot = Robot(self, (x,y))
			self.grid.place_agent(robot, robot.pos)
			self.schedule.add(robot)

		for _ in range(self.numberBoxes):
			x, y = randint(0, WIDTH-1), randint(0, HEIGHT-1)
			while self.grid.is_cell_empty((x,y)) == False:
				x, y = randint(0, WIDTH-1), randint(0, HEIGHT-1)
			box = Box(self, (x,y))
			self.grid.place_agent(box, box.pos)
			self.schedule.add(box)

	
	def step(self):
		if self.duration > 0:
			self.schedule.step()
			self.duration = self.duration - 1
		else:
			print("Numbero de movimientos necesarios: ", self.allBoxesAddedTime)
			print("Numero de movimientos realizados: ", self.schedule.steps * NUMBER_ROBOTS)
			print("Una estrategia para que lo resuelvan mas rapido se basa en")
			print("la observacion de que se quedan mucho tiempo en la parte derecha")
			print("ya que regresan al pallet, algo que se podria hacer es que")
			print("es que tengan una sala indicada a la que deberian de vovler")
			self.running = False

def agent_portrayal(agent):
	if isinstance(agent, Wall):
		return {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Color": "Gray", "Layer": 0}
	elif isinstance(agent, Robot):
		if agent.condition == Robot.WITHOUT_BOX:
			return {"Shape": "space-robot.png",  "Layer": 1}
		elif agent.condition == Robot.WITH_BOX:
			return {"Shape": "space-robot-box.png",  "Layer": 1}
	elif isinstance(agent, Box):
		return {"Shape": "caja-del-paquete.png",  "Layer": 1}
	elif isinstance(agent, Pallet):
		if agent.condition == Pallet.EMPTY:
			return {"Shape": "pallet.png",  "Layer": 0}
		elif agent.condition == Pallet.BOX_1:
			return {"Shape": "pallet1.png",  "Layer": 0}
		elif agent.condition == Pallet.BOX_2:
			return {"Shape": "pallet2.png",  "Layer": 0}
		elif agent.condition == Pallet.BOX_3:
			return {"Shape": "pallet3.png",  "Layer": 0}
		elif agent.condition == Pallet.BOX_4:
			return {"Shape": "pallet4.png",  "Layer": 0}
		elif agent.condition == Pallet.BOX_5:
			return {"Shape": "pallet5.png",  "Layer": 0}

grid = CanvasGrid(agent_portrayal, WIDTH, HEIGHT, 450, 450)

if __name__ == "__main__":
	server = ModularServer(Store, [grid], "Store", {})
	server.port = server.port = 8521
	server.launch()