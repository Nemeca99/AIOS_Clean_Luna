#!/usr/bin/env python3
"""
CARMA Mycelium Network
Network infrastructure and user management for CARMA system
"""

import time
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional

# Import from parent module
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from support_core.support_core import SystemConfig


class ConnectionStatus(Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    BLOCKED = "blocked"
    SUSPICIOUS = "suspicious"


class TrafficType(Enum):
    NORMAL = "normal"
    SUSPICIOUS = "suspicious"
    MALICIOUS = "malicious"
    UNKNOWN = "unknown"


@dataclass
class UserConnection:
    user_id: str
    connection_id: str
    slot_number: int
    api_key: str
    connected_at: float
    last_activity: float
    status: ConnectionStatus
    internal_ip: str
    traffic_count: int = 0
    suspicious_activity: int = 0


@dataclass
class TrafficEvent:
    timestamp: float
    source_ip: str
    destination_ip: str
    user_id: str
    traffic_type: TrafficType
    data_size: int
    protocol: str
    suspicious_score: float = 0.0


@dataclass
class ServerBlock:
    block_id: str
    external_ip: str
    internal_network: str
    max_users: int = 60
    connected_users: Dict[int, UserConnection] = None
    traffic_monitor: List[TrafficEvent] = None
    blocked_ips: set = None
    suspicious_ips: set = None
    
    def __post_init__(self):
        if self.connected_users is None:
            self.connected_users = {}
        if self.traffic_monitor is None:
            self.traffic_monitor = []
        if self.blocked_ips is None:
            self.blocked_ips = set()
        if self.suspicious_ips is None:
            self.suspicious_ips = set()


class CARMAMyceliumNetwork:
    """Mycelium-like internal network for CARMA system."""
    
    def __init__(self, num_initial_blocks: int = SystemConfig.SERVER_BLOCKS, users_per_block: int = SystemConfig.MAX_USERS_PER_BLOCK):
        self.server_blocks = {}
        self.total_users = 0
        self.traffic_monitoring = False
        self.traffic_thread = None
        
        # Create initial server blocks
        for i in range(num_initial_blocks):
            block_id = f"block_{i:03d}"
            external_ip = self._generate_external_ip(i)
            self.create_server_block(block_id, external_ip)
        
        print(" CARMA Mycelium Network Initialized")
        print(f"   Server blocks: {len(self.server_blocks)}")
        print(f"   Max users per block: {users_per_block}")
        print(f"   Total capacity: {len(self.server_blocks) * users_per_block} users")
    
    def create_server_block(self, block_id: str, external_ip: str) -> ServerBlock:
        """Create a new server block."""
        internal_network = self._generate_internal_network(block_id)
        
        server_block = ServerBlock(
            block_id=block_id,
            external_ip=external_ip,
            internal_network=internal_network,
            max_users=60
        )
        
        self.server_blocks[block_id] = server_block
        return server_block
    
    def _generate_external_ip(self, index: int) -> str:
        """Generate external IP address."""
        base_ip = "192.168.1"
        return f"{base_ip}.{index + 1}"
    
    def _generate_internal_network(self, block_id: str) -> str:
        """Generate internal network address."""
        block_num = int(block_id.split('_')[1])
        return f"10.{block_num // 256}.{block_num % 256}.0/24"
    
    def connect_user(self, block_id: str, user_id: str, api_key: str) -> Optional[UserConnection]:
        """Connect a user to a server block."""
        if block_id not in self.server_blocks:
            return None
        
        server_block = self.server_blocks[block_id]
        
        # Check if user already connected
        for conn in server_block.connected_users.values():
            if conn.user_id == user_id:
                return conn
        
        # Find available slot
        slot = self._find_available_slot(server_block)
        if slot is None:
            return None
        
        # Create connection
        connection = UserConnection(
            user_id=user_id,
            connection_id=f"conn_{user_id}_{int(time.time())}",
            slot_number=slot,
            api_key=api_key,
            connected_at=time.time(),
            last_activity=time.time(),
            status=ConnectionStatus.CONNECTED,
            internal_ip=self._generate_internal_ip(server_block, slot)
        )
        
        server_block.connected_users[slot] = connection
        self.total_users += 1
        
        return connection
    
    def _find_available_slot(self, server_block: ServerBlock) -> Optional[int]:
        """Find available slot in server block."""
        for slot in range(server_block.max_users):
            if slot not in server_block.connected_users:
                return slot
        return None
    
    def _generate_internal_ip(self, server_block: ServerBlock, slot: int) -> str:
        """Generate internal IP for user slot."""
        base_network = server_block.internal_network.split('/')[0]
        base_parts = base_network.split('.')
        return f"{base_parts[0]}.{base_parts[1]}.{base_parts[2]}.{slot + 1}"
    
    def get_network_status(self) -> Dict[str, any]:
        """Get network status."""
        total_connected = sum(len(block.connected_users) for block in self.server_blocks.values())
        total_capacity = len(self.server_blocks) * 60
        
        return {
            'total_blocks': len(self.server_blocks),
            'total_connected_users': total_connected,
            'total_capacity': total_capacity,
            'utilization_percentage': (total_connected / total_capacity) * 100 if total_capacity > 0 else 0,
            'traffic_monitoring': self.traffic_monitoring
        }

