# Lu

**Lu** is an evolving pseudocode compiler designed to translate pseudocode into Python code. It aims to facilitate the conversion of algorithmic logic from pseudocode to executable Python code, making the implementation process more efficient and straightforward.

## Features

- **Tokenization**: Converts Lu code into tokens for easier processing.
- **Print Statement Conversion**: Translates Lu print statements into Python's `print()` function.
- **Comment Handling**: Identifies and preserves comments in Lu code.
- **Variable Management**:
  - **Declaration**: Supports explicit variable declaration with type specification.
  - **Assignment**: Allows assigning values to declared variables.
  - **Deletion**: Provides functionality to delete variables.
- **Type Checking**: Implements basic type checking for variable assignments.
- **Error Handling**: 
  - Provides specific error types for different scenarios (syntax errors, type errors, etc.).
  - Includes detailed error messages with line and column information.
- **Logging System**: 
  - Implements a robust logging system with different log levels.
  - Provides colored console output for better readability.
  - Includes file and line information in log messages for easy debugging.

  
## Installation

To set up Lu on your local machine, follow these steps:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/gsdev215/lu.git
    ```


# Lu Language Compiler TODO List

## Completed Tasks

- [x] Implement basic tokenization
- [x] Handle `print` statements in pseudocode
- [x] Add support for comment handling
- [x] Implement variable declaration and assignment
- [x] Add basic type checking for variables
- [x] Implement variable deletion
- [x] Create a basic error handling system
- [x] Develop a logging system with colored output
- [x] Add file and line information to error messages

## In Progress

- [ ] Improve error handling and reporting
  - [ ] Add more specific error types for different scenarios
  - [ ] Enhance error messages with code snippets
- [ ] Implement Function definitions and calls

## To Do

- [ ] Add support for additional pseudocode constructs
  - [ ] Implement if/else conditionals and support for loops (while, for)
  - [ ] Add support for nested scopes and closures

- [ ] Enhance type system
  - [ ] Add support for custom data types and classes
  - [ ] Implement type inference

- [ ] Improve compiler architecture
  - [ ] Implement an Abstract Syntax Tree (AST) for more robust parsing
  - [ ] Develop a symbol table for better variable and function scope management

- [ ] Enhance language features
  - [ ] Add support for importing other Lu files
  - [ ] Implement a standard library of built-in functions
  - [ ] Add support for multi-line strings and string interpolation
  - [ ] Implement async/await functionality
  - [ ] Add support for decorators

- [ ] Enhance documentation and provide usage examples
  - [ ] Write comprehensive language specification
  - [ ] Create tutorials and guides for Lu programming

- [ ] Performance optimization

## Contributing

We welcome contributions to Lu! To contribute:

1. **Fork the repository** on GitHub.
2. **Create a new branch** for your changes:
    ```bash
    git checkout -b feature/your-feature-name
    ```
3. **Make your changes** and commit them with descriptive messages:
    ```bash
    git commit -am 'Add new feature'
    ```
4. **Push your changes** to your forked repository:
    ```bash
    git push origin feature/your-feature-name
    ```
5. **Open a pull request** to merge your changes into the main repository.

Please adhere to our coding standards and include tests with your contributions.

## License

This project is licensed under the [Apache License 2.0](LICENSE). See the LICENSE file for more details.

## Contact

For questions or suggestions, please open an issue on GitHub or contact us at [gsdev.devloper@gmail.com].

