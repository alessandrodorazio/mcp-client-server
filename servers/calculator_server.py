from mcp.server.fastmcp import FastMCP
import math

# Create a FastMCP server instance
mcp = FastMCP("Calculator Service")

@mcp.tool()
async def basic_calc(operation: str, x: float, y: float) -> str:
    """Perform basic mathematical operations.
    
    Args:
        operation: The operation to perform (add, subtract, multiply, divide)
        x: First number
        y: Second number
    
    Returns:
        Result of the calculation
    """
    operation = operation.lower()
    
    if operation == "add":
        result = x + y
        return f"{x} + {y} = {result}"
    elif operation == "subtract":
        result = x - y
        return f"{x} - {y} = {result}"
    elif operation == "multiply":
        result = x * y
        return f"{x} × {y} = {result}"
    elif operation == "divide":
        if y == 0:
            return "Error: Division by zero"
        result = x / y
        return f"{x} ÷ {y} = {result}"
    else:
        return f"Unknown operation: {operation}. Please use add, subtract, multiply, or divide."

@mcp.tool()
async def scientific_calc(function: str, value: float) -> str:
    """Perform scientific mathematical calculations.
    
    Args:
        function: Mathematical function (sqrt, sin, cos, log, exp)
        value: The value to calculate
    
    Returns:
        Result of the calculation
    """
    function = function.lower()
    
    if function == "sqrt":
        if value < 0:
            return "Error: Cannot calculate square root of a negative number"
        result = math.sqrt(value)
        return f"√{value} = {result}"
    elif function == "sin":
        result = math.sin(value)
        return f"sin({value}) = {result}"
    elif function == "cos":
        result = math.cos(value)
        return f"cos({value}) = {result}"
    elif function == "log":
        if value <= 0:
            return "Error: Cannot calculate logarithm of a non-positive number"
        result = math.log10(value)
        return f"log10({value}) = {result}"
    elif function == "exp":
        result = math.exp(value)
        return f"e^{value} = {result}"
    else:
        return f"Unknown function: {function}. Please use sqrt, sin, cos, log, or exp."

@mcp.tool()
async def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """Convert between different units.
    
    Args:
        value: The value to convert
        from_unit: Source unit (km, m, cm, mi, ft, in)
        to_unit: Target unit (km, m, cm, mi, ft, in)
    
    Returns:
        Result of the conversion
    """
    # Conversion factors to meters
    to_meters = {
        "km": 1000,
        "m": 1,
        "cm": 0.01,
        "mi": 1609.34,
        "ft": 0.3048,
        "in": 0.0254
    }
    
    # Check if units are supported
    if from_unit not in to_meters:
        return f"Unsupported source unit: {from_unit}"
    if to_unit not in to_meters:
        return f"Unsupported target unit: {to_unit}"
    
    # Convert to meters first, then to target unit
    in_meters = value * to_meters[from_unit]
    result = in_meters / to_meters[to_unit]
    
    return f"{value} {from_unit} = {result} {to_unit}"

# Run the server when the script is executed directly
if __name__ == "__main__":
    mcp.run() 