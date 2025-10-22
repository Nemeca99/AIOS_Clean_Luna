# Privacy Core - Data Protection & Compliance

**Purpose:** Privacy controls and data protection

## What It Does

- Data anonymization
- PII detection and redaction
- GDPR/CCPA compliance
- Data retention policies
- User data export

## Key Components

- `privacy_manager.py` - Main privacy orchestrator
- `anonymizer.py` - Data anonymization
- `pii_detector.py` - PII detection

## Usage

```python
from privacy_core.privacy_manager import PrivacyManager

privacy = PrivacyManager()
cleaned = privacy.anonymize(data)
```

## Configuration

See `config/privacy_config.json` for retention policies and compliance settings.

