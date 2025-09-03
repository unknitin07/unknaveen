#!/usr/bin/env python3
"""
Enhanced Channel Mirroring Userbot - Professional Edition
Author: Enhanced AI Assistant
Version: 2.0

New Features:
- Multi-channel support (mirror multiple channels at once)
- Advanced message filtering and rules engine
- Database logging for message tracking
- Webhook notifications
- Auto-restart on failure
- Message scheduling and delay options
- Content moderation filters
- Statistics and analytics
- Config file support
- Better session management
- Rate limiting improvements

Requirements: Python 3.10+, pyrogram, pytgcalls, tgcrypto, aiofiles, aiosqlite
Install: pip install pyrogram pytgcalls tgcrypto aiofiles aiosqlite requests
"""

import asyncio
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import sqlite3

import aiofiles
import aiosqlite
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    FloodWait, ChatAdminRequired, UserNotParticipant,
    MessageTooLong, MediaEmpty, FileReferenceExpired
)

# Optional imports
try:
    from pytgcalls import PyTgCalls
    from pytgcalls.exceptions import NoActiveGroupCall
    PYTGCALLS_AVAILABLE = True
except ImportError:
    PYTGCALLS_AVAILABLE = False
    print("Warning: pytgcalls not available. Voice chat monitoring disabled.")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: requests not available. Webhook notifications disabled.")

# ========================================
# CONFIGURATION SYSTEM
# ========================================

class Config:
    """Enhanced configuration management"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.data = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if Path(self.config_file).exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}")
                if attempt == retry_attempts - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
        
        return None
    
    def _get_message_type(self, message: Message) -> str:
        """Get message type for logging"""
        if message.photo:
            return "photo"
        elif message.video:
            return "video"
        elif message.animation:
            return "animation"
        elif message.document:
            return "document"
        elif message.audio:
            return "audio"
        elif message.voice:
            return "voice"
        elif message.sticker:
            return "sticker"
        elif message.poll:
            return "poll"
        elif message.location:
            return "location"
        elif message.contact:
            return "contact"
        else:
            return "text"
    
    def _get_file_size(self, message: Message) -> int:
        """Get file size from message"""
        if message.document:
            return getattr(message.document, 'file_size', 0)
        elif message.photo:
            return getattr(message.photo, 'file_size', 0)
        elif message.video:
            return getattr(message.video, 'file_size', 0)
        elif message.audio:
            return getattr(message.audio, 'file_size', 0)
        elif message.voice:
            return getattr(message.voice, 'file_size', 0)
        return 0

# ========================================
# SERVICE MESSAGE HANDLER
# ========================================

class ServiceMessageHandler:
    """Handle service messages like voice chat events"""
    
    def __init__(self, client_manager: ClientManager, database: Database):
        self.client_manager = client_manager
        self.database = database
        self.notification_service = NotificationService()
    
    async def handle_service_message(self, message: Message):
        """Handle service messages"""
        try:
            if not message.service:
                return
            
            source_channel = f"@{message.chat.username}" if message.chat.username else str(message.chat.id)
            channel_mapping = config.get('channels.mapping', {})
            target_channel = channel_mapping.get(source_channel)
            
            if not target_channel:
                return
            
            service = message.service
            notification_text = None
            
            # Voice chat events
            if hasattr(service, 'group_call_started') and service.group_call_started:
                notification_text = "🎙️ **Voice Chat Started**"
            elif hasattr(service, 'group_call_ended') and service.group_call_ended:
                notification_text = "🎙️ **Voice Chat Ended**"
            elif hasattr(service, 'video_chat_started') and service.video_chat_started:
                notification_text = "📹 **Video Chat Started**"
            elif hasattr(service, 'video_chat_ended') and service.video_chat_ended:
                notification_text = "📹 **Video Chat Ended**"
            elif hasattr(service, 'live_stream_started'):
                notification_text = "🔴 **Live Stream Started**"
            elif hasattr(service, 'live_stream_ended'):
                notification_text = "🔴 **Live Stream Ended**"
            
            if notification_text:
                await self._send_service_notification(target_channel, notification_text)
                await self.database.log_message(
                    source_channel, target_channel,
                    message.id, 0, "service", notification_text
                )
                
        except Exception as e:
            logger.error(f"Service message handling error: {e}")
            await self.database.log_error("service_message", str(e), source_channel)
    
    async def _send_service_notification(self, target_channel: str, text: str):
        """Send service notification to target channel"""
        try:
            await self.client_manager.sharer_client.send_message(
                chat_id=target_channel,
                text=text
            )
            logger.info(f"Service notification sent: {text}")
        except Exception as e:
            logger.error(f"Service notification error: {e}")

# ========================================
# ENHANCED VOICE CHAT MONITOR
# ========================================

class VoiceChatMonitor:
    """Enhanced voice chat monitoring with better detection"""
    
    def __init__(self, client_manager: ClientManager, database: Database):
        self.client_manager = client_manager
        self.database = database
        self.notification_service = NotificationService()
        self.active_calls = set()
        self.monitoring = False
        
    async def start_monitoring(self):
        """Start voice chat monitoring"""
        if not config.get('features.voice_chat_monitoring', True):
            logger.info("Voice chat monitoring disabled in config")
            return
            
        if not PYTGCALLS_AVAILABLE:
            logger.warning("PyTgCalls not available. Advanced VC monitoring disabled.")
            return
        
        self.monitoring = True
        logger.info("Starting enhanced voice chat monitoring...")
        
        try:
            while self.monitoring:
                await self._check_voice_chats()
                await asyncio.sleep(30)  # Check every 30 seconds
        except Exception as e:
            logger.error(f"Voice chat monitoring error: {e}")
            await self.notification_service.send_error_notification(e, "voice chat monitoring")
    
    async def _check_voice_chats(self):
        """Check voice chat status for all source channels"""
        try:
            channel_mapping = config.get('channels.mapping', {})
            
            for source_channel in channel_mapping.keys():
                try:
                    source_chat = await self.client_manager.listener_client.get_chat(source_channel)
                    chat_id = source_chat.id
                    
                    # Check if voice chat is active
                    is_active = await self._is_voice_chat_active(chat_id)
                    
                    if is_active and chat_id not in self.active_calls:
                        # Voice chat started
                        self.active_calls.add(chat_id)
                        await self._send_vc_notification(source_channel, "🎙️ **Voice Chat Started** (detected)", True)
                        
                    elif not is_active and chat_id in self.active_calls:
                        # Voice chat ended
                        self.active_calls.discard(chat_id)
                        await self._send_vc_notification(source_channel, "🎙️ **Voice Chat Ended** (detected)", False)
                        
                except Exception as e:
                    logger.debug(f"VC check error for {source_channel}: {e}")
                    
        except Exception as e:
            logger.error(f"Voice chat check error: {e}")
    
    async def _is_voice_chat_active(self, chat_id: int) -> bool:
        """Check if voice chat is active in a chat"""
        try:
            if self.client_manager.pytgcalls:
                group_call = await self.client_manager.pytgcalls.get_group_call(chat_id)
                return group_call is not None
        except (NoActiveGroupCall, Exception):
            pass
        return False
    
    async def _send_vc_notification(self, source_channel: str, text: str, started: bool):
        """Send voice chat notification"""
        try:
            channel_mapping = config.get('channels.mapping', {})
            target_channel = channel_mapping.get(source_channel)
            
            if target_channel:
                await self.client_manager.sharer_client.send_message(
                    chat_id=target_channel,
                    text=text
                )
                logger.info(f"VC notification sent: {text}")
                
                # Log to database
                await self.database.log_message(
                    source_channel, target_channel, 0, 0, "voice_event", text
                )
                
        except Exception as e:
            logger.error(f"VC notification error: {e}")
    
    def stop_monitoring(self):
        """Stop voice chat monitoring"""
        self.monitoring = False
        logger.info("Voice chat monitoring stopped")

# ========================================
# STATISTICS AND MONITORING
# ========================================

class StatsManager:
    """Statistics and monitoring system"""
    
    def __init__(self, database: Database):
        self.database = database
        self.notification_service = NotificationService()
        self.start_time = datetime.now()
        self.last_stats_time = datetime.now()
        
    async def start_stats_monitoring(self):
        """Start periodic statistics reporting"""
        stats_interval = config.get('notifications.stats_interval', 3600)  # 1 hour default
        
        while True:
            try:
                await asyncio.sleep(stats_interval)
                await self._generate_and_send_stats()
            except Exception as e:
                logger.error(f"Stats monitoring error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _generate_and_send_stats(self):
        """Generate and send statistics"""
        try:
            # Get stats from database
            daily_stats = await self.database.get_stats(1)
            
            # Calculate uptime
            uptime = datetime.now() - self.start_time
            uptime_str = f"{uptime.days}d {uptime.seconds // 3600}h {(uptime.seconds % 3600) // 60}m"
            
            # Create stats message
            stats_text = f"""
📊 **Bot Statistics**
⏱️ Uptime: {uptime_str}
📨 Messages processed: {daily_stats['total_messages']}
📁 Files processed: {daily_stats['files_processed']}
🎯 Active sources: {daily_stats['active_sources']}
❌ Errors: {daily_stats['errors']}
📈 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """.strip()
            
            # Send to notification service
            await self.notification_service.send_stats_notification(daily_stats)
            
            logger.info(f"Stats: Messages={daily_stats['total_messages']}, Files={daily_stats['files_processed']}, Errors={daily_stats['errors']}")
            
        except Exception as e:
            logger.error(f"Stats generation error: {e}")
    
    async def get_runtime_stats(self) -> Dict[str, Any]:
        """Get current runtime statistics"""
        uptime = datetime.now() - self.start_time
        daily_stats = await self.database.get_stats(1)
        
        return {
            "uptime_seconds": int(uptime.total_seconds()),
            "uptime_human": f"{uptime.days}d {uptime.seconds // 3600}h {(uptime.seconds % 3600) // 60}m",
            "daily_stats": daily_stats,
            "start_time": self.start_time.isoformat(),
            "current_time": datetime.now().isoformat()
        }

# ========================================
# MAIN BOT ORCHESTRATOR
# ========================================

class ChannelMirrorBot:
    """Main bot orchestrator class"""
    
    def __init__(self):
        self.client_manager = ClientManager()
        self.database = Database(config.get('database.file', 'mirror_bot.db'))
        self.message_processor = None
        self.service_handler = None
        self.voice_monitor = None
        self.stats_manager = None
        self.running = False
        
    async def initialize(self) -> bool:
        """Initialize all bot components"""
        try:
            logger.info("Initializing Channel Mirror Bot...")
            
            # Initialize database
            if config.get('database.enabled', True):
                await self.database.init_db()
                logger.info("✅ Database initialized")
            
            # Initialize clients
            if not await self.client_manager.initialize():
                return False
            
            if not await self.client_manager.start_clients():
                return False
            
            # Initialize processors
            self.message_processor = MessageProcessor(self.client_manager, self.database)
            self.service_handler = ServiceMessageHandler(self.client_manager, self.database)
            self.voice_monitor = VoiceChatMonitor(self.client_manager, self.database)
            self.stats_manager = StatsManager(self.database)
            
            # Setup message handlers
            self._setup_handlers()
            
            logger.info("✅ Bot initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            return False
    
    def _setup_handlers(self):
        """Setup pyrogram message handlers"""
        # Regular message handler
        @self.client_manager.listener_client.on_message(
            filters.chat(list(config.get('channels.mapping', {}).keys()))
        )
        async def handle_message(client: Client, message: Message):
            await self.message_processor.process_message(message)
        
        # Service message handler
        @self.client_manager.listener_client.on_message(
            filters.chat(list(config.get('channels.mapping', {}).keys())) & filters.service
        )
        async def handle_service(client: Client, message: Message):
            await self.service_handler.handle_service_message(message)
    
    async def start(self):
        """Start the bot"""
        try:
            logger.info("🚀 Starting Channel Mirror Bot...")
            self.running = True
            
            # Start background tasks
            tasks = [
                self.client_manager.listener_client.idle(),
                self.voice_monitor.start_monitoring(),
                self.stats_manager.start_stats_monitoring()
            ]
            
            # Database cleanup task
            if config.get('database.enabled', True):
                async def cleanup_task():
                    while self.running:
                        await asyncio.sleep(86400)  # Daily cleanup
                        cleanup_days = config.get('database.cleanup_days', 30)
                        await self.database.cleanup_old_records(cleanup_days)
                
                tasks.append(cleanup_task())
            
            # Print startup info
            channel_mapping = config.get('channels.mapping', {})
            logger.info(f"📡 Monitoring {len(channel_mapping)} channel pairs")
            for source, target in channel_mapping.items():
                logger.info(f"   {source} -> {target}")
            
            logger.info("✅ Bot is running! Press Ctrl+C to stop...")
            
            # Run all tasks
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except KeyboardInterrupt:
            logger.info("👋 Shutdown requested by user")
        except Exception as e:
            logger.error(f"💥 Runtime error: {e}")
            
            # Try to restart if configured
            if config.get('features.auto_restart', False):
                logger.info("🔄 Attempting auto-restart...")
                if await self.client_manager.restart_clients():
                    logger.info("✅ Restart successful, continuing...")
                    await self.start()  # Recursive restart
                else:
                    logger.error("❌ Restart failed")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Gracefully shutdown the bot"""
        try:
            logger.info("🔄 Shutting down bot...")
            self.running = False
            
            # Stop voice monitoring
            if self.voice_monitor:
                self.voice_monitor.stop_monitoring()
            
            # Stop clients
            await self.client_manager.stop_clients()
            
            # Send shutdown notification
            if hasattr(self, 'message_processor') and self.message_processor:
                await self.message_processor.notification_service.send_notification(
                    "Bot Shutdown",
                    f"Bot stopped after processing {getattr(self.message_processor, 'processed_count', 0)} messages",
                    "info"
                )
            
            logger.info("✅ Bot stopped successfully")
            
        except Exception as e:
            logger.error(f"Shutdown error: {e}")

# ========================================
# UTILITY FUNCTIONS
# ========================================

async def validate_configuration() -> bool:
    """Validate bot configuration"""
    logger.info("Validating configuration...")
    
    # Check API credentials
    api_id = config.get('api.api_id')
    api_hash = config.get('api.api_hash')
    
    if not api_id or not api_hash or api_id == 12345678:
        logger.error("❌ API credentials not configured!")
        logger.error("Please edit config.json with your API credentials from https://my.telegram.org")
        return False
    
    # Check channel configuration
    channel_mapping = config.get('channels.mapping', {})
    if not channel_mapping:
        logger.error("❌ No channel mapping configured!")
        logger.error("Please configure source -> target channel mapping in config.json")
        return False
    
    # Check replacement file
    replacement_file = config.get('replacement.file_path', 'naveen.apk')
    if not os.path.exists(replacement_file):
        logger.warning(f"⚠️ Replacement file not found: {replacement_file}")
        logger.warning("File replacement feature will not work!")
    else:
        size_mb = os.path.getsize(replacement_file) / (1024 * 1024)
        logger.info(f"✅ Replacement file found: {size_mb:.1f} MB")
    
    # Check optional dependencies
    missing_deps = []
    if not PYTGCALLS_AVAILABLE and config.get('features.voice_chat_monitoring', True):
        missing_deps.append('pytgcalls')
    
    if not REQUESTS_AVAILABLE and config.get('notifications.webhook_url'):
        missing_deps.append('requests')
    
    if missing_deps:
        logger.warning(f"⚠️ Missing optional dependencies: {', '.join(missing_deps)}")
        logger.warning("Some features may be disabled")
    
    logger.info("✅ Configuration validation completed")
    return True

def print_startup_banner():
    """Print startup banner"""
    print("=" * 80)
    print("  Enhanced Channel Mirroring Userbot v2.0")
    print("  Professional Edition with Advanced Features")
    print("=" * 80)
    print(f"  Configuration file: {config.config_file}")
    print(f"  Python version: {sys.version.split()[0]}")
    print(f"  Database: {'Enabled' if config.get('database.enabled') else 'Disabled'}")
    print(f"  Voice monitoring: {'Enabled' if PYTGCALLS_AVAILABLE and config.get('features.voice_chat_monitoring') else 'Disabled'}")
    print(f"  Webhooks: {'Enabled' if config.get('notifications.webhook_url') else 'Disabled'}")
    print("=" * 80)

# ========================================
# MAIN FUNCTION
# ========================================

async def main():
    """Main function - entry point"""
    print_startup_banner()
    
    # Validate configuration
    if not await validate_configuration():
        logger.error("Configuration validation failed. Please fix configuration and restart.")
        return
    
    # Create and start bot
    bot = ChannelMirrorBot()
    
    if not await bot.initialize():
        logger.error("Bot initialization failed. Exiting.")
        return
    
    # Start the bot
    await bot.start()

# ========================================
# ENTRY POINT
# ========================================

if __name__ == "__main__":
    # Python version check
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ is required!")
        print(f"You have Python {sys.version}")
        sys.exit(1)
    
    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("sessions").mkdir(exist_ok=True)  # For session files
    
    # Run the bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        logger.exception("Fatal error occurred")
        sys.exit(1)
                print(f"Error loading config: {e}")
                return self.get_default_config()
        else:
            config = self.get_default_config()
            self.save_config(config)
            return config
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "api": {
                "api_id": 12345678,
                "api_hash": "your_api_hash_here"
            },
            "channels": {
                "sources": ["@source_channel1", "@source_channel2"],
                "targets": ["@target_channel1", "@target_channel2"],
                "mapping": {
                    "@source_channel1": "@target_channel1",
                    "@source_channel2": "@target_channel2"
                }
            },
            "sessions": {
                "listener": "listener_account",
                "sharer": "sharer_account"
            },
            "replacement": {
                "file_path": "naveen.apk",
                "invitation_code": "511726258529",
                "replace_all_files": True
            },
            "features": {
                "voice_chat_monitoring": True,
                "message_scheduling": False,
                "content_filtering": False,
                "auto_delete_old": False,
                "forward_mode": False
            },
            "delays": {
                "message_delay": 0.5,
                "flood_wait_multiplier": 1.2,
                "retry_attempts": 3
            },
            "filters": {
                "blocked_words": ["spam", "scam"],
                "allowed_file_types": [".apk", ".pdf", ".txt", ".jpg", ".png"],
                "max_file_size_mb": 50,
                "min_message_length": 0
            },
            "notifications": {
                "webhook_url": "",
                "notify_errors": True,
                "notify_stats": True,
                "stats_interval": 3600
            },
            "database": {
                "enabled": True,
                "file": "mirror_bot.db",
                "cleanup_days": 30
            },
            "logging": {
                "level": "INFO",
                "max_file_size_mb": 10,
                "backup_count": 5
            }
        }
    
    def save_config(self, config: Dict[str, Any] = None):
        """Save configuration to file"""
        if config is None:
            config = self.data
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default=None):
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self.data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

# Initialize configuration
config = Config()

# ========================================
# DATABASE SYSTEM
# ========================================

class Database:
    """SQLite database for message tracking and analytics"""
    
    def __init__(self, db_file: str):
        self.db_file = db_file
        
    async def init_db(self):
        """Initialize database tables"""
        async with aiosqlite.connect(self.db_file) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_channel TEXT,
                    target_channel TEXT,
                    source_message_id INTEGER,
                    target_message_id INTEGER,
                    message_type TEXT,
                    content_preview TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'sent',
                    file_size INTEGER DEFAULT 0
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS errors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_type TEXT,
                    error_message TEXT,
                    channel TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE,
                    messages_processed INTEGER DEFAULT 0,
                    files_replaced INTEGER DEFAULT 0,
                    errors_count INTEGER DEFAULT 0,
                    voice_events INTEGER DEFAULT 0
                )
            """)
            
            await db.commit()
    
    async def log_message(self, source_channel: str, target_channel: str, 
                         source_msg_id: int, target_msg_id: int, 
                         msg_type: str, content: str = "", file_size: int = 0):
        """Log processed message"""
        try:
            async with aiosqlite.connect(self.db_file) as db:
                await db.execute("""
                    INSERT INTO messages 
                    (source_channel, target_channel, source_message_id, 
                     target_message_id, message_type, content_preview, file_size)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (source_channel, target_channel, source_msg_id, 
                     target_msg_id, msg_type, content[:100], file_size))
                await db.commit()
        except Exception as e:
            logger.error(f"Database logging error: {e}")
    
    async def log_error(self, error_type: str, error_msg: str, channel: str = ""):
        """Log error to database"""
        try:
            async with aiosqlite.connect(self.db_file) as db:
                await db.execute("""
                    INSERT INTO errors (error_type, error_message, channel)
                    VALUES (?, ?, ?)
                """, (error_type, str(error_msg)[:500], channel))
                await db.commit()
        except Exception as e:
            logger.error(f"Error logging to DB: {e}")
    
    async def get_stats(self, days: int = 1) -> Dict[str, int]:
        """Get statistics for last N days"""
        try:
            async with aiosqlite.connect(self.db_file) as db:
                date_filter = (datetime.now() - timedelta(days=days)).date()
                
                cursor = await db.execute("""
                    SELECT COUNT(*) as total_messages,
                           SUM(CASE WHEN message_type LIKE '%file%' THEN 1 ELSE 0 END) as files_processed,
                           COUNT(DISTINCT source_channel) as active_sources
                    FROM messages 
                    WHERE date(timestamp) >= ?
                """, (date_filter,))
                
                row = await cursor.fetchone()
                
                cursor = await db.execute("""
                    SELECT COUNT(*) as error_count
                    FROM errors 
                    WHERE date(timestamp) >= ?
                """, (date_filter,))
                
                error_row = await cursor.fetchone()
                
                return {
                    'total_messages': row[0] if row else 0,
                    'files_processed': row[1] if row else 0,
                    'active_sources': row[2] if row else 0,
                    'errors': error_row[0] if error_row else 0
                }
        except Exception as e:
            logger.error(f"Stats error: {e}")
            return {'total_messages': 0, 'files_processed': 0, 'active_sources': 0, 'errors': 0}
    
    async def cleanup_old_records(self, days: int = 30):
        """Clean up old database records"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).date()
            async with aiosqlite.connect(self.db_file) as db:
                await db.execute("DELETE FROM messages WHERE date(timestamp) < ?", (cutoff_date,))
                await db.execute("DELETE FROM errors WHERE date(timestamp) < ?", (cutoff_date,))
                await db.commit()
                logger.info(f"Cleaned up records older than {days} days")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

# ========================================
# ENHANCED LOGGING SETUP
# ========================================

def setup_logging():
    """Setup enhanced logging with rotation"""
    Path("logs").mkdir(exist_ok=True)
    
    log_level = getattr(logging, config.get('logging.level', 'INFO').upper())
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    # File handler with rotation
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
        'logs/mirror_bot.log',
        maxBytes=config.get('logging.max_file_size_mb', 10) * 1024 * 1024,
        backupCount=config.get('logging.backup_count', 5)
    )
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Setup logger
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()

# ========================================
# ENHANCED LINK REPLACEMENT ENGINE
# ========================================

class LinkReplacer:
    """Advanced link replacement with pattern matching"""
    
    def __init__(self):
        self.invitation_code = config.get('replacement.invitation_code', '511726258529')
        self.patterns = [
            # Standard invitation code pattern
            re.compile(r'(https?://[^\s)\]]*?)([?&])invitationCode=[^&\s)\]]*', re.IGNORECASE),
            # Alternative patterns
            re.compile(r'(https?://[^\s)\]]*?)([?&])invite=[^&\s)\]]*', re.IGNORECASE),
            re.compile(r'(https?://[^\s)\]]*?)([?&])ref=[^&\s)\]]*', re.IGNORECASE),
        ]
    
    def replace_links(self, text: str) -> Tuple[str, int]:
        """Replace invitation codes in text, return (new_text, replacements_count)"""
        if not text:
            return text, 0
        
        modified_text = text
        total_replacements = 0
        
        for pattern in self.patterns:
            def replacer(match):
                nonlocal total_replacements
                url_part = match.group(1)
                separator = match.group(2)
                param_name = self._extract_param_name(match.group(0))
                new_url = f"{url_part}{separator}{param_name}={self.invitation_code}"
                logger.debug(f"Link replaced: {match.group(0)} -> {new_url}")
                total_replacements += 1
                return new_url
            
            modified_text = pattern.sub(replacer, modified_text)
        
        return modified_text, total_replacements
    
    def _extract_param_name(self, matched_text: str) -> str:
        """Extract parameter name from matched text"""
        if 'invitationCode' in matched_text:
            return 'invitationCode'
        elif 'invite' in matched_text:
            return 'invite'
        elif 'ref' in matched_text:
            return 'ref'
        return 'invitationCode'

# ========================================
# CONTENT FILTER SYSTEM
# ========================================

class ContentFilter:
    """Advanced content filtering system"""
    
    def __init__(self):
        self.blocked_words = config.get('filters.blocked_words', [])
        self.allowed_file_types = config.get('filters.allowed_file_types', [])
        self.max_file_size = config.get('filters.max_file_size_mb', 50) * 1024 * 1024
        self.min_message_length = config.get('filters.min_message_length', 0)
    
    def should_process_message(self, message: Message) -> Tuple[bool, str]:
        """Check if message should be processed"""
        if not config.get('features.content_filtering', False):
            return True, ""
        
        # Check text content
        text = message.text or message.caption or ""
        
        # Minimum length check
        if len(text.strip()) < self.min_message_length:
            return False, "Message too short"
        
        # Blocked words check
        text_lower = text.lower()
        for word in self.blocked_words:
            if word.lower() in text_lower:
                return False, f"Contains blocked word: {word}"
        
        # File type check
        if message.document and self.allowed_file_types:
            file_name = getattr(message.document, 'file_name', '') or ''
            file_ext = Path(file_name).suffix.lower()
            if file_ext and file_ext not in self.allowed_file_types:
                return False, f"File type not allowed: {file_ext}"
        
        # File size check
        file_size = 0
        if message.document:
            file_size = getattr(message.document, 'file_size', 0)
        elif message.photo:
            file_size = getattr(message.photo, 'file_size', 0)
        elif message.video:
            file_size = getattr(message.video, 'file_size', 0)
        
        if file_size > self.max_file_size:
            return False, f"File too large: {file_size / 1024 / 1024:.1f}MB"
        
        return True, ""

# ========================================
# NOTIFICATION SYSTEM
# ========================================

class NotificationService:
    """Webhook and notification service"""
    
    def __init__(self):
        self.webhook_url = config.get('notifications.webhook_url', '')
        self.notify_errors = config.get('notifications.notify_errors', True)
        self.notify_stats = config.get('notifications.notify_stats', True)
        
    async def send_notification(self, title: str, message: str, level: str = "info"):
        """Send notification via webhook"""
        if not self.webhook_url or not REQUESTS_AVAILABLE:
            return
        
        try:
            payload = {
                "title": title,
                "message": message,
                "level": level,
                "timestamp": datetime.now().isoformat(),
                "bot": "Channel Mirror Bot"
            }
            
            # Run in thread to avoid blocking
            import threading
            thread = threading.Thread(
                target=self._send_webhook,
                args=(payload,)
            )
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            logger.error(f"Notification error: {e}")
    
    def _send_webhook(self, payload: Dict[str, Any]):
        """Send webhook in separate thread"""
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Webhook send error: {e}")
    
    async def send_error_notification(self, error: Exception, context: str = ""):
        """Send error notification"""
        if self.notify_errors:
            await self.send_notification(
                "Bot Error",
                f"Error in {context}: {str(error)[:200]}",
                "error"
            )
    
    async def send_stats_notification(self, stats: Dict[str, int]):
        """Send statistics notification"""
        if self.notify_stats:
            message = f"Messages: {stats['total_messages']}, Files: {stats['files_processed']}, Errors: {stats['errors']}"
            await self.send_notification(
                "Daily Stats",
                message,
                "info"
            )

# ========================================
# CLIENT MANAGER
# ========================================

class ClientManager:
    """Enhanced client management with auto-restart"""
    
    def __init__(self):
        self.listener_client = None
        self.sharer_client = None
        self.pytgcalls = None
        self.restart_count = 0
        self.max_restarts = 5
        
    async def initialize(self) -> bool:
        """Initialize clients"""
        try:
            api_id = config.get('api.api_id')
            api_hash = config.get('api.api_hash')
            
            if not api_id or not api_hash or api_id == 12345678:
                logger.error("❌ API credentials not configured!")
                return False
            
            # Initialize clients
            self.listener_client = Client(
                config.get('sessions.listener', 'listener_account'),
                api_id=api_id,
                api_hash=api_hash
            )
            
            self.sharer_client = Client(
                config.get('sessions.sharer', 'sharer_account'),
                api_id=api_id,
                api_hash=api_hash
            )
            
            # Initialize PyTgCalls if available
            if PYTGCALLS_AVAILABLE and config.get('features.voice_chat_monitoring', True):
                self.pytgcalls = PyTgCalls(self.listener_client)
            
            return True
            
        except Exception as e:
            logger.error(f"Client initialization error: {e}")
            return False
    
    async def start_clients(self) -> bool:
        """Start both clients"""
        try:
            logger.info("Starting clients...")
            await self.listener_client.start()
            await self.sharer_client.start()
            
            if self.pytgcalls:
                await self.pytgcalls.start()
            
            return await self._verify_access()
            
        except Exception as e:
            logger.error(f"Client start error: {e}")
            return False
    
    async def _verify_access(self) -> bool:
        """Verify access to configured channels"""
        try:
            channel_mapping = config.get('channels.mapping', {})
            
            for source, target in channel_mapping.items():
                try:
                    source_chat = await self.listener_client.get_chat(source)
                    target_chat = await self.sharer_client.get_chat(target)
                    logger.info(f"✅ {source} -> {target}")
                except Exception as e:
                    logger.error(f"❌ Channel access error {source} -> {target}: {e}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Access verification error: {e}")
            return False
    
    async def stop_clients(self):
        """Stop all clients"""
        try:
            tasks = []
            if self.pytgcalls:
                tasks.append(self.pytgcalls.stop())
            if self.listener_client:
                tasks.append(self.listener_client.stop())
            if self.sharer_client:
                tasks.append(self.sharer_client.stop())
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                
        except Exception as e:
            logger.error(f"Client stop error: {e}")
    
    async def restart_clients(self) -> bool:
        """Restart clients after failure"""
        if self.restart_count >= self.max_restarts:
            logger.error("Max restart attempts reached!")
            return False
        
        self.restart_count += 1
        logger.info(f"Restarting clients (attempt {self.restart_count})...")
        
        await self.stop_clients()
        await asyncio.sleep(5)  # Wait before restart
        
        return await self.start_clients()

# ========================================
# ENHANCED MESSAGE PROCESSOR
# ========================================

class MessageProcessor:
    """Enhanced message processing with advanced features"""
    
    def __init__(self, client_manager: ClientManager, database: Database):
        self.client_manager = client_manager
        self.database = database
        self.link_replacer = LinkReplacer()
        self.content_filter = ContentFilter()
        self.notification_service = NotificationService()
        self.replacement_file = config.get('replacement.file_path', 'naveen.apk')
        self.message_delay = config.get('delays.message_delay', 0.5)
        self.processed_count = 0
    
    async def process_message(self, message: Message):
        """Process a single message with all enhancements"""
        try:
            source_channel = f"@{message.chat.username}" if message.chat.username else str(message.chat.id)
            
            # Get target channel
            channel_mapping = config.get('channels.mapping', {})
            target_channel = channel_mapping.get(source_channel)
            
            if not target_channel:
                logger.warning(f"No target channel mapped for {source_channel}")
                return
            
            # Content filtering
            should_process, filter_reason = self.content_filter.should_process_message(message)
            if not should_process:
                logger.info(f"Message filtered: {filter_reason}")
                return
            
            # Skip service messages (handled separately)
            if message.service:
                return
            
            # Add delay for rate limiting
            if self.message_delay > 0:
                await asyncio.sleep(self.message_delay)
            
            # Process the message
            await self._send_processed_message(message, source_channel, target_channel)
            self.processed_count += 1
            
            if self.processed_count % 100 == 0:
                logger.info(f"Processed {self.processed_count} messages")
            
        except Exception as e:
            logger.error(f"Message processing error: {e}")
            await self.database.log_error("message_processing", str(e), source_channel)
            await self.notification_service.send_error_notification(e, "message processing")
    
    async def _send_processed_message(self, message: Message, source_channel: str, target_channel: str):
        """Send processed message to target channel"""
        try:
            # Process text/caption
            original_text = message.text or message.caption or ""
            modified_text, replacements = self.link_replacer.replace_links(original_text)
            
            if replacements > 0:
                logger.info(f"Made {replacements} link replacements")
            
            # Determine if file should be replaced
            should_replace_file = config.get('replacement.replace_all_files', True) and any([
                message.document,
                message.audio,
                message.voice
            ])
            
            # Send message based on type
            if should_replace_file and os.path.exists(self.replacement_file):
                sent_msg = await self._send_replacement_file(target_channel, modified_text, message)
                msg_type = "file_replacement"
                file_size = os.path.getsize(self.replacement_file)
            else:
                sent_msg = await self._send_media_message(message, target_channel, modified_text)
                msg_type = self._get_message_type(message)
                file_size = self._get_file_size(message)
            
            # Log to database
            if sent_msg and config.get('database.enabled', True):
                await self.database.log_message(
                    source_channel, target_channel,
                    message.id, sent_msg.id,
                    msg_type, modified_text[:100], file_size
                )
            
        except Exception as e:
            logger.error(f"Send message error: {e}")
            raise
    
    async def _send_replacement_file(self, target_channel: str, caption: str, original_message: Message) -> Optional[Message]:
        """Send replacement APK file"""
        return await self._handle_flood_wait(
            self.client_manager.sharer_client.send_document,
            chat_id=target_channel,
            document=self.replacement_file,
            caption=caption if caption else None,
            parse_mode=enums.ParseMode.HTML if original_message.entities else None
        )
    
    async def _send_media_message(self, message: Message, target_channel: str, text: str) -> Optional[Message]:
        """Send media message based on type"""
        client = self.client_manager.sharer_client
        
        if message.photo:
            return await self._handle_flood_wait(
                client.send_photo,
                chat_id=target_channel,
                photo=message.photo.file_id,
                caption=text if text else None,
                parse_mode=enums.ParseMode.HTML if message.entities else None
            )
        elif message.video:
            return await self._handle_flood_wait(
                client.send_video,
                chat_id=target_channel,
                video=message.video.file_id,
                caption=text if text else None,
                parse_mode=enums.ParseMode.HTML if message.entities else None
            )
        elif message.animation:
            return await self._handle_flood_wait(
                client.send_animation,
                chat_id=target_channel,
                animation=message.animation.file_id,
                caption=text if text else None,
                parse_mode=enums.ParseMode.HTML if message.entities else None
            )
        elif message.document:
            return await self._handle_flood_wait(
                client.send_document,
                chat_id=target_channel,
                document=message.document.file_id,
                caption=text if text else None,
                parse_mode=enums.ParseMode.HTML if message.entities else None
            )
        elif message.audio:
            return await self._handle_flood_wait(
                client.send_audio,
                chat_id=target_channel,
                audio=message.audio.file_id,
                caption=text if text else None,
                parse_mode=enums.ParseMode.HTML if message.entities else None
            )
        elif message.voice:
            return await self._handle_flood_wait(
                client.send_voice,
                chat_id=target_channel,
                voice=message.voice.file_id,
                caption=text if text else None,
                parse_mode=enums.ParseMode.HTML if message.entities else None
            )
        elif message.sticker:
            return await self._handle_flood_wait(
                client.send_sticker,
                chat_id=target_channel,
                sticker=message.sticker.file_id
            )
        elif message.poll:
            return await self._handle_flood_wait(
                client.send_poll,
                chat_id=target_channel,
                question=message.poll.question,
                options=[option.text for option in message.poll.options],
                is_anonymous=message.poll.is_anonymous,
                allows_multiple_answers=message.poll.allows_multiple_answers
            )
        elif message.location:
            return await self._handle_flood_wait(
                client.send_location,
                chat_id=target_channel,
                latitude=message.location.latitude,
                longitude=message.location.longitude
            )
        elif message.contact:
            return await self._handle_flood_wait(
                client.send_contact,
                chat_id=target_channel,
                phone_number=message.contact.phone_number,
                first_name=message.contact.first_name,
                last_name=message.contact.last_name or ""
            )
        elif text:
            return await self._handle_flood_wait(
                client.send_message,
                chat_id=target_channel,
                text=text,
                parse_mode=enums.ParseMode.HTML if message.entities else None
            )
        
        return None
    
    async def _handle_flood_wait(self, func, *args, **kwargs):
        """Enhanced flood wait handling"""
        retry_attempts = config.get('delays.retry_attempts', 3)
        multiplier = config.get('delays.flood_wait_multiplier', 1.2)
        
        for attempt in range(retry_attempts):
            try:
                return await func(*args, **kwargs)
            except FloodWait as e:
                wait_time = min(e.value * multiplier, 300)  # Max 5 minutes
                logger.warning(f"FloodWait: waiting {wait_time}s (attempt {attempt + 1})")
                await asyncio.sleep(wait_time)
            except (MessageTooLong, MediaEmpty, FileReferenceExpired) as e:
                logger.error(f"Unrecoverable error in {func.__name__}: {e}")
                break
            except Exception as e: