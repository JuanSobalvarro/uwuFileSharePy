# Notes for the project

## Coroutines
Coroutines are a way to write asynchronous code in which we can pause or continue execution.
They are defined using the `async def` syntax and can be paused using the `await` keyword. 
Coroutines are used to perform non-blocking I/O operations, allowing other tasks to run while waiting for a response.

## Threads 
Threads are line of execution for a process. It is different from a process in that it shares the same memory space and 
resources. Threads are used to perform concurrent tasks, allowing multiple operations to run simultaneously. In Python, 
the `threading` module is used to create and manage threads. Threads can be created using the `Thread` class and can be 
started using the `start()` method. Threads can also be synchronized using locks, semaphores, and other synchronization 
primitives.

