# Exam for INF200 January Block 2023

## Model details
### Geography
	- fodder
	- param_geography
	Highland
	- param_geography = 300
	Lowland
	- param_geography = 800
	Water	
	- param_geography = -1
	Desert
	- param_geography = 0
	
### Fauna
	- age
	- weight
	- fitness
	- param_fauna
	Herbivores
	- param_fauna = 
		- w_birth      8
		- sigma_birth  1.5
		- beta         0.9
		- eta          0.05
		- a_half       40
		- phi_age      0.6
		- w_half       10
		- phi_weight   0.1
		- mu           0.25
		- gamma        0.2
		- zeta         3.5
		- xi           1.2
		- omega        0.4
		- F            10
		- DeltaPhiMax  N/A
	Carnivores
	- param_fauna = 
		- w_birth      6
		- sigma_birth  1
		- beta         0.75
		- eta          0.125
		- a_half       40
		- phi_age      0.3
		- w_half       4
		- phi_weight   0.4
		- mu           0.4
		- gamma        0.8
		- zeta         3.5
		- xi           1.1
		- omega        0.8
		- F            50
		- DeltaPhiMax  10

### Rossumøya
	- 2d array of cells
	
### Cell
	- loc = (row, col)
	- pop {dictionary of fauna}
	- geography
	- list of herbivores
	- list of carnivores
	
### Parameters
	param_fauna
		- w_birth
		- sigma_birth
		- beta
		- eta
		- a_half
		- phi_age
		- w_half
		- phi_weight
		- mu
		- gamma
		- zeta
		- xi
		- omega
		- F
		- DeltaPhiMax
	param_geography
		- f_max

## Simulation:
Simulate over the number of years, go through the annual_cycle:
_(go through each cell inside each steps of the annual cycle.)_

	- procreation()
	- feeding()
	- migration()
	- aging()
	- loss_of_weight()
	- death()
