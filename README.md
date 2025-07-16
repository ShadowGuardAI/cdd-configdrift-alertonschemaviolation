# cdd-configdrift-AlertOnSchemaViolation
Validates a configuration file against a pre-defined JSON schema. Alerts if the configuration violates the schema. Uses `jsonschema` library. - Focused on Detects unauthorized or unexpected changes in configuration files (e.g., YAML, JSON). Compares current configurations against baselines and alerts on deviations. Primarily designed for identifying configuration hardening issues.

## Install
`git clone https://github.com/ShadowGuardAI/cdd-configdrift-alertonschemaviolation`

## Usage
`./cdd-configdrift-alertonschemaviolation [params]`

## Parameters
- `-h`: Show help message and exit
- `-f`: No description provided
- `-l`: Set the logging level.

## License
Copyright (c) ShadowGuardAI
