public class Employee{
    public String name;
    public int age;
    void getrole(){
        System.out.println("Employee.");
    }
    int calculateSalary(){
        return 30000;
    }
}
public class Manager extends Employee{
    void getrole(){
        System.out.println("Manager.");
    }
    int calculateSalary(){
        return 50000;
    }
}
public class Developer extends Employee{
    void getrole(){
        System.out.println("Developer.");
    }
    int calculateSalary(){
        return 40000;
    }
}
