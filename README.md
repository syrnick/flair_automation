# WARNING !!!

AI - generated code.
All with Claude Code.

My main focus was the schedule command. Everything else may not work.

# Flair Vent Controller

A command line tool to control Flair vents, automatically changing room states between active and inactive based on time of day.

## Features

- **Schedule-based automation**: Define custom time-based schedules to automatically control room states
- **Manual control**: Activate or deactivate specific rooms on demand
- **Status monitoring**: Check current state of rooms
- **API room listing**: Query Flair API to list all available rooms
- **Separated architecture**: Core logic separated from CLI interface
- **Configuration-driven**: JSON-based room, schedule, and API configuration

## Installation

1. Clone or download the files
2. Create a virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Update `flair_config.json` with your actual Flair API credentials and room IDs

## Configuration

Edit `flair_config.json`:

```json
{
  "api_base_url": "https://api.flair.co/",
  "client_id": "YOUR_CLIENT_ID_HERE",
  "client_secret": "YOUR_CLIENT_SECRET_HERE",
  "rooms": {
    "alex_office": {
      "id": "181924",
      "name": "Alex Office"
    },
    "master_bedroom": {
      "id": "182493",
      "name": "Master Bedroom"
    }
  },
  "schedule": [
    {
      "segmentName": "night",
      "from": "22:00",
      "to": "07:00",
      "roomState": {
        "alex_office": "inactive",
        "master_bedroom": "inactive"
      }
    },
    {
      "segmentName": "day",
      "from": "07:00",
      "to": "22:00",
      "roomState": {
        "alex_office": "active",
        "master_bedroom": "active"
      }
    }
  ]
}
```

## Usage Examples

### Basic Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Apply schedule (automatically activates/deactivates rooms based on current time)
python flair_cli.py schedule

# Apply schedule with verbose output
python flair_cli.py schedule --verbose

# Manual control specific room
python flair_cli.py activate --room alex_office
python flair_cli.py deactivate --room master_bedroom

# Check status of all rooms
python flair_cli.py status

# Check status of specific room
python flair_cli.py status --room alex_office

# List all rooms from Flair API
python flair_cli.py list
```

### Automation Examples

```bash
# Add to crontab to apply schedule every 15 minutes
*/15 * * * * /path/to/venv/bin/python /path/to/flair_cli.py schedule

# Or run hourly
0 * * * * /path/to/venv/bin/python /path/to/flair_cli.py schedule
```

## Command Reference

| Command | Description | Options |
|---------|-------------|---------|
| `schedule` | Apply configured schedule based on current time | `--verbose` |
| `activate` | Manually activate a room | `--room` (required) |
| `deactivate` | Manually deactivate a room | `--room` (required) |
| `status` | Check room state(s) | `--room` (optional) |
| `list` | List all rooms from Flair API | None |

## Global Options

- `--config, -c`: Path to configuration file (default: flair_config.json)
- `--room, -r`: Specific room name (for activate/deactivate/status commands)
- `--verbose, -v`: Enable verbose output showing detailed results
- `--help, -h`: Show help message

## Files

- `flair_cli.py` - Command line interface
- `flair_controller.py` - Core logic and API handling
- `flair_config.json` - Configuration file with API credentials, room definitions, and schedules
- `requirements.txt` - Python dependencies
- `LICENSE` - MIT License

## Schedule Configuration

Schedules support multiple time segments with different room states:

- **Time format**: Use 24-hour format (HH:MM)
- **Overnight periods**: Schedules automatically handle overnight periods (e.g., 22:00 to 07:00)
- **Room states**: Set each room to `"active"` or `"inactive"`
- **Multiple segments**: Define as many schedule segments as needed

The `schedule` command will:
1. Find the current active time segment
2. Check the current state of each room via API
3. Only update rooms where the state differs from the configured state