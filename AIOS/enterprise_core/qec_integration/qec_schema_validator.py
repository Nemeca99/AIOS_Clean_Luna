"""
QEC Schema Validator
Strict validation for all QEC data schemas with lenient mode for exploration
"""

import json
import jsonschema
from typing import Dict, Any, List, Tuple, Optional
import sys
import os
from pathlib import Path
import argparse
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class QECSchemaValidator:
    """
    Validate QEC data against published schemas
    """
    
    def __init__(self, schemas_dir: str = "schemas"):
        self.schemas_dir = Path(schemas_dir)
        self.schemas = {}
        self.load_schemas()
        
    def load_schemas(self):
        """Load all published schemas"""
        schema_files = {
            'rollout_v1': 'rollout_v1.json',
            'features_v1': 'features_v1.json', 
            'result_v1': 'result_v1.json'
        }
        
        for schema_name, filename in schema_files.items():
            schema_path = self.schemas_dir / filename
            if schema_path.exists():
                with open(schema_path, 'r') as f:
                    self.schemas[schema_name] = json.load(f)
                logger.info(f"Loaded schema: {schema_name}")
            else:
                logger.warning(f"Schema file not found: {schema_path}")
    
    def validate_rollout_data(self, data: Dict[str, Any], lenient: bool = False) -> Tuple[bool, List[str]]:
        """Validate rollout data against schema"""
        if 'rollout_v1' not in self.schemas:
            return False, ["Rollout schema not loaded"]
        
        return self._validate_against_schema(data, self.schemas['rollout_v1'], lenient)
    
    def validate_features_data(self, data: Dict[str, Any], lenient: bool = False) -> Tuple[bool, List[str]]:
        """Validate features data against schema"""
        if 'features_v1' not in self.schemas:
            return False, ["Features schema not loaded"]
        
        return self._validate_against_schema(data, self.schemas['features_v1'], lenient)
    
    def validate_result_data(self, data: Dict[str, Any], lenient: bool = False) -> Tuple[bool, List[str]]:
        """Validate result data against schema"""
        if 'result_v1' not in self.schemas:
            return False, ["Result schema not loaded"]
        
        return self._validate_against_schema(data, self.schemas['result_v1'], lenient)
    
    def _validate_against_schema(self, data: Dict[str, Any], schema: Dict[str, Any], 
                               lenient: bool = False) -> Tuple[bool, List[str]]:
        """Validate data against schema"""
        errors = []
        
        try:
            if lenient:
                # In lenient mode, only check required fields and basic types
                errors = self._lenient_validation(data, schema)
            else:
                # Strict validation
                jsonschema.validate(data, schema)
                return True, []
                
        except jsonschema.ValidationError as e:
            errors.append(f"Validation error: {e.message}")
        except Exception as e:
            errors.append(f"Unexpected error: {str(e)}")
        
        return len(errors) == 0, errors
    
    def _lenient_validation(self, data: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
        """Perform lenient validation (required fields only)"""
        errors = []
        
        # Check required fields
        required_fields = schema.get('required', [])
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Check basic types for required fields
        properties = schema.get('properties', {})
        for field in required_fields:
            if field in data and field in properties:
                expected_type = properties[field].get('type')
                if expected_type and not self._check_basic_type(data[field], expected_type):
                    errors.append(f"Field '{field}' has wrong type. Expected {expected_type}, got {type(data[field]).__name__}")
        
        return errors
    
    def _check_basic_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected basic type"""
        type_mapping = {
            'string': str,
            'integer': int,
            'number': (int, float),
            'boolean': bool,
            'array': list,
            'object': dict
        }
        
        if expected_type in type_mapping:
            return isinstance(value, type_mapping[expected_type])
        
        return True  # Unknown type, assume valid
    
    def validate_file(self, file_path: str, schema_type: str, lenient: bool = False) -> Tuple[bool, List[str]]:
        """Validate a JSON file against schema"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            return False, [f"JSON decode error: {e}"]
        except Exception as e:
            return False, [f"File read error: {e}"]
        
        if schema_type == 'rollout':
            return self.validate_rollout_data(data, lenient)
        elif schema_type == 'features':
            return self.validate_features_data(data, lenient)
        elif schema_type == 'result':
            return self.validate_result_data(data, lenient)
        else:
            return False, [f"Unknown schema type: {schema_type}"]
    
    def validate_directory(self, dir_path: str, schema_type: str, lenient: bool = False) -> Dict[str, Tuple[bool, List[str]]]:
        """Validate all JSON files in a directory"""
        results = {}
        dir_path = Path(dir_path)
        
        if not dir_path.exists():
            return {"error": (False, ["Directory does not exist"])}
        
        json_files = list(dir_path.glob("**/*.json"))
        
        for json_file in json_files:
            is_valid, errors = self.validate_file(str(json_file), schema_type, lenient)
            results[str(json_file)] = (is_valid, errors)
        
        return results
    
    def generate_validation_report(self, validation_results: Dict[str, Tuple[bool, List[str]]]) -> Dict[str, Any]:
        """Generate validation report"""
        total_files = len(validation_results)
        valid_files = sum(1 for is_valid, _ in validation_results.values() if is_valid)
        invalid_files = total_files - valid_files
        
        # Collect all errors
        all_errors = []
        for file_path, (is_valid, errors) in validation_results.items():
            if not is_valid:
                all_errors.extend([f"{file_path}: {error}" for error in errors])
        
        # Error frequency analysis
        error_frequency = {}
        for error in all_errors:
            error_type = error.split(': ')[-1] if ': ' in error else error
            error_frequency[error_type] = error_frequency.get(error_type, 0) + 1
        
        report = {
            'summary': {
                'total_files': total_files,
                'valid_files': valid_files,
                'invalid_files': invalid_files,
                'validation_rate': valid_files / total_files if total_files > 0 else 0
            },
            'error_analysis': {
                'total_errors': len(all_errors),
                'unique_errors': len(set(all_errors)),
                'error_frequency': error_frequency
            },
            'detailed_results': validation_results,
            'timestamp': datetime.now().isoformat()
        }
        
        return report

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='QEC Schema Validator')
    parser.add_argument('--file', help='JSON file to validate')
    parser.add_argument('--directory', help='Directory to validate')
    parser.add_argument('--schema-type', required=True, choices=['rollout', 'features', 'result'],
                       help='Schema type to validate against')
    parser.add_argument('--lenient', action='store_true', help='Use lenient validation mode')
    parser.add_argument('--output', help='Output file for validation report')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize validator
    validator = QECSchemaValidator()
    
    # Validate file or directory
    if args.file:
        is_valid, errors = validator.validate_file(args.file, args.schema_type, args.lenient)
        if is_valid:
            print(f"✓ {args.file} is valid")
        else:
            print(f"✗ {args.file} has errors:")
            for error in errors:
                print(f"  - {error}")
    
    elif args.directory:
        results = validator.validate_directory(args.directory, args.schema_type, args.lenient)
        report = validator.generate_validation_report(results)
        
        # Print summary
        summary = report['summary']
        print(f"Validation Summary:")
        print(f"  Total files: {summary['total_files']}")
        print(f"  Valid files: {summary['valid_files']}")
        print(f"  Invalid files: {summary['invalid_files']}")
        print(f"  Validation rate: {summary['validation_rate']:.2%}")
        
        # Print error analysis
        error_analysis = report['error_analysis']
        if error_analysis['total_errors'] > 0:
            print(f"\nError Analysis:")
            print(f"  Total errors: {error_analysis['total_errors']}")
            print(f"  Unique errors: {error_analysis['unique_errors']}")
            print(f"  Most common errors:")
            for error, count in sorted(error_analysis['error_frequency'].items(), 
                                     key=lambda x: x[1], reverse=True)[:5]:
                print(f"    - {error}: {count} times")
        
        # Save report if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\nValidation report saved to: {args.output}")
    
    else:
        print("Please specify either --file or --directory")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
