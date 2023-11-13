using System;


public record Person(int Id, string FirstName, string LastName){
    //constructor
    public Person():this(0, "", "")
    {
    }
}

public class Program
{
	public static void Main()
	{
		new Person(0, "", "");
		new Person();
	}
}