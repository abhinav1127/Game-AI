package dk.itu.mario.engine.level;

import java.util.Random;
import java.util.*;

//Make any new member variables and functions you deem necessary.
//Make new constructors if necessary
//You must implement mutate() and crossover()


public class MyDNA extends DNA
{
	
	public int numGenes = 0; //number of genes

	// Return a new DNA that differs from this one in a small way.
	// Do not change this DNA by side effect; copy it, change the copy, and return the copy.
	public MyDNA mutate ()
	{
		MyDNA copy = new MyDNA();
		//YOUR CODE GOES BELOW HERE
		Random random = new Random();
		int positionToChange = random.nextInt(20);
		int changingTo = (int) this.getChromosome().charAt(positionToChange);
		while (changingTo == this.getChromosome().charAt(positionToChange)) {
			changingTo = random.nextInt(6);
		}
		String newChromosome = this.getChromosome().substring(0,positionToChange)+changingTo+this.getChromosome().substring(positionToChange + 1);
		copy.setChromosome(newChromosome);
		//YOUR CODE GOES ABOVE HERE
		return copy;
	}
	
	// Do not change this DNA by side effect
	public ArrayList<MyDNA> crossover (MyDNA mate)
	{
		ArrayList<MyDNA> offspring = new ArrayList<MyDNA>();
		//YOUR CODE GOES BELOW HERE
		String firstChild = this.getChromosome().substring(0,10) + mate.getChromosome().substring(10,20);
		String secondChild = mate.getChromosome().substring(0,10) + this.getChromosome().substring(10,20);

		MyDNA copy1 = new MyDNA();
		copy1.setChromosome(firstChild);

		MyDNA copy2 = new MyDNA();
		copy2.setChromosome(secondChild);

		offspring.add(copy1);
		offspring.add(copy2);

		//YOUR CODE GOES ABOVE HERE
		return offspring;
	}
	
	// Optional, modify this function if you use a means of calculating fitness other than using the fitness member variable.
	// Return 0 if this object has the same fitness as other.
	// Return -1 if this object has lower fitness than other.
	// Return +1 if this objet has greater fitness than other.
	public int compareTo(MyDNA other)
	{
		int result = super.compareTo(other);
		//YOUR CODE GOES BELOW HERE
		if (this.getFitness() > other.getFitness()) {
			result = 1;
		} else if (this.getFitness() < other.getFitness()) {
			result = -1;
		} else {
			result = 0;
		}
		
		//YOUR CODE GOES ABOVE HERE
		return result;
	}
	
	
	// For debugging purposes (optional)
	public String toString ()
	{
		String s = super.toString();
		//YOUR CODE GOES BELOW HERE
		
		//YOUR CODE GOES ABOVE HERE
		return s;
	}
	
	public void setNumGenes (int n)
	{
		this.numGenes = n;
	}

}

