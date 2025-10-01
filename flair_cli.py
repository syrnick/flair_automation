#!/usr/bin/env python3

import argparse
import sys
from datetime import datetime
from flair_controller import FlairController

def main():
    parser = argparse.ArgumentParser(
        description="Control Flair vents - activate/deactivate rooms based on time of day"
    )

    parser.add_argument(
        "command",
        choices=["activate", "deactivate", "status", "list", "schedule"],
        help="Command to execute"
    )

    parser.add_argument(
        "--room", "-r",
        type=str,
        help="Specific room name (optional, affects all rooms if not specified)"
    )

    parser.add_argument(
        "--config", "-c",
        type=str,
        default="flair_config.json",
        help="Path to configuration file (default: flair_config.json)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    controller = FlairController(args.config)

    if args.command == "list":
        rooms = controller.list_api_rooms()
        if rooms is None:
            print("Failed to retrieve rooms from API")
            return 1
        elif rooms:
            print("Rooms from Flair API:")
            for room in rooms:
                active_status = "active" if room['active'] else "inactive"
                print(f"  - {room['name']} (ID: {room['id']}, Status: {active_status})")
        else:
            print("No rooms found")
        return 0

    if args.command == "schedule":
        results = controller.apply_schedule()
        if not results:
            print("No schedule applied (no active segment or schedule not configured)")
            return 0

        success_count = sum(1 for r in results.values() if r['success'])
        total_count = len(results)

        if args.verbose:
            for room_name, result in results.items():
                if result['reason'] == 'already_correct':
                    print(f"✓ {room_name}: already {result['current']}")
                elif result['reason'] == 'updated':
                    print(f"✓ {room_name}: updated from {result['previous']} to {result['desired']}")
                elif result['reason'] == 'not_configured':
                    print(f"✗ {room_name}: not in room configuration")
                else:
                    print(f"✗ {room_name}: {result['reason']}")

        print(f"Schedule applied: {success_count}/{total_count} rooms processed successfully")
        return 0 if success_count == total_count else 1

    if args.command == "status":
        if args.room:
            state = controller.get_room_state(args.room)
            if state:
                active = state.get("active", "unknown")
                print(f"Room '{args.room}': {'active' if active else 'inactive'}")
            else:
                print(f"Failed to get status for room '{args.room}'")
                return 1
        else:
            rooms = controller.get_all_rooms()
            print("Room status:")
            for room in rooms:
                state = controller.get_room_state(room)
                if state:
                    active = state.get("active", "unknown")
                    status = "active" if active else "inactive"
                    print(f"  {room}: {status}")
                else:
                    print(f"  {room}: error getting status")
        return 0

    if args.command == "activate":
        if not args.room:
            print("Error: --room is required for activate command")
            return 1

        success = controller.activate_room(args.room)
        if success:
            print(f"Room '{args.room}' activated")
            return 0
        else:
            print(f"Failed to activate room '{args.room}'")
            return 1

    if args.command == "deactivate":
        if not args.room:
            print("Error: --room is required for deactivate command")
            return 1

        success = controller.deactivate_room(args.room)
        if success:
            print(f"Room '{args.room}' deactivated")
            return 0
        else:
            print(f"Failed to deactivate room '{args.room}'")
            return 1

if __name__ == "__main__":
    sys.exit(main())