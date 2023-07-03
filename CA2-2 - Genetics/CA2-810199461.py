import random

class Utils():
    def __init__(self):
        pass

    def parse_line(self, line, delimiter=' '):
        index = line.index(delimiter) if delimiter in line else None
        if index is None:
            return [line, None]
        result = line[0:index]
        remainingLine = line[index + 1:]
        return [result, remainingLine]
    
    def make_list_from_line(self, line):
        li = []
        while line:
            arg, line = self.parse_line(line)
            li.append(arg)
        
        return li
    
    def get_list_from_input(self, make_it_int=False):
        inp = input()
        return self.make_list_from_line(inp) if not make_it_int else \
            [int(x) for x in self.make_list_from_line(inp)]
    
utils = Utils()    
carry_percentage = 0.5
crossover_probability = 0.8
population_size = 200

class EquationBuilder:
    
    def __init__(self, operators, operands, equation_length, goal_number):
        self.operators = operators
        self.operands = operands
        self.equation_length = equation_length
        self.goal_number = goal_number
        self.population = self.make_first_population()
        
    def make_first_population(self):
        new_population = []
        for i in range(population_size):
            new_chromosome = ''
            for i in range(self.equation_length):
                new_chromosome += str(self.operands[random.randint(0, len(self.operands) - 1)]) if i%2 == 0 else \
                                  str(self.operators[random.randint(0, len(self.operators) - 1)])
            new_population.append(new_chromosome)
            
        return new_population
    
    def find_equation(self):
        while (True):
            random.shuffle(self.population)
            fitnesses = []
            for i in range(population_size):
                new_eq = self.population[i]
                new_fitt = self.calc_fitness(new_eq)
                fitnesses.append(new_fitt)
                if new_fitt == 0:
                    return new_eq 
            
            best_chromosomes = [x for _,x in sorted(zip(fitnesses, self.population))]
            carried_size = int(population_size*carry_percentage)
            carried_chromosomes = best_chromosomes[:carried_size]
            
            crossover_pool = self.create_crossover_pool()

            self.population.clear()
            
            for i in range(population_size - carried_size):
                self.population.append(self.mutate(crossover_pool[i]))

            self.population.extend(carried_chromosomes)
    
    def create_crossover_pool(self):
        crossover_pool = []
        candidates = []
        self.create_crossover_chromosomes(crossover_pool, candidates)
        self.crossover_candidates(candidates)
        crossover_pool.extend(candidates) 
        return crossover_pool
    
    def mutate(self, chromosome):
        chromosome = list(chromosome)
        num_of_mutate = random.randint(1, self.equation_length)
        for i in range(num_of_mutate):
            index = random.randint(1, self.equation_length) - 1
            chromosome[index] = str(random.choice(self.operands)) if chromosome[index].isnumeric() \
            else str(random.choice(self.operators))
        chromosome = "".join(chromosome)
        return chromosome

    def calc_fitness(self, chromosome):
        return abs(self.goal_number - eval(chromosome))
    
    def create_crossover_chromosomes(self, crossover_pool, candidates):
        for i in range(len(self.population)):     
            if random.random() > crossover_probability:
                crossover_pool.append(self.population[i])
            else:
                candidates.append(self.population[i])
        
    def crossover_candidates(self, candidates):
        for i in range(len(candidates)):
            divider = random.randint(0, self.equation_length)
            part1 = candidates[i][0:divider]
            part2 = candidates[i+1][divider:] if i != len(candidates) - 1 else candidates[0][divider:]
            candidates[i] = part1 + part2

equation_length = int(input())
operands = utils.get_list_from_input()
operators = utils.get_list_from_input()
goal_number = int(input())

equationBuilder = EquationBuilder(operators, operands, equation_length, goal_number)
    
equation = equationBuilder.find_equation()
print(equation)