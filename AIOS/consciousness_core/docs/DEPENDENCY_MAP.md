# Lyra Blackwall Module Dependency Map

This file shows the dependencies between different modules in the Lyra Blackwall codebase.

## Core Modules

### .Extra_Optional.Future.Future.Extra.Open Extraction Blackwall Phase Two.echo_drive_core

#### Imports:
- `from memory_loader import load_memory_shards`
- `from vector_embedder import embed_text, search_faiss_index`
- `import faiss`

#### Imported by:

### .Extra_Optional.Future.Future.Phase 2.echo_drive_core

#### Imports:
- `from memory_loader import load_memory_shards`
- `from vector_embedder import embed_text, search_faiss_index`
- `import faiss`

#### Imported by:

### .Extra_Optional.Future.Future.Phase 4.echo_core_loop

#### Imports:
- `import datetime`
- `import subprocess`
- `import time`

#### Imported by:

### .Extra_Optional.Python.Python.lyra_code_core

#### Imports:
- `import datetime`

#### Imported by:

### boot.blackwall_core

#### Imports:
- `from collections import defaultdict`

#### Imported by:

### boot.discord_relay_core

#### Imports:
- `import asyncio`
- `import discord`

#### Imported by:

### core.__init__

#### Imports:
- `from .blackwall_pipeline import (`

#### Imported by:

### core.backup.blackwall_pipeline

#### Imports:

#### Imported by:

### core.blackwall_pipeline

#### Imports:
- `from .init_services import initialize_services`
- `from .init_services import initialize_services`
- `from collections import defaultdict, Counter`
- `from datetime import datetime`
- `from lexicon.init_services import initialize_services`
- `from lexicon.init_services import initialize_services`
- `from spacy.language import Language`
- `from typing import Any, Dict, List, Optional, Tuple, Set`
- `import copy`
- `import gc`
- `import gc`
- `import psutil`
- `import random`
- `import signal`
- `import spacy`
- `import time`
- `import traceback`

#### Imported by:

### core.blackwall_pipeline_integration

#### Imports:
- `from typing import Dict, Any, Optional, List, Tuple`

#### Imported by:

### core.cleanup_blackwall_files

#### Imports:
- `from datetime import datetime`

#### Imported by:

### core.compute_fragment_weights

#### Imports:

#### Imported by:

### core.convert_logs_to_new_format

#### Imports:
- `from typing import Dict, Any, List, Optional, Tuple`
- `import argparse`
- `import datetime`

#### Imported by:

### core.drift

#### Imports:
- `import random`

#### Imported by:

### core.error_handler

#### Imports:
- `from datetime import datetime`
- `from typing import Dict, Any, Optional, List, Callable`
- `import time`
- `import traceback`

#### Imported by:

### core.feedback_tools

#### Imports:

#### Imported by:

### core.google_drive_link

#### Imports:
- `from google_auth_oauthlib.flow import InstalledAppFlow`
- `from google_auth_oauthlib.flow import InstalledAppFlow`
- `from googleapiclient.discovery import build`
- `from googleapiclient.discovery import build`
- `from googleapiclient.errors import HttpError`
- `from googleapiclient.errors import HttpError`
- `from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload`
- `from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload`
- `import datetime`
- `import io`
- `import subprocess`

#### Imported by:

### core.google_drive_link_fixed

#### Imports:
- `from google_auth_oauthlib.flow import InstalledAppFlow`
- `from googleapiclient.discovery import build`
- `from googleapiclient.errors import HttpError`
- `from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload`
- `import datetime`
- `import io`

#### Imported by:

### core.google_drive_link_fixed2

#### Imports:
- `from google_auth_oauthlib.flow import InstalledAppFlow`
- `from google_auth_oauthlib.flow import InstalledAppFlow`
- `from googleapiclient.discovery import build`
- `from googleapiclient.discovery import build`
- `from googleapiclient.errors import HttpError`
- `from googleapiclient.errors import HttpError`
- `from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload`
- `from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload`
- `import datetime`
- `import io`
- `import subprocess`

#### Imported by:

### core.init_services

#### Imports:
- `from .llm_service import default_llm_service as dls`
- `from typing import Dict, Tuple, Optional, Any`

#### Imported by:

### core.left_hemisphere.generate_left_lexicon_from_thesaurus

#### Imports:
- `from collections import defaultdict`

#### Imported by:

### core.left_hemisphere.generate_lexicon_json

#### Imports:

#### Imported by:

### core.lexicon_service

#### Imports:
- `from collections import defaultdict`
- `from collections import defaultdict`
- `from collections import defaultdict`
- `from typing import Dict, Any, Optional, List, Set, Tuple`
- `import time`
- `import traceback`
- `import traceback`

#### Imported by:

### core.llm_service

#### Imports:
- `from typing import Dict, Any, Optional, List, Union, Tuple`
- `import random`
- `import time`

#### Imported by:

### core.llm_summarizer

#### Imports:

#### Imported by:

### core.lyra_bot

#### Imports:
- `from blackwall_pipeline import BlackwallPipeline, clean_text`
- `from google_drive_link import download_from_drive, upload_to_drive`
- `from googleapiclient.discovery import build`
- `from googleapiclient.errors import HttpError`
- `from lyra_memory import load_memory_from_file, append_memory, truncate_memory_if_needed, safe_upload_memory_snapshot, search_ltm_logs, consolidate_stm_to_ltm`
- `import discord`
- `import subprocess`
- `import time`
- `import traceback`

#### Imported by:

### core.lyra_bot_fixed

#### Imports:
- `from blackwall_pipeline import BlackwallPipeline`
- `from google_drive_link import download_from_drive, upload_to_drive`
- `from googleapiclient.discovery import build`
- `from googleapiclient.errors import HttpError`
- `from lyra_memory import load_memory_from_file, append_memory, truncate_memory_if_needed`
- `import discord`
- `import time`
- `import traceback`

#### Imported by:

### core.lyra_core_loader

#### Imports:
- `import patch_litellm`
- `import time`

#### Imported by:

### core.lyra_memory

#### Imports:
- `import datetime`
- `import patch_litellm`

#### Imported by:

### core.lyra_vector_memory

#### Imports:
- `from sentence_transformers import SentenceTransformer`
- `from typing import List, Dict, Any, Optional`
- `import numpy as np`

#### Imported by:

### core.patch_litellm

#### Imports:
- `import litellm`

#### Imported by:

### core.run_blackwall

#### Imports:
- `from blackwall_pipeline import (`
- `from error_handler import error_handler`
- `from init_services import initialize_services`
- `from typing import Dict, List, Any, Optional, Tuple`
- `import argparse`
- `import datetime`
- `import datetime`
- `import psutil`
- `import random`
- `import time`
- `import traceback`
- `import traceback`

#### Imported by:

### core.semantic_memory

#### Imports:
- `from sentence_transformers import SentenceTransformer, util`
- `import numpy as np`

#### Imported by:

### core.test_bot_integration

#### Imports:
- `from blackwall_pipeline import BlackwallPipeline`
- `from datetime import datetime`
- `from google_drive_link import get_drive_service`
- `import traceback`

#### Imported by:

### core.test_dynamic_fusion

#### Imports:
- `from typing import Dict, Any`
- `import inspect`
- `import traceback`

#### Imported by:

### core.test_lexicon_service

#### Imports:
- `from pprint import pprint`

#### Imported by:

### core.test_log_access

#### Imports:

#### Imported by:

### core.test_new_log_format

#### Imports:
- `from typing import Dict, Any`
- `import datetime`

#### Imported by:

### core.validate_lexicon_organization

#### Imports:

#### Imported by:

### core.validate_pipeline

#### Imports:
- `from blackwall_pipeline import BlackwallPipeline`
- `import traceback`

#### Imported by:

### core.weight_delta_logger

#### Imports:
- `from datetime import datetime`

#### Imported by:

## Dashboard Modules

### Copilot.web_dashboard

#### Imports:
- `import argparse`
- `import datetime`

#### Imported by:

### archive.Copilot.web_dashboard

#### Imports:
- `import argparse`
- `import datetime`

#### Imported by:

### archive.integrated_dashboard

#### Imports:
- `import argparse`
- `import datetime`
- `import subprocess`
- `import time`

#### Imported by:

### dashboard.__init__

#### Imports:

#### Imported by:

### dashboard.integrated_dashboard

#### Imports:
- `import argparse`
- `import datetime`
- `import subprocess`
- `import time`

#### Imported by:

### dashboard.web_dashboard

#### Imports:
- `import argparse`
- `import datetime`

#### Imported by:

### integrated_dashboard

#### Imports:
- `import argparse`
- `import datetime`
- `import subprocess`
- `import time`

#### Imported by:

## Memory Management Modules

### .Extra_Optional.Future.Future.Extra.Open Extraction Blackwall Phase One.memory_loader

#### Imports:

#### Imported by:

### .Extra_Optional.Future.Future.Extra.Open Extraction Blackwall Phase One.memory_watcher

#### Imports:
- `from watchdog.events import FileSystemEventHandler`
- `from watchdog.observers import Observer`
- `import time`

#### Imported by:

### .Extra_Optional.Future.Future.Extra.Open Extraction Blackwall Phase Two.healing_memory_engine

#### Imports:
- `import hashlib`
- `import time`

#### Imported by:

### .Extra_Optional.Future.Future.Phase 1.memory_loader

#### Imports:

#### Imported by:

### .Extra_Optional.Future.Future.Phase 2.healing_memory_engine

#### Imports:
- `import hashlib`
- `import time`

#### Imported by:

### .Extra_Optional.Future.Future.Phase 3.generate_memory_index

#### Imports:
- `import faiss`
- `import numpy as np`

#### Imported by:

### .Extra_Optional.Future.Future.Phase 4.memory_pruner_agent

#### Imports:
- `from datetime import datetime`

#### Imported by:

### .Extra_Optional.Python.Python.dynamic_memory_loader

#### Imports:
- `from watchdog.events import FileSystemEventHandler`
- `from watchdog.observers import Observer`
- `import time`

#### Imported by:

### .Extra_Optional.Python.Python.memory_manager

#### Imports:

#### Imported by:

### Copilot.fix_memory_markdown

#### Imports:

#### Imported by:

### Copilot.generate_memory_index

#### Imports:
- `from datetime import datetime`
- `import argparse`
- `import random`
- `import time`

#### Imported by:

### Copilot.reprocess_memory_files

#### Imports:
- `from datetime import datetime`
- `import time`

#### Imported by:

### Lyra_OS.Lyra Documentary.Development.memory_bridge

#### Imports:
- `from datetime import datetime`

#### Imported by:

### admin_memory_console

#### Imports:
- `import argparse`
- `import csv`

#### Imported by:

### archive.Copilot.fix_memory_markdown

#### Imports:

#### Imported by:

### archive.Copilot.generate_memory_index

#### Imports:
- `from datetime import datetime`
- `import argparse`
- `import random`
- `import time`

#### Imported by:

### archive.Copilot.reprocess_memory_files

#### Imports:
- `from datetime import datetime`
- `import time`

#### Imported by:

### boot.memory_watcher

#### Imports:
- `from watchdog.events import FileSystemEventHandler`
- `from watchdog.observers import Observer`
- `import faiss`
- `import numpy as np`
- `import time`

#### Imported by:

### core.lyra_memory

#### Imports:
- `import datetime`
- `import patch_litellm`

#### Imported by:

### core.lyra_vector_memory

#### Imports:
- `from sentence_transformers import SentenceTransformer`
- `from typing import List, Dict, Any, Optional`
- `import numpy as np`

#### Imported by:

### core.semantic_memory

#### Imports:
- `from sentence_transformers import SentenceTransformer, util`
- `import numpy as np`

#### Imported by:

### generate_memory_index

#### Imports:
- `from datetime import datetime`
- `from lyra_vector_memory import generate_memory_index`

#### Imported by:
- `generate_memory_index`

### memory_diagnostics

#### Imports:
- `from datetime import datetime`

#### Imported by:

### memory_management.__init__

#### Imports:

#### Imported by:

### memory_management.fix_memory_markdown

#### Imports:

#### Imported by:

### memory_management.generate_memory_index

#### Imports:
- `from datetime import datetime`
- `import argparse`
- `import random`
- `import time`

#### Imported by:

### memory_management.process_and_learn_memories

#### Imports:
- `from datetime import datetime`
- `import random`
- `import time`

#### Imported by:

### memory_management.reprocess_memory_files

#### Imports:
- `from datetime import datetime`
- `import time`

#### Imported by:

### memory_management.summarize_and_index_memories

#### Imports:

#### Imported by:

### utils.memory_diagnostics

#### Imports:
- `from datetime import datetime`

#### Imported by:

### utils.test_memory_processing

#### Imports:
- `from utils.test_framework import BlackwallTestCase`
- `import tempfile`
- `import unittest`

#### Imported by:

