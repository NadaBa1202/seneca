"""
Dragontail (Data Dragon) data manager for League of Legends static game data.

This module provides efficient access to champion, item, rune, and other static
game data from Riot's Data Dragon, with caching and search capabilities.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import logging
from functools import lru_cache
import asyncio
from concurrent.futures import ThreadPoolExecutor

from ..config import get_config
from ..models import Champion, Item, RuneTree, ChampionSpell, ChampionPassive, ChampionStats

logger = logging.getLogger(__name__)
config = get_config()


class DragontailDataManager:
    """
    Manager for accessing and caching Dragontail (Data Dragon) data.
    
    Provides efficient access to champions, items, runes, and other static
    game data with intelligent caching and search capabilities.
    """
    
    def __init__(self, data_path: Optional[Path] = None, language: str = "en_US"):
        self.data_path = data_path or config.data.dragontail_data_path
        self.language = language
        self.version = self._get_version()
        
        # Cache for loaded data
        self._champions_cache: Optional[Dict[str, Champion]] = None
        self._items_cache: Optional[Dict[str, Item]] = None
        self._runes_cache: Optional[List[RuneTree]] = None
        self._summoner_spells_cache: Optional[Dict[str, Any]] = None
        
        # Initialize data synchronously to avoid async issues
        self._load_data_sync()
        
        logger.info(f"Initialized DragontailDataManager with version {self.version}, language {language}")
    
    def _load_data_sync(self):
        """Load basic data synchronously to avoid async executor issues."""
        try:
            # Load champions synchronously
            self._load_champions_sync()
            # Load items synchronously  
            self._load_items_sync()
            # Load runes synchronously
            self._load_runes_sync()
        except Exception as e:
            logger.error(f"Error loading data synchronously: {e}")
    
    def _load_champions_sync(self):
        """Load champions synchronously."""
        try:
            champions = {}
            # The data_path now points directly to the 15.18.1 directory
            champion_dir = self.data_path / "data" / self.language / "champion"
            
            if not champion_dir.exists():
                logger.warning(f"Champion directory does not exist: {champion_dir}")
                self._champions_cache = {}
                return
            
            champion_files = list(champion_dir.glob("*.json"))
            logger.info(f"Found {len(champion_files)} champion files in {champion_dir}")
            
            for file_path in champion_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if 'data' in data:
                            for champ_key, champ_data in data['data'].items():
                                champion = self._parse_champion_data(champ_data)
                                champions[champ_key] = champion
                        else:
                            logger.warning(f"No 'data' key found in {file_path}")
                except Exception as e:
                    logger.warning(f"Error loading champion file {file_path}: {e}")
            
            self._champions_cache = champions
            logger.info(f"Successfully loaded {len(champions)} champions synchronously")
            
        except Exception as e:
            logger.error(f"Error loading champions: {e}")
            self._champions_cache = {}
    
    def _get_version(self) -> str:
        """Get the Data Dragon version from the manifest."""
        try:
            manifest_path = self.data_path / "manifest.json"
            if manifest_path.exists():
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                    return manifest.get("v", "unknown")
            return "unknown"
        except Exception as e:
            logger.warning(f"Could not read version from manifest: {e}")
            return "unknown"
    
    def _get_data_file_path(self, filename: str) -> Path:
        """Get the full path to a data file."""
        return self.data_path / "data" / self.language / filename
    
    async def _load_json_file(self, filepath: Path) -> Optional[Dict[str, Any]]:
        """Asynchronously load a JSON file."""
        if not filepath.exists():
            logger.warning(f"Data file not found: {filepath}")
            return None
        
        try:
            loop = asyncio.get_event_loop()
            with self._executor:
                def load_file():
                    with open(filepath, 'r', encoding='utf-8') as f:
                        return json.load(f)
                return await loop.run_in_executor(self._executor, load_file)
        except Exception as e:
            logger.error(f"Error loading JSON file {filepath}: {e}")
            return None
    
    async def load_champions(self, force_reload: bool = False) -> Dict[str, Champion]:
        """
        Load all champion data.
        
        Args:
            force_reload: Force reload even if cached
            
        Returns:
            Dictionary mapping champion IDs to Champion objects
        """
        if self._champions_cache is not None and not force_reload:
            return self._champions_cache
        
        logger.info("Loading champion data...")
        champions = {}
        
        # Load champion list first
        champion_list_path = self._get_data_file_path("champion.json")
        champion_list_data = await self._load_json_file(champion_list_path)
        
        if not champion_list_data:
            logger.error("Failed to load champion list")
            return {}
        
        # Load individual champion files for detailed data
        champion_dir = self._get_data_file_path("champion")
        if champion_dir.is_dir():
            for champion_file in champion_dir.glob("*.json"):
                champion_data = await self._load_json_file(champion_file)
                if champion_data and "data" in champion_data:
                    for champion_id, raw_data in champion_data["data"].items():
                        try:
                            champion = self._parse_champion_data(raw_data)
                            champions[champion_id] = champion
                        except Exception as e:
                            logger.error(f"Error parsing champion {champion_id}: {e}")
        
        self._champions_cache = champions
        logger.info(f"Loaded {len(champions)} champions")
        return champions
    
    def _parse_champion_data(self, raw_data: Dict[str, Any]) -> Champion:
        """Parse raw champion data into Champion model."""
        # Parse spells
        spells = []
        for spell_data in raw_data.get("spells", []):
            spell = ChampionSpell(
                id=spell_data.get("id", ""),
                name=spell_data.get("name", ""),
                description=spell_data.get("description", ""),
                tooltip=spell_data.get("tooltip", ""),
                max_rank=spell_data.get("maxrank", 5),
                cooldown=spell_data.get("cooldown", []),
                cost=spell_data.get("cost", []),
                range=spell_data.get("range", []),
                image=spell_data.get("image", {}),
                resource=spell_data.get("resource", "")
            )
            spells.append(spell)
        
        # Parse passive
        passive_data = raw_data.get("passive", {})
        passive = ChampionPassive(
            name=passive_data.get("name", ""),
            description=passive_data.get("description", ""),
            image=passive_data.get("image", {})
        )
        
        # Parse stats
        stats_data = raw_data.get("stats", {})
        stats = ChampionStats(
            hp=stats_data.get("hp", 0),
            hp_per_level=stats_data.get("hpperlevel", 0),
            mp=stats_data.get("mp", 0),
            mp_per_level=stats_data.get("mpperlevel", 0),
            move_speed=stats_data.get("movespeed", 0),
            armor=stats_data.get("armor", 0),
            armor_per_level=stats_data.get("armorperlevel", 0),
            spell_block=stats_data.get("spellblock", 0),
            spell_block_per_level=stats_data.get("spellblockperlevel", 0),
            attack_range=stats_data.get("attackrange", 0),
            attack_damage=stats_data.get("attackdamage", 0),
            attack_damage_per_level=stats_data.get("attackdamageperlevel", 0),
            attack_speed=stats_data.get("attackspeed", 0),
            attack_speed_per_level=stats_data.get("attackspeedperlevel", 0)
        )
        
        return Champion(
            id=raw_data.get("id", ""),
            key=raw_data.get("key", ""),
            name=raw_data.get("name", ""),
            title=raw_data.get("title", ""),
            lore=raw_data.get("lore", ""),
            blurb=raw_data.get("blurb", ""),
            ally_tips=raw_data.get("allytips", []),
            enemy_tips=raw_data.get("enemytips", []),
            tags=raw_data.get("tags", []),
            partype=raw_data.get("partype", ""),
            stats=stats,
            spells=spells,
            passive=passive,
            image=raw_data.get("image", {}),
            info=raw_data.get("info", {"attack": 5, "defense": 5, "magic": 5, "difficulty": 3})  # Add info field with defaults
        )
    
    async def load_items(self, force_reload: bool = False) -> Dict[str, Item]:
        """Load all item data."""
        if self._items_cache is not None and not force_reload:
            return self._items_cache
        
        logger.info("Loading item data...")
        items = {}
        
        item_file_path = self._get_data_file_path("item.json")
        item_data = await self._load_json_file(item_file_path)
        
        if item_data and "data" in item_data:
            for item_id, raw_data in item_data["data"].items():
                try:
                    item = self._parse_item_data(item_id, raw_data)
                    items[item_id] = item
                except Exception as e:
                    logger.error(f"Error parsing item {item_id}: {e}")
        
        self._items_cache = items
        logger.info(f"Loaded {len(items)} items")
        return items
    
    def _parse_item_data(self, item_id: str, raw_data: Dict[str, Any]) -> Item:
        """Parse raw item data into Item model."""
        return Item(
            id=item_id,
            name=raw_data.get("name", ""),
            description=raw_data.get("description", ""),
            short_description=raw_data.get("plaintext", ""),
            stats=raw_data.get("stats", {}),
            gold=raw_data.get("gold", {}),
            tags=raw_data.get("tags", []),
            maps=raw_data.get("maps", {}),
            image=raw_data.get("image", {}),
            into=raw_data.get("into", []),
            from_items=raw_data.get("from", [])
        )
    
    async def load_runes(self, force_reload: bool = False) -> List[RuneTree]:
        """Load rune data."""
        if self._runes_cache is not None and not force_reload:
            return self._runes_cache
        
        logger.info("Loading rune data...")
        runes = []
        
        runes_file_path = self._get_data_file_path("runesReforged.json")
        runes_data = await self._load_json_file(runes_file_path)
        
        if runes_data:
            for tree_data in runes_data:
                try:
                    tree = self._parse_rune_tree_data(tree_data)
                    runes.append(tree)
                except Exception as e:
                    logger.error(f"Error parsing rune tree: {e}")
        
        self._runes_cache = runes
        logger.info(f"Loaded {len(runes)} rune trees")
        return runes
    
    def _parse_rune_tree_data(self, raw_data: Dict[str, Any]) -> RuneTree:
        """Parse raw rune tree data into RuneTree model."""
        # This would need to be implemented based on the actual rune data structure
        # The structure shown in the earlier data suggests a complex nested format
        slots = []
        for slot_data in raw_data.get("slots", []):
            slot_runes = []
            for rune_data in slot_data.get("runes", []):
                # Parse individual rune data here
                pass
            slots.append(slot_runes)
        
        return RuneTree(
            id=raw_data.get("id", 0),
            key=raw_data.get("key", ""),
            icon=raw_data.get("icon", ""),
            name=raw_data.get("name", ""),
            slots=slots
        )
    
    def _load_items_sync(self):
        """Load items synchronously."""
        try:
            item_file_path = self.data_path / "15.18.1" / "data" / self.language / "item.json"
            
            if item_file_path.exists():
                with open(item_file_path, 'r', encoding='utf-8') as f:
                    item_data = json.load(f)
                    
                items = {}
                if "data" in item_data:
                    # Load first 20 items for testing
                    item_keys = list(item_data["data"].keys())[:20]
                    for item_id in item_keys:
                        try:
                            raw_data = item_data["data"][item_id]
                            item = self._parse_item_data(item_id, raw_data)
                            items[item_id] = item
                        except Exception as e:
                            logger.warning(f"Error parsing item {item_id}: {e}")
                
                self._items_cache = items
                logger.info(f"Loaded {len(items)} items synchronously")
            else:
                self._items_cache = {}
                
        except Exception as e:
            logger.error(f"Error loading items: {e}")
            self._items_cache = {}
    
    def _load_runes_sync(self):
        """Load runes synchronously."""
        try:
            runes_file_path = self.data_path / "15.18.1" / "data" / self.language / "runesReforged.json"
            
            if runes_file_path.exists():
                with open(runes_file_path, 'r', encoding='utf-8') as f:
                    runes_data = json.load(f)
                    
                runes = []
                if isinstance(runes_data, list):
                    for rune_tree_data in runes_data:
                        try:
                            rune_tree = self._parse_rune_tree_data(rune_tree_data)
                            runes.append(rune_tree)
                        except Exception as e:
                            logger.warning(f"Error parsing rune tree: {e}")
                
                self._runes_cache = runes
                logger.info(f"Loaded {len(runes)} rune trees synchronously")
            else:
                self._runes_cache = []
                
        except Exception as e:
            logger.error(f"Error loading runes: {e}")
            self._runes_cache = []
    
    # Synchronous access methods
    def get_champions(self) -> Dict[str, Champion]:
        """Get all champions (synchronous)."""
        if self._champions_cache is None:
            return {}
        return self._champions_cache
    
    def get_items(self) -> Dict[str, Item]:
        """Get all items (synchronous)."""
        if self._items_cache is None:
            return {}
        return self._items_cache
    
    def get_runes(self) -> List[RuneTree]:
        """Get all rune trees (synchronous)."""
        if self._runes_cache is None:
            return []
        return self._runes_cache
    
    def search_champions_sync(self, query: str) -> List[Champion]:
        """Search champions synchronously."""
        champions = self.get_champions()
        query_lower = query.lower()
        results = []
        
        for champion in champions.values():
            if (query_lower in champion.name.lower() or 
                query_lower in champion.title.lower() or
                any(query_lower in tag.lower() for tag in champion.tags)):
                results.append(champion)
        
        return results
    
    def get_champion_by_name_sync(self, name: str) -> Optional[Champion]:
        """Get a champion by name synchronously."""
        champions = self.get_champions()
        name_lower = name.lower()
        
        for champion in champions.values():
            if champion.name.lower() == name_lower:
                return champion
        return None
    
    # Search and query methods
    async def search_champions(
        self, 
        query: str, 
        search_fields: List[str] = None
    ) -> List[Champion]:
        """
        Search champions by name, title, tags, or other fields.
        
        Args:
            query: Search query string
            search_fields: Fields to search in (default: name, title, tags)
            
        Returns:
            List of matching champions
        """
        if search_fields is None:
            search_fields = ["name", "title", "tags", "lore"]
        
        champions = await self.load_champions()
        query_lower = query.lower()
        results = []
        
        for champion in champions.values():
            # Search in specified fields
            if any(query_lower in str(getattr(champion, field, "")).lower() 
                   for field in search_fields):
                results.append(champion)
        
        return results
    
    async def get_champion_by_id(self, champion_id: str) -> Optional[Champion]:
        """Get a specific champion by ID."""
        champions = await self.load_champions()
        return champions.get(champion_id)
    
    async def get_champion_by_name(self, name: str) -> Optional[Champion]:
        """Get a champion by name (case-insensitive)."""
        champions = await self.load_champions()
        name_lower = name.lower()
        
        for champion in champions.values():
            if champion.name.lower() == name_lower:
                return champion
        return None
    
    async def get_champions_by_role(self, role: str) -> List[Champion]:
        """Get champions by their primary role/tag."""
        champions = await self.load_champions()
        role_lower = role.lower()
        results = []
        
        for champion in champions.values():
            if role_lower in [tag.lower() for tag in champion.tags]:
                results.append(champion)
        
        return results
    
    async def search_items(self, query: str) -> List[Item]:
        """Search items by name or description."""
        items = await self.load_items()
        query_lower = query.lower()
        results = []
        
        for item in items.values():
            if (query_lower in item.name.lower() or 
                query_lower in item.description.lower() or
                query_lower in item.short_description.lower()):
                results.append(item)
        
        return results
    
    async def get_item_by_id(self, item_id: str) -> Optional[Item]:
        """Get a specific item by ID."""
        items = await self.load_items()
        return items.get(item_id)
    
    async def get_items_by_tag(self, tag: str) -> List[Item]:
        """Get items by tag."""
        items = await self.load_items()
        results = []
        
        for item in items.values():
            if tag in item.tags:
                results.append(item)
        
        return results
    
    # Utility methods
    async def get_champion_counters(self, champion_id: str) -> Dict[str, Any]:
        """
        Get counter information for a champion.
        This could be extended to include statistical data or community data.
        """
        champion = await self.get_champion_by_id(champion_id)
        if not champion:
            return {}
        
        # This is a placeholder - you could integrate with external APIs
        # or maintain a database of counter relationships
        return {
            "champion": champion,
            "counters": [],  # Could be populated from external data
            "countered_by": [],  # Could be populated from external data
            "tips": champion.enemy_tips
        }
    
    async def get_champion_build_suggestions(self, champion_id: str) -> Dict[str, Any]:
        """Get suggested builds for a champion."""
        champion = await self.get_champion_by_id(champion_id)
        if not champion:
            return {}
        
        # This could be expanded to include actual build data
        # from community sources or statistical analysis
        return {
            "champion": champion,
            "builds": [],  # Could be populated from external data
            "core_items": [],  # Could be analyzed from champion stats/tags
            "situational_items": []
        }
    
    async def validate_data_integrity(self) -> Dict[str, Any]:
        """Validate the integrity of loaded data."""
        results = {
            "champions": {"loaded": 0, "errors": []},
            "items": {"loaded": 0, "errors": []},
            "runes": {"loaded": 0, "errors": []}
        }
        
        try:
            champions = await self.load_champions()
            results["champions"]["loaded"] = len(champions)
        except Exception as e:
            results["champions"]["errors"].append(str(e))
        
        try:
            items = await self.load_items()
            results["items"]["loaded"] = len(items)
        except Exception as e:
            results["items"]["errors"].append(str(e))
        
        try:
            runes = await self.load_runes()
            results["runes"]["loaded"] = len(runes)
        except Exception as e:
            results["runes"]["errors"].append(str(e))
        
        return results
    
    def __del__(self):
        """Cleanup when the object is destroyed."""
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=False)


# Global instance
_dragontail_manager: Optional[DragontailDataManager] = None


def get_dragontail_manager() -> DragontailDataManager:
    """Get the global Dragontail data manager instance."""
    global _dragontail_manager
    if _dragontail_manager is None:
        _dragontail_manager = DragontailDataManager()
    return _dragontail_manager


async def preload_data():
    """Preload all Dragontail data for faster access."""
    manager = get_dragontail_manager()
    await asyncio.gather(
        manager.load_champions(),
        manager.load_items(),
        manager.load_runes(),
        return_exceptions=True
    )


if __name__ == "__main__":
    async def main():
        # Test the data manager
        manager = DragontailDataManager()
        
        print("Testing Dragontail Data Manager...")
        
        # Test data validation
        validation = await manager.validate_data_integrity()
        print(f"Data validation: {validation}")
        
        # Test champion loading
        champions = await manager.load_champions()
        print(f"Loaded {len(champions)} champions")
        
        # Test champion search
        aatrox_results = await manager.search_champions("Aatrox")
        if aatrox_results:
            print(f"Found Aatrox: {aatrox_results[0].name} - {aatrox_results[0].title}")
        
        # Test items
        items = await manager.load_items()
        print(f"Loaded {len(items)} items")
        
        # Test runes
        runes = await manager.load_runes()
        print(f"Loaded {len(runes)} rune trees")
    
    asyncio.run(main())
