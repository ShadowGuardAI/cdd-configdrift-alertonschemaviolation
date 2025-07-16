import argparse
import json
import logging
import sys

try:
    import jsonschema
    from jsonschema import validate
except ImportError:
    print("Please install the required dependencies: pip install jsonschema")
    sys.exit(1)

try:
    import yaml
except ImportError:
    print("Please install the required dependencies: pip install PyYAML")
    sys.exit(1)


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def setup_argparse():
    """
    Sets up the argument parser for the CLI.

    Returns:
        argparse.ArgumentParser: The configured argument parser.
    """
    parser = argparse.ArgumentParser(description='Validates a configuration file against a JSON schema and alerts on violations.')
    parser.add_argument('config_file', help='Path to the configuration file (JSON or YAML).')
    parser.add_argument('schema_file', help='Path to the JSON schema file.')
    parser.add_argument('-f', '--format', choices=['json', 'yaml'], default=None,
                        help='Specify the format of the config file (json or yaml). Autodetects if omitted.')
    parser.add_argument('-l', '--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO',
                        help='Set the logging level.')
    return parser


def load_config(config_file, format=None):
    """
    Loads the configuration file (JSON or YAML).

    Args:
        config_file (str): Path to the configuration file.
        format (str, optional):  Format of the config file ('json' or 'yaml'). Autodetects if None. Defaults to None.

    Returns:
        dict: The configuration data as a dictionary.

    Raises:
        FileNotFoundError: If the configuration file is not found.
        ValueError: If the file format is invalid or if the config file is empty.
        Exception: If there is an error during file reading.
    """
    try:
        with open(config_file, 'r') as f:
            if format == 'json' or (format is None and config_file.endswith('.json')):
                try:
                    config_data = json.load(f)
                except json.JSONDecodeError as e:
                     raise ValueError(f"Invalid JSON format in {config_file}: {e}")
            elif format == 'yaml' or (format is None and (config_file.endswith('.yaml') or config_file.endswith('.yml'))):
                try:
                    config_data = yaml.safe_load(f)
                except yaml.YAMLError as e:
                     raise ValueError(f"Invalid YAML format in {config_file}: {e}")
            else:
                # Attempt auto-detection based on content
                content = f.read()
                if not content.strip():  # Check for empty file
                    raise ValueError(f"Configuration file {config_file} is empty.")

                try:
                    # Try JSON first
                    config_data = json.loads(content)
                except json.JSONDecodeError:
                    try:
                        # Then try YAML
                        config_data = yaml.safe_load(content)
                    except yaml.YAMLError:
                        raise ValueError(f"Could not determine format of {config_file}.  Please specify format using -f/--format.")
                
        if not config_data:
            raise ValueError(f"Configuration file {config_file} is empty or contains no data.")

        return config_data
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    except ValueError as e:
        raise e
    except Exception as e:
        raise Exception(f"Error reading configuration file: {e}")



def load_schema(schema_file):
    """
    Loads the JSON schema from a file.

    Args:
        schema_file (str): Path to the JSON schema file.

    Returns:
        dict: The JSON schema as a dictionary.

    Raises:
        FileNotFoundError: If the schema file is not found.
        ValueError: If the schema file is invalid JSON.
    """
    try:
        with open(schema_file, 'r') as f:
            try:
                schema_data = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON format in schema file {schema_file}: {e}")
        return schema_data
    except FileNotFoundError:
        raise FileNotFoundError(f"Schema file not found: {schema_file}")
    except Exception as e:
        raise Exception(f"Error reading schema file: {e}")


def validate_config(config_data, schema_data):
    """
    Validates the configuration data against the JSON schema.

    Args:
        config_data (dict): The configuration data.
        schema_data (dict): The JSON schema.

    Returns:
        bool: True if the configuration is valid, False otherwise.

    Raises:
        jsonschema.exceptions.ValidationError: If the configuration violates the schema.
        jsonschema.exceptions.SchemaError: If the schema itself is invalid.
    """
    try:
        validate(instance=config_data, schema=schema_data)
        return True
    except jsonschema.exceptions.ValidationError as e:
        raise jsonschema.exceptions.ValidationError(f"Configuration validation error: {e}")
    except jsonschema.exceptions.SchemaError as e:
        raise jsonschema.exceptions.SchemaError(f"Invalid schema: {e}")
    except Exception as e:
        raise Exception(f"An unexpected error occurred during validation: {e}")



def main():
    """
    Main function to parse arguments, load config and schema, and validate.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    # Set logging level
    logging.getLogger().setLevel(args.log_level)

    try:
        # Load configuration data
        config_data = load_config(args.config_file, args.format)

        # Load schema data
        schema_data = load_schema(args.schema_file)

        # Validate configuration against the schema
        if validate_config(config_data, schema_data):
            logging.info("Configuration is valid.")
            print("Configuration is valid.")
        else:
            # This should never happen, as validate_config raises an exception on failure.
            logging.error("Configuration is invalid, but no exception was raised. This is unexpected.")
            print("Configuration is invalid, but no exception was raised. This is unexpected.")

    except FileNotFoundError as e:
        logging.error(e)
        print(f"Error: {e}")
        sys.exit(1)
    except ValueError as e:
        logging.error(e)
        print(f"Error: {e}")
        sys.exit(1)
    except jsonschema.exceptions.ValidationError as e:
        logging.error(e)
        print(f"Error: {e}")
        sys.exit(1)
    except jsonschema.exceptions.SchemaError as e:
        logging.error(e)
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()