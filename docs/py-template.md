*TBU*
```bash
class MyClass:
    """A brief description of what this class does."""

    def __init__(self, name: str, initial_value: int = 0) -> None:
        """
        Initializes an instance of MyClass.

        Args:
            name (str): The name for this instance.
            initial_value (int, optional): An initial value. Defaults to 0.
        """
        self.name = name
        self.value = initial_value
        print(f"Instance '{self.name}' created with value {self.value}.")

    def update_value(self, new_value: int) -> None:
        """
        Updates the instance's value.

        Args:
            new_value (int): The new value to set.
        """
        print(f"Updating value for '{self.name}' from {self.value} to {new_value}.")
        self.value = new_value


def main() -> None:
    # Create an instance of the class
    my_object = MyClass(name="Demo Object", initial_value=42)
        
    # Update the state of the instance
    my_object.update_value(100)

if __name__ == '__main__':      # Skips next line if file was imported.
    main()                      # Runs `def main(): ...` function.
```
