# Command Library

Reusable command definitions for robot mechanisms.

## How It Works

1. Each JSON file defines commands for a category (intake, conveyor, etc.)
2. Season configs reference which categories they need
3. Seasons can override command names/code for their specific mechanisms

## Adding a New Category

1. Copy `_template.json` to `your_category.json`
2. Edit the commands for your mechanism
3. Reference it in your season's `config.json`

## File Format
```json
{
    "category": "Category Name",
    "description": "What this category is for",
    "commands": [
        {
            "id": "unique_id",
            "name": "Display Name",
            "code_template": "mech.methodName();",
            "color": "#00FF00",
            "description": "What this does"
        }
    ]
}
```